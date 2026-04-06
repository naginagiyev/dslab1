import sys
import json
from pathlib import Path
from path import workspaceDir
from models.codex import CodexModel
from tools.notebook import Notebook
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

plan = workspaceDir / "plan.json"

class ProcessorAgent:
    def __init__(self):
        with open(plan, "r", encoding="utf-8") as f:
            self.plan = json.load(f)["preprocessing"]
        
        self.preprocessingNotebook = Notebook("preprocessing.ipynb")
        self.codex = CodexModel()
        self.lastStepID = 0

    def act(self, query: str):
        generatedCode = self.codex.code(self.plan[self.lastStepID])
        self.preprocessingNotebook.appendCodeCell(generatedCode)
        self.preprocessingNotebook.save()

    def test(self) -> str:
        self.preprocessingNotebook.runLast()
        return self.preprocessingNotebook.getLastOutput()

    def reason(self) -> str:
        pass

processoragent = ProcessorAgent()
print(processoragent.seePlan())