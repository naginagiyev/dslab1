import subprocess
from paths import sandboxDir

class CodeRunner:
    def __init__(self, fileName: str):
        self.filePath = sandboxDir / fileName

    def add(self, script):
        header = "".join([
            "# initialize paths\n",
            "from paths import dataDir\n",
            "from paths import sandboxDir\n",
            "from paths import modelsDir\n\n",
            "# Generated code starts here\n"
            ])
        
        with open(self.filePath, "w") as f:
            f.write(header + script)

    def getOutput(self):
        result = subprocess.run(["python", self.filePath], capture_output=True, text=True)
        if result.returncode != 0:
            return {"operation": "error", "output": result.stderr}
        return {"operation": "success", "output": result.stdout.strip() if result.stdout else "No output"}