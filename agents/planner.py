import json
from pathlib import Path
from llms.generation import GenerationModel
from paths import promptsDir, configDir, sandboxDir

class Planner:
    def __init__(self):
        self.configurationPath = configDir / "configuration.json"
        self.processingModel = GenerationModel(
            promptsDir / "processingplanprompt.md",
            model="gpt-4.1",
        )
        self.trainingModel = GenerationModel(
            promptsDir / "trainplanprompt.md",
            model="gpt-4.1",
        )

    def _loadConsultation(self):
        with open(self.configurationPath, "r", encoding="utf-8") as f:
            self.consultation = json.load(f)

    def _loadRuntimeConfig(self):
        with open(self.configurationPath, "r", encoding="utf-8") as f:
            self.runtimeConfig = json.load(f)

    def _loadModelOptions(self):
        modelOptionsPath = configDir / "modeloptions.md"
        with open(modelOptionsPath, "r", encoding="utf-8") as f:
            self.modelOptions = f.read()

    def _loadEdaReport(self):
        stem = Path(self.consultation["dataFile"]).stem
        edaPath = sandboxDir / f"{stem}eda.md"
        with open(edaPath, "r", encoding="utf-8") as f:
            self.edaReport = f.read()

    def _refreshContext(self):
        self._loadConsultation()
        self._loadRuntimeConfig()
        self._loadModelOptions()
        self._loadEdaReport()
        sandboxDir.mkdir(parents=True, exist_ok=True)

    def createPreProcessingPlan(self):
        self._refreshContext()
        query = (
            f"Dataset Path: {self.consultation['dataFile']}\n"
            f"Task Type: {self.consultation['taskType']}\n"
            f"Target Column: {self.consultation['targetCol']}\n\n"
            f"EDA Report:\n{self.edaReport}\n\n"
        )

        processingPlan = self.processingModel.generate(query=query)
        
        preprocessingPlanPath = sandboxDir / "processingplan.md"
        with open(preprocessingPlanPath, "w", encoding="utf-8") as f:
            f.write(processingPlan)

        return preprocessingPlanPath

    def createTrainingPlan(self):
        self._refreshContext()
        query = (
            f"Train Data Path: {self.runtimeConfig['trainFile']}\n"
            f"Validation Data Path: {self.runtimeConfig.get('valFile', 'No Validation Data')}\n"
            f"Task Type: {self.consultation['taskType']}\n"
            f"Target Column: {self.consultation['targetCol']}\n\n"
            f"Explainable Model: {self.runtimeConfig.get('explainableModel')}\n"
            f"Model Options:\n{self.modelOptions}\n\n"
        )

        trainPlan = self.trainingModel.generate(query=query)
        
        trainPlanPath = sandboxDir / "trainingplan.md"
        with open(trainPlanPath, "w", encoding="utf-8") as f:
            f.write(trainPlan)

        return trainPlanPath
    
    def createPlan(self) -> tuple[Path, Path]:
        return self.createPreProcessingPlan(), self.createTrainingPlan()