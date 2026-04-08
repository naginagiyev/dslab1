import subprocess
from paths import promptsDir
from models.generation import GenerationModel

class CMDAgent:
    def __init__(self):
        self.model = GenerationModel(promptsDir / "cmdagent.md")

    def run(self, request: str) -> str:
        command = self.model.generate(query=request)
        try:
            proc = subprocess.run(
                f"conda run -n allinone {command}",
                shell=True,
                capture_output=True,
                text=True
            )
            output = (proc.stdout + proc.stderr).strip()
            return output if output else "The command executed successfully!"
        except Exception as e:
            return str(e)