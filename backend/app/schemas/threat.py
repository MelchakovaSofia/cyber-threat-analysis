from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.log import NetworkLogOut


class ThreatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    log_id: int
    threat_type: str
    probability: float
    severity: str
    description: str
    created_at: datetime


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    threat_id: int
    message: str
    level: str
    status: str
    created_at: datetime


class ThreatDetail(BaseModel):
    threat: ThreatOut
    log: NetworkLogOut | None = None


class DashboardStats(BaseModel):
    analyzed_events: int
    detected_threats: int
    open_alerts: int
    risk_level: str
    top_ips: list[dict]
    activity_by_hour: list[dict]
    threats_by_type: list[dict]
