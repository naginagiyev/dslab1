import json
import pandas as pd
import onnxruntime as ort
from llms.codex import CodexModel
from tools.datareader import loadData
from tools.metrics import computeScore
from tools.coderunner import CodeRunner
from paths import configDir, modelsDir, promptsDir, sandboxDir, dataDir

class EvaluationAgent:
    def __init__(self):
        self.coder = CodexModel()
        self.runner = CodeRunner(fileName="train.py")

        planPath = promptsDir / "evaluationprompt.md"
        with open(planPath, 'r', encoding="utf-8") as plan:
            self.evaluationPrompt = plan.read()

        configurationPath = configDir / "configuration.json"
        with open(configurationPath, 'r', encoding="utf-8") as f:
            self.configuration = json.load(f)
        self.consultation = self.configuration

        self.metric = self.consultation.get('desiredMetric')
        self.target = self.consultation.get('targetCol')
        self.minMetric = self.consultation.get('minScoreRequirement')

        self.runtimeConfig = self.configuration

        self.trainDataPath = dataDir / self.runtimeConfig.get('trainFile')
        self.testDataPath = dataDir / self.runtimeConfig.get('testFile')
        self.modelPath = modelsDir / self.runtimeConfig.get('modelFile')

        constantsPath = configDir / "constants.json"
        with open(constantsPath, 'r', encoding="utf-8") as f:
            self.constants = json.load(f)
        
        self.tuningIterations = self.constants.get('tuningIterations')
        self.paramHistory = []
        self.previousScores = None

    def loadModel(self):
        self.session = ort.InferenceSession(modelsDir / "model.onnx")     

    def getPredictions(self, input: pd.DataFrame) -> pd.DataFrame:
        inputData = input.drop(columns=[self.target]).values.astype("float32")
        inputName = self.session.get_inputs()[0].name
        modelOutputs = self.session.run(None, {inputName: inputData})
        return pd.DataFrame(modelOutputs[0], columns=["prediction"])

    def evaluate(self, df: pd.DataFrame) -> float:
        trueValues = df[self.target]
        predictions = self.getPredictions(df)
        trainScore = computeScore(
            metric=str(self.metric).lower(),
            true=trueValues, pred=predictions["prediction"])
        return round(float(trainScore), 2)
    
    def readTrainCode(self) -> str:
        with open(sandboxDir / "train.py", "r") as code:
            code = code.read()

        marker = "# Generated code starts here"
        return code.split(marker, 1)[1]

    def act(self, paramChanges: dict) -> None:
        trainCode = self.readTrainCode()    

        tunedCode = self.coder.tuneParameters(
            currentCode=f"Training code:\n{trainCode}", 
            changes=f"Changes to make:\n{json.dumps(paramChanges, ensure_ascii=False)}"
            )
        
        self.runner.add(tunedCode)
        return self.runner.getOutput()   

    def tune(self):
        trainData = loadData(self.trainDataPath, self.target)
        testData = loadData(self.testDataPath, self.target)

        for iter in range(self.tuningIterations):
            self.loadModel()
            trainScore = self.evaluate(trainData)
            testScore = self.evaluate(testData)

            print(f"Iteration: {iter + 1}")
            print(f"Train Score: {trainScore}")
            print(f"Test Score: {testScore}")
            print()

            if trainScore >= self.minMetric and testScore >= self.minMetric:
                break

            if self.paramHistory and self.previousScores is not None:
                self.paramHistory[-1]["scoreBefore"] = self.previousScores
                self.paramHistory[-1]["scoreAfter"] = {"train": trainScore, "test": testScore}
                self.paramHistory[-1]["helped"] = (
                    trainScore >= self.previousScores["train"] and
                    testScore >= self.previousScores["test"]
                )

            if iter == 0:
                query = (
                    f"Train Code:\n{self.readTrainCode()}\n\n"
                    f"{self.metric.upper()} Train Score: {trainScore}\n"
                    f"{self.metric.upper()} Test Score: {testScore}\n"
                    f"Min {self.metric.upper()} Score To Hit: {self.minMetric}\n\n"
                )
            else:
                query = (
                    f"Parameter Change History:\n{json.dumps(self.paramHistory, ensure_ascii=False)}\n\n"
                    f"{self.metric.upper()} Train Score: {trainScore}\n"
                    f"{self.metric.upper()} Test Score: {testScore}\n"
                    f"Min {self.metric.upper()} Score To Hit: {self.minMetric}\n\n"
                )

            tuningResult = self.coder.suggestParameters(
                systemPrompt=self.evaluationPrompt,
                userContent=query
            )
            paramChanges = tuningResult
            self.paramHistory.append({"parameterChanges": paramChanges})
            self.previousScores = {"train": trainScore, "test": testScore}
            self.act(paramChanges)