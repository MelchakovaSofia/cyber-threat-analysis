from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NetworkLogCreate(BaseModel):
    ip_address: str
    timestamp: datetime
    protocol: str
    port: int
    bytes_sent: int = 0
    bytes_received: int = 0
    status: str = "unknown"


class NetworkLogOut(NetworkLogCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
