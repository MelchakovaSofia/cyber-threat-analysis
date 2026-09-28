from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class NetworkLog(Base):
    __tablename__ = "network_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    ip_address: Mapped[str] = mapped_column(String(45), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    protocol: Mapped[str] = mapped_column(String(16))
    port: Mapped[int] = mapped_column(Integer)
    bytes_sent: Mapped[int] = mapped_column(BigInteger, default=0)
    bytes_received: Mapped[int] = mapped_column(BigInteger, default=0)
    status: Mapped[str] = mapped_column(String(32), default="unknown")
