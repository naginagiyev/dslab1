import json
from pathlib import Path
from schemas import ConsultationReport
from llms.generation import GenerationModel
from paths import promptsDir, configDir, sandboxDir

class ConfigFiller:
    def __init__(self):
        self.model = GenerationModel(
            promptsDir / "configfiller.md",
            responseFormat=ConsultationReport,
        )

    def emptyConsultation(self) -> dict:
        return ConsultationReport().model_dump()

    def fill(self, datasetPath: str, consultation: dict | None = None, targetCol: str | None = None, includeConsultation: bool = True, save: bool = True,) -> dict:
        consultationPath = configDir / "consultation.json"
        if consultation is None and consultationPath.exists():
            with open(consultationPath, "r", encoding="utf-8") as f:
                consultation = json.load(f)

        if consultation is None:
            consultation = self.emptyConsultation()
        else:
            base = self.emptyConsultation()
            base.update(consultation)
            consultation = base

        stem = Path(datasetPath).stem
        edaPath = sandboxDir / f"{stem}eda.md"

        with open(edaPath, "r", encoding="utf-8") as f:
            edaReport = f.read()

        query = f"EDA Report:\n{edaReport}"
        if includeConsultation:
            query = (
                f"Consultation:\n{json.dumps(consultation, indent=2)}\n\n"
                f"{query}"
            )

        result = self.model.generate(query=query)
        filled = result.model_dump()

        for key, value in consultation.items():
            if value is not None:
                filled[key] = value

        if targetCol:
            filled["targetCol"] = targetCol

        filled["dataFile"] = Path(datasetPath).name

        if save:
            configDir.mkdir(parents=True, exist_ok=True)
            with open(consultationPath, "w", encoding="utf-8") as f:
                json.dump(filled, f, indent=4)

        return filled