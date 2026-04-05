import json
from pathlib import Path
from schemas import ConsultationReport
from models.generation import GenerationModel
from path import promptsDir, configDir, workspaceDir


class ConfigFiller:
    def __init__(self):
        self.model = GenerationModel(
            promptsDir / "configfiller.md",
            responseFormat=ConsultationReport,
        )

    def fill(self, datasetPath: str):
        consultationPath = configDir / "consultation.json"
        with open(consultationPath, "r", encoding="utf-8") as f:
            consultation = json.load(f)

        stem = Path(datasetPath).stem
        edaPath = workspaceDir / f"{stem}eda.md"
        edaReport = ""
        if edaPath.exists():
            with open(edaPath, "r", encoding="utf-8") as f:
                edaReport = f.read()

        query = (
            f"Consultation:\n{json.dumps(consultation, indent=2)}\n\n"
            f"EDA Report:\n{edaReport}"
        )

        result = self.model.generate(query=query)
        with open(consultationPath, "w", encoding="utf-8") as f:
            json.dump(result.model_dump(), f, indent=4)