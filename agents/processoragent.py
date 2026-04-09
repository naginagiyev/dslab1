from cmdagent import CMDAgent
from paths import workspaceDir
from models.codex import CodexModel
from tools.coderunner import CodeRunner

class ProcessorAgent:
    def __init__(self):
        self.coder = CodexModel()
        self.runner = CodeRunner()
        planPath = workspaceDir / "processingplan.md"

        # load the plan prompt
        with open(planPath, 'r', encoding="utf-8") as plan:
            self.plan = plan.read()

    def act(self) -> str:
        generatedCode = self.coder.code(self.plan)
        self.runner.add(generatedCode)
        output = self.runner.getOutput()
        print(output)
        return output
    
processor = ProcessorAgent()
processor.act()