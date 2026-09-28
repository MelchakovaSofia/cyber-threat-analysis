"""Import and clean CSV / JSON network logs."""
import io

import pandas as pd
from sqlalchemy.orm import Session

from app.models.network_log import NetworkLog

REQUIRED_COLUMNS = ["ip_address", "timestamp", "protocol", "port"]


def read_file(content: bytes, filename: str) -> pd.DataFrame:
    if filename.lower().endswith(".csv"):
        df = pd.read_csv(io.BytesIO(content))
    elif filename.lower().endswith(".json"):
        df = pd.read_json(io.BytesIO(content))
    else:
        raise ValueError("Only CSV and JSON files are supported")
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")
    return clean(df)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    data = df.drop_duplicates().copy()
    data["timestamp"] = pd.to_datetime(data["timestamp"], errors="coerce")
    data = data.dropna(subset=["ip_address", "timestamp"])
    data["port"] = pd.to_numeric(data["port"], errors="coerce").fillna(0).astype(int)
    for column in ("bytes_sent", "bytes_received"):
        if column not in data.columns:
            data[column] = 0
        data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0).astype(int)
    if "status" not in data.columns:
        data["status"] = "unknown"
    return data


def save_logs(db: Session, df: pd.DataFrame, batch_size: int = 1000) -> int:
    records = [
        NetworkLog(
            ip_address=str(row.ip_address),
            timestamp=row.timestamp.to_pydatetime(),
            protocol=str(row.protocol),
            port=int(row.port),
            bytes_sent=int(row.bytes_sent),
            bytes_received=int(row.bytes_received),
            status=str(row.status),
        )
        for row in df.itertuples()
    ]
    for start in range(0, len(records), batch_size):
        db.bulk_save_objects(records[start : start + batch_size])
        db.commit()
    return len(records)
