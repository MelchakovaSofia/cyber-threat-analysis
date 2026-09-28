from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TrainRequest(BaseModel):
    model_name: str = "random_forest"
    test_size: float = 0.2


class TrainResult(BaseModel):
    model_name: str
    version: str
    accuracy: float
    precision: float
    recall: float
    f1: float


class PredictRequest(BaseModel):
    log_ids: list[int] | None = None


class PredictionOut(BaseModel):
    log_id: int
    threat_type: str
    probability: float
    severity: str


class MLModelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: int
    model_name: str
    version: str
    accuracy: float
    is_active: bool
    created_at: datetime
