import json
from llms.codex import CodexModel
from tools.coderunner import CodeRunner
from paths import configDir, promptsDir, workspaceDir

class TrainAgent:
    def __init__(self):
        self.coder = CodexModel()
        self.runner = CodeRunner(fileName="train.py")
        self.lastReasoning = None
        self.lastGeneratedCode = None
        self.consultationPath = configDir / "consultation.json"
        planPath = workspaceDir / "trainingplan.md"

        with open(planPath, 'r', encoding="utf-8") as plan:
            self.plan = plan.read()
        with open(self.consultationPath, 'r', encoding="utf-8") as consultationFile:
            self.consultation = json.load(consultationFile)
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
        header = f"Dataset Path: {self.consultation['processedDataFile']}\n\n"
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
        self.consultation['modelFile'] = "model.pkl"
        with open(self.consultationPath, 'w', encoding="utf-8") as f:
            json.dump(self.consultation, f, indent=2)

if __name__ == "__main__":
    trainer = TrainAgent()
    trainer.train()
