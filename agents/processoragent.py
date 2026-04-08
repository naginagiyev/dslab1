import json
from cmdagent import CMDAgent
from paths import workspaceDir
from models.codex import CodexModel
from tools.notebook import Notebook
from memory.varregister import VariableRegistry

plan = workspaceDir / "plan.json"

class ProcessorAgent:
    def __init__(self):
        with open(plan, "r", encoding="utf-8") as f:
            self.plan = json.load(f)["preprocessing"]

        self.lastStepID = 0
        self.codex = CodexModel()
        self.cmdagent = CMDAgent()
        self.varRegistry = VariableRegistry()
        self.preprocessingNotebook = Notebook("preprocessing.ipynb")

    def act(self, code):
        return self.preprocessingNotebook.commitCodeCell(code)

processoragent = ProcessorAgent()
processoragent.preprocess()