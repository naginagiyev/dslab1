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
        output = self.preprocessingNotebook.commitCodeCell(generatedCode)
        return output

    def reason(self, output: str) -> str:
        reasoningOutput = self.codex.reason(output)
        return reasoningOutput

    def preprocess(self):
        for step in self.plan:
            output = self.act(step)
            if output.startswith("Error"):
                reasoningOutput = self.reason(output)

processoragent = ProcessorAgent()