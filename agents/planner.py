import json
from pathlib import Path
from schemas import Plan
from models.generation import GenerationModel
from path import promptsDir, configDir, workspaceDir

class Planner:
    def __init__(self):
        self.model = GenerationModel(
            promptsDir / "planner.md",
            model="gpt-4.1",
            responseFormat=Plan,
        )

    def createPlan(self, datasetPath: str) -> Path:
        consultationPath = configDir / "consultation.json"
        with open(consultationPath, "r", encoding="utf-8") as f:
            consultation = json.load(f)

        modelOptionsPath = configDir / "modeloptions.md"
        modelOptions = ""
        if modelOptionsPath.exists():
            with open(modelOptionsPath, "r", encoding="utf-8") as f:
                modelOptions = f.read()

        stem = Path(datasetPath).stem
        edaPath = workspaceDir / f"{stem}eda.md"
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

        workspaceDir.mkdir(parents=True, exist_ok=True)
        planPath = workspaceDir / "plan.json"
        with open(planPath, "w", encoding="utf-8") as f:
            json.dump(plan.model_dump(), f, indent=2, ensure_ascii=False)

        return planPath