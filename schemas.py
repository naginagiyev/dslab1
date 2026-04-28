from typing import Literal
from pydantic import BaseModel, RootModel

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

class ReasoningResult(BaseModel):
    condition: Literal["fail", "pass"]
    prompt: str | None = None

class ParameterChange(BaseModel):
    current: float | int | str | None = None
    new: float | int | str | None = None

class TuningResult(RootModel[dict[str, ParameterChange]]):
    pass