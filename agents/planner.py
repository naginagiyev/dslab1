import os
import json
from pathlib import Path
from models.generation import GenerationModel
from path import promptsDir, configDir, workspaceDir

class Planner:
    def __init__(self):
        self.model = GenerationModel(
            os.path.join(promptsDir, "planner.md"),
            model="gpt-4.1",
        )

    def createPlan(self, datasetPath: str) -> str:
        consultationPath = os.path.join(configDir, "consultation.json")
        with open(consultationPath, "r", encoding="utf-8") as f:
            consultation = json.load(f)

        modelOptionsPath = os.path.join(configDir, "modeloptions.md")
        modelOptions = ""
        if os.path.exists(modelOptionsPath):
            with open(modelOptionsPath, "r", encoding="utf-8") as f:
                modelOptions = f.read()

        stem = Path(datasetPath).stem
        edaPath = os.path.join(workspaceDir, f"{stem}eda.md")
        edaReport = ""
        if os.path.exists(edaPath):
            with open(edaPath, "r", encoding="utf-8") as f:
                edaReport = f.read()

        query = (
            f"Dataset Path: {datasetPath}\n\n"
            f"Consultation:\n{json.dumps(consultation, indent=2)}\n\n"
            f"Model Options:\n{modelOptions}\n\n"
            f"EDA Report:\n{edaReport}"
        )

        plan = self.model.generate(query=query)

        os.makedirs(workspaceDir, exist_ok=True)
        planPath = os.path.join(workspaceDir, "plan.md")
        with open(planPath, "w", encoding="utf-8") as f:
            f.write(plan)

        return planPath