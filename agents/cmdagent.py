import os
import subprocess
from path import promptsDir
from models.generation import GenerationModel

class CmdAgent:
    def __init__(self):
        self.model = GenerationModel(os.path.join(promptsDir, "cmdagent.md"))

    def run(self, request: str) -> dict:
        command = self.model.generate(query=request)
        try:
            proc = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            output = (proc.stdout + proc.stderr).strip()
            return {
                "result": "success" if proc.returncode == 0 else "error",
                "output": output if output else None
            }
        except Exception as e:
            return {
                "result": "error",
                "output": str(e)
            }