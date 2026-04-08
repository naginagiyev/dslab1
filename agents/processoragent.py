import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cmdagent import CMDAgent
from path import workspaceDir
from models.codex import CodexModel
from tools.notebook import Notebook

plan = workspaceDir / "plan.json"

class ProcessorAgent:
    def __init__(self):
        with open(plan, "r", encoding="utf-8") as f:
            self.plan = json.load(f)["preprocessing"]
        
        self.preprocessingNotebook = Notebook("preprocessing.ipynb")
        self.cmdagent = CMDAgent()
        self.codex = CodexModel()
        self.lastStepID = 0

    def act(self, query: str):
        generatedCode = self.codex.code(query)
        output = self.preprocessingNotebook.commitCodeCell(generatedCode)
        return output

    def reason(self, output: str) -> str:
        reasoningOutput = self.codex.reason(output)
        return reasoningOutput

    def preprocess(self):
        while self.lastStepID < len(self.plan):
            output = self.act(self.plan[self.lastStepID])
            if output.startswith("Error"):
                reasoningOutput = self.reason(output)
                if reasoningOutput.tool == "command":
                    self.cmdagent.run(reasoningOutput.prompt)
                elif reasoningOutput.tool == "code":
                    output = self.act(reasoningOutput.prompt)
                    if not output.startswith("Error"):
                        self.lastStepID += 1
            else:
                self.lastStepID += 1

processoragent = ProcessorAgent()
processoragent.preprocess()