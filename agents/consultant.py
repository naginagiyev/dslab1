import json
import pandas as pd
from paths import promptsDir, configDir
from models.generation import GenerationModel
from schemas import ConsultationReport, TargetDetectionResult

class Consultant:
    def __init__(self):
        self.history = []
        self.questionAgent = GenerationModel(promptsDir / "consultant.md")
        self.reportAgent = GenerationModel(
            promptsDir / "consultantassistant.md",
            responseFormat=ConsultationReport
        )
        self.targetAgent = GenerationModel(
            promptsDir / "targetdetector.md",
            responseFormat=TargetDetectionResult
        )

    def nextQuestion(self, userInput: str):
        response = self.questionAgent.generate(query=userInput, history=self.history)
        if response.strip() == "[OFFTOPIC]":
            prev = next((h["assistant"] for h in reversed(self.history) if h["assistant"].strip() not in ("[DONE]", "[OFFTOPIC]")), "Should the model be explainable?")
            return f"I think the query you have written is not related to our topic. So, I am asking again {prev}"
        self.history.append({"user": userInput, "assistant": response})
        if response.strip() == "[DONE]":
            return None
        return response

    def saveReport(self):
        conversation = "\n".join(
            f"User: {h['user']}\nAssistant: {h['assistant']}"
            for h in self.history
        )
        report = self.reportAgent.generate(query=conversation)
        configDir.mkdir(parents=True, exist_ok=True)
        with open(configDir / "consultation.json", "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, indent=4)
        return report

    def detectTarget(self, datasetPath: str, report: ConsultationReport | None = None, save: bool = True) -> str:
        if report is None:
            report = ConsultationReport()
        df = pd.read_csv(datasetPath)
        col_samples = {col: df[col].dropna().unique()[:2].tolist() for col in df.columns}
        query = json.dumps({
            "taskType": report.taskType,
            "desiredMetric": report.desiredMetric,
            "columns": col_samples,
        }, default=str)
        result = self.targetAgent.generate(query=query)
        report.targetCol = result.targetCol
        if save:
            configDir.mkdir(parents=True, exist_ok=True)
            with open(configDir / "consultation.json", "w", encoding="utf-8") as f:
                json.dump(report.model_dump(), f, indent=4)
        return result.targetCol