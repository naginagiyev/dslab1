from pydantic import BaseModel

class ConsultationReport(BaseModel):
    taskType: str | None
    targetCol: str | None
    desiredMetric: str | None
    minScoreRequirement: float | None
    explainableModel: bool
    saveModel: bool
    writeReport: bool
    deployment: bool

class TargetDetectionResult(BaseModel):
    targetCol: str
