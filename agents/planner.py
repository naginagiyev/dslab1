import json
from pathlib import Path
from schemas import Plan
from llms.generation import GenerationModel
from paths import promptsDir, configDir, sandboxDir

class Planner:
    def __init__(self):
        self.model = GenerationModel(
            promptsDir / "planner.md",
            model="gpt-4.1",
            responseFormat=Plan,
        )

    def createPlan(self, datasetPath: str) -> tuple[Path, Path]:
        consultationPath = configDir / "consultation.json"
        with open(consultationPath, "r", encoding="utf-8") as f:
            consultation = json.load(f)

        modelOptionsPath = configDir / "modeloptions.md"
        modelOptions = ""
        if modelOptionsPath.exists():
            with open(modelOptionsPath, "r", encoding="utf-8") as f:
                modelOptions = f.read()

        stem = Path(datasetPath).stem
        edaPath = sandboxDir / f"{stem}eda.md"
        edaReport = ""
        if edaPath.exists():
            with open(edaPath, "r", encoding="utf-8") as f:
                edaReport = f.read()

        query = (
            f"Dataset Path: {datasetPath}\n\n"
            f"Consultation:\n{json.dumps(consultation, indent=2)}\n\n"
            f"Model Options:\n{modelOptions}\n\n"
            f"EDA Report:\n{edaReport}"
        )

        plan = self.model.generate(query=query)

        sandboxDir.mkdir(parents=True, exist_ok=True)

        preprocessingPath = sandboxDir / "processingplan.md"
        with open(preprocessingPath, "w", encoding="utf-8") as f:
            f.write(plan.preprocessing)

        trainingPath = sandboxDir / "trainingplan.md"
        with open(trainingPath, "w", encoding="utf-8") as f:
            f.write(plan.training)

        return preprocessingPath, trainingPath
