import os
import json
from llms.codex import CodexModel
from tools.coderunner import CodeRunner
from paths import configDir, modelsDir, promptsDir, sandboxDir

class TrainAgent:
    def __init__(self):
        self.coder = CodexModel()
        self.runner = CodeRunner(fileName="train.py")
        self.lastReasoning = None
        self.lastGeneratedCode = None
        self.configurationPath = configDir / "configuration.json"
        planPath = sandboxDir / "trainingplan.md"

        with open(planPath, 'r', encoding="utf-8") as plan:
            self.plan = plan.read()
        with open(self.configurationPath, 'r', encoding="utf-8") as f:
            self.runtimeConfig = json.load(f)
        self.consultation = self.runtimeConfig
        with open(promptsDir / "trainreasoningprompt.md", "r", encoding="utf-8") as f:
            self.reasoningPrompt = f.read()

    def train(self):
        output = self.act()
        while True:
            reasoning = self.reason(output=output)
            if reasoning.condition == "pass":
                self.saveModelPath()
                break
            output = self.fixCode()

    def act(self) -> str:
        trainFile = self.runtimeConfig['trainFile']
        valFile = self.runtimeConfig.get('valFile')
        header = f"Train Data Path: {trainFile}\n"
        if valFile:
            header += f"Validation Data Path: {valFile}\n"
        header += "\n"
        generatedCode = self.coder.code(header + self.plan)
        self.lastGeneratedCode = generatedCode
        self.runner.add(generatedCode)
        return self.runner.getOutput()

    def fixCode(self) -> str:
        fixedCode = self.coder.fixCode(self.lastGeneratedCode, self.lastReasoning)
        self.lastGeneratedCode = fixedCode
        self.runner.add(fixedCode)
        return self.runner.getOutput()

    def reason(self, output: str) -> dict:
        generatedReasoning = self.coder.reason(self.reasoningPrompt, output["output"])
        self.lastReasoning = generatedReasoning.prompt
        return generatedReasoning

    def saveModelPath(self):
        modelsDir.mkdir(parents=True, exist_ok=True)
        modelFile = self.runtimeConfig.get('modelFile', 'model.pkl')
        self.runtimeConfig['modelFile'] = os.path.basename(modelFile)
        with open(self.configurationPath, 'w', encoding="utf-8") as f:
            json.dump(self.runtimeConfig, f, indent=2)

if __name__ == "__main__":
    trainer = TrainAgent()
    trainer.train()