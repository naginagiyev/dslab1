import os
import json
from models.generation import GenerationModel
from path import promptsDir, configDir, agentWorkspaceDir

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

        query = (
            f"Dataset Path: {datasetPath}\n"
            f"Consultation:\n{json.dumps(consultation, indent=2)}"
        )

        plan = self.model.generate(query=query)

        os.makedirs(agentWorkspaceDir, exist_ok=True)
        planPath = os.path.join(agentWorkspaceDir, "plan.md")
        with open(planPath, "w", encoding="utf-8") as f:
            f.write(plan)

        return planPath