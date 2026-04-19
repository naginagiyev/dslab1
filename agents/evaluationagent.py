import json
import numpy as np
import onnxruntime as ort
from llms.codex import CodexModel
from tools.datareader import loadData
from tools.metrics import computeScore
from tools.coderunner import CodeRunner
from paths import modelsDir, configDir, promptsDir, sandboxDir

class EvaluationAgent:
    def __init__(self):
        with open(configDir / "runtimeconfig.json", "r") as f:
            self.runtimeConfig = json.load(f)

        self.trainDF = loadData(self.runtimeConfig['trainFile'])
        self.testDF = loadData(self.runtimeConfig['testFile'])

        self.modelPath = self.runtimeConfig['modelFile']
        self.session = ort.InferenceSession(modelsDir / self.modelPath)

        self.coder = CodexModel()
        self.runner = CodeRunner(fileName="evaluation.py")

        with open(configDir / "consultation.json", 'r') as f:
            self.consultation = json.load(f)
        self.targetColumn = self.consultation["targetCol"]
        self.desiredMetric = self.consultation["desiredMetric"]
        self.minScoreRequirement = self.consultation["minScoreRequirement"]

        with open(configDir / "runtimeconfig.json", 'r') as f:
            self.runtimeConfig = json.load(f)

    def runInference(self, df):
        targetCol = self.runtimeConfig[self.targetColumn]
        X = df.drop(columns=[targetCol]).values.astype(np.float32)
        y = df[targetCol].values
        inputName = self.session.get_inputs()[0].name
        preds = self.session.run(None, {inputName: X})[0]
        return y, preds

    def getEvaluation(self):
        trainTrue, trainPreds = self.runInference(self.trainDF)
        testTrue, testPreds = self.runInference(self.testDF)

        trainScore = computeScore(trainTrue, trainPreds)
        testScore = computeScore(testTrue, testPreds)

        self.runtimeConfig[f"train{self.desiredMetric}Score"] = round(trainScore * 100, 2)
        self.runtimeConfig[f"test{self.desiredMetric}Score"] = round(testScore * 100, 2)

        with open(configDir / "runtimeconfig.json", "w") as f:
            json.dump(self.runtimeConfig, f, indent=4)

        return (
            f"Train {self.desiredMetric} score: {trainScore * 100:.2f}%\n"
            f"Test {self.desiredMetric} score: {testScore * 100:.2f}%"
        )