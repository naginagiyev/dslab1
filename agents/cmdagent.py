import os
import subprocess
from path import promptsDir
from models.generation import GenerationModel

class CmdAgent:
    def __init__(self):
        self.model = GenerationModel(os.path.join(promptsDir, "cmdagent.md"))

    def run(self, request: str) -> str:
        command = self.model.generate(query=request)
        try:
            proc = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            output = (proc.stdout + proc.stderr).strip()
            return output if output else "The command executed successfully!"
        except Exception as e:
            return str(e)