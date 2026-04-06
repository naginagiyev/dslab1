from pydantic import BaseModel

class ConsultationReport(BaseModel):
    taskType: str | None = None
    targetCol: str | None = None
    desiredMetric: str | None = None
    minScoreRequirement: float | None = None
    explainableModel: bool | None = None
    writeReport: bool | None = None
    deployment: bool | None = None

class TargetDetectionResult(BaseModel):
    targetCol: str

class Plan(BaseModel):
    preprocessing: list[str]
    training: list[str]