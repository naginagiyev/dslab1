import json
import pandas as pd
from pathlib import Path
from paths import promptsDir, configDir
from llms.generation import GenerationModel
from schemas import ConsultationReport, TargetDetectionResult

class Consultant:
    def __init__(self):
        self.history = []
        self.configurationPath = configDir / "configuration.json"
        self.metricsPath = configDir / "metrics.json"
        self.questionAgent = GenerationModel(promptsDir / "consultant.md")
        self.reportAgent = GenerationModel(
            promptsDir / "consultantassistant.md",
            responseFormat=ConsultationReport
        )
        self.targetAgent = GenerationModel(
            promptsDir / "targetdetector.md",
            responseFormat=TargetDetectionResult
        )
        self.allowedMetrics = self.loadAllowedMetrics()

    def loadAllowedMetrics(self) -> list[str]:
        with open(self.metricsPath, "r", encoding="utf-8") as f:
            metricsByGroup = json.load(f)
        metrics = []
        for groupMetrics in metricsByGroup.values():
            for metric in groupMetrics:
                if metric not in metrics:
                    metrics.append(metric)
        return metrics

    def normalizeMetric(self, metric: str | None) -> str | None:
        if metric is None:
            return None
        normalizedMap = {item.lower(): item for item in self.allowedMetrics}
        return normalizedMap.get(str(metric).strip().lower())

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
        metricsText = ", ".join(self.allowedMetrics)
        query = (
            f"{conversation}\n\n"
            f"Allowed Metrics (use exact naming): {metricsText}\n"
            "desiredMetric must be exactly one value from Allowed Metrics or null."
        )
        report = self.reportAgent.generate(query=query)
        report.desiredMetric = self.normalizeMetric(report.desiredMetric)
        configDir.mkdir(parents=True, exist_ok=True)
        configuration = {}
        if self.configurationPath.exists():
            with open(self.configurationPath, "r", encoding="utf-8") as f:
                configuration = json.load(f)
        configuration.update(report.model_dump())
        with open(self.configurationPath, "w", encoding="utf-8") as f:
            json.dump(configuration, f, indent=4)
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
        report.dataFile = Path(datasetPath).name
        if save:
            configDir.mkdir(parents=True, exist_ok=True)
            configuration = {}
            if self.configurationPath.exists():
                with open(self.configurationPath, "r", encoding="utf-8") as f:
                    configuration = json.load(f)
            configuration.update(report.model_dump())
            with open(self.configurationPath, "w", encoding="utf-8") as f:
                json.dump(configuration, f, indent=4)
        return result.targetCol