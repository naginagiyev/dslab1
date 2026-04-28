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
        self.metricsPath = configDir / "metrics.json"
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

    def emptyConsultation(self) -> dict:
        return ConsultationReport().model_dump()

    def fill(self, datasetPath: str, consultation: dict | None = None, targetCol: str | None = None, includeConsultation: bool = True, save: bool = True,) -> dict:
        configurationPath = configDir / "configuration.json"
        if consultation is None and configurationPath.exists():
            with open(configurationPath, "r", encoding="utf-8") as f:
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

        metricsText = ", ".join(self.allowedMetrics)
        query = (
            f"Allowed Metrics (use exact naming): {metricsText}\n"
            "desiredMetric must be exactly one value from Allowed Metrics or null.\n\n"
            f"EDA Report:\n{edaReport}"
        )
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

        if consultation.get("desiredMetric") is not None:
            filled["desiredMetric"] = self.normalizeMetric(consultation.get("desiredMetric"))
        else:
            filled["desiredMetric"] = self.normalizeMetric(filled.get("desiredMetric"))

        filled["dataFile"] = Path(datasetPath).name

        if save:
            configDir.mkdir(parents=True, exist_ok=True)
            with open(configurationPath, "w", encoding="utf-8") as f:
                json.dump(filled, f, indent=4)

        return filled