import json
from pathlib import Path
from paths import sandboxDir, configDir, promptsDir
from llms.generation import GenerationModel

class ReportWriter:
    def __init__(self):
        configurationPath = configDir / "configuration.json"
        with open(configurationPath, "r", encoding="utf-8") as f:
            configuration = json.load(f)

        self.taskType = configuration["taskType"]
        self.dataFile = configuration["dataFile"]
        self.deployment = configuration.get("deployment", False)
        self.endPoint = configuration.get("endPoint", None)

        stem = Path(self.dataFile).stem
        edaReportPath = sandboxDir / f"{stem}eda.md"
        preprocessingPath = sandboxDir / "processing.py"

        with open(edaReportPath, "r", encoding="utf-8") as f:
            edaReport = f.read()
        with open(preprocessingPath, "r", encoding="utf-8") as f:
            preprocessingCode = f.read()

        with open(sandboxDir / "train.py", "r", encoding="utf-8") as f:
            trainCode = f.read()

        with open(sandboxDir / "tuning.json", "r", encoding="utf-8") as f:
            tuningData = json.load(f)

        self.files = {
            "preprocessing": f"EDA Report:\n{edaReport}\n\nPreprocessing Code:\n{preprocessingCode}",
            "train": trainCode,
            "evaluation": json.dumps(tuningData, indent=2),
        }

        self.sectionMap = {
            "preprocessing": "## Data & Preprocessing",
            "train": "## Training",
            "evaluation": "## Evaluation",
        }

        self.model = GenerationModel(promptsDir / "reportprompt.md")

    def createStructure(self):
        title = f"# Documentation - {self.taskType.replace('-', ' ').title()} for {self.dataFile.split('.')[0]}"
        docPath = sandboxDir / "documentation.md"
        with open(docPath, "w", encoding="utf-8") as f:
            f.write(f"{title}\n\n")
            for heading in self.sectionMap.values():
                f.write(f"{heading}\n\n")
            if self.deployment:
                f.write("## Deployment\n\n")

    def writeReport(self):
        self.createStructure()
        docPath = sandboxDir / "documentation.md"
        with open(docPath, "r", encoding="utf-8") as f:
            content = f.read()

        for key, heading in self.sectionMap.items():
            response = self.model.generate(self.files[key])
            content = content.replace(f"{heading}\n\n", f"{heading}\n\n{response}\n\n", 1)

        if self.deployment and self.endPoint:
            deploymentContent = f"The model is deployed and accessible at the following endpoint:\n\n**API URL:** {self.endPoint}\n\n"
            content = content.replace("## Deployment\n\n", f"## Deployment\n\n{deploymentContent}", 1)

        with open(docPath, "w", encoding="utf-8") as f:
            f.write(content)