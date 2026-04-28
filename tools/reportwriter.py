import json
from pathlib import Path
from paths import sandboxDir, configDir

class ReportWriter:
    def __init__(self):
        configurationPath = configDir / "configuration.json"
        with open(configurationPath, "r", encoding="utf-8") as f:
            configuration = json.load(f)

        stem = Path(configuration["dataFile"]).stem
        edaReportPath = sandboxDir / f"{stem}eda.md"
        preprocessingPath = sandboxDir / "preprocessing.py"

        with open(edaReportPath, "r", encoding="utf-8") as f:
            edaReport = f.read()
        with open(preprocessingPath, "r", encoding="utf-8") as f:
            preprocessingCode = f.read()

        with open(sandboxDir / "train.py", "r", encoding="utf-8") as f:
            trainCode = f.read()

        with open(sandboxDir / "tuning.json", "r", encoding="utf-8") as f:
            tuningData = json.load(f)

        self.files = {
            "configuration": configuration,
            "preprocessing": f"EDA Report:\n{edaReport}\n\nPreprocessing Code:\n{preprocessingCode}",
            "train": trainCode,
            "evaluation": tuningData,
        }

writer = ReportWriter()
print(writer.configuration)