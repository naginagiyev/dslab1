import json
from models.codex import CodexModel
from tools.coderunner import CodeRunner
from paths import workspaceDir, configDir

class ProcessorAgent:
    def __init__(self):
        self.coder = CodexModel()
        self.runner = CodeRunner()
        self.consultationPath = configDir / "consultation.json"
        planPath = workspaceDir / "processingplan.md"

        # load the plan prompt
        with open(planPath, 'r', encoding="utf-8") as plan:
            self.plan = plan.read()

        # load consultation file
        with open(self.consultationPath, 'r', encoding="utf-8") as consultationFile:
            self.consultation = json.load(consultationFile)

    def act(self) -> str:
        header = f"Dataset Path: {self.consultation['dataFile']}\n\n"
        generatedCode = self.coder.code(header + self.plan)
        self.runner.add(generatedCode)
        output = self.runner.getOutput()
        print(output)
        return output
    
processor = ProcessorAgent()
processor.act()