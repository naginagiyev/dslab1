from typing import Literal
from pydantic import BaseModel

class ConsultationReport(BaseModel):
    dataFile: str | None = None
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
    preprocessing: str
    training: str

class ReasoningResult(BaseModel):
    condition: Literal["fail", "pass"]
    prompt: str | None = None