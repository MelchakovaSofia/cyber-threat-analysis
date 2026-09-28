"""Feature engineering for network logs."""
import pandas as pd

FEATURE_COLUMNS = [
    "port",
    "bytes_sent",
    "bytes_received",
    "hour",
    "protocol_code",
    "failed_login",
    "requests_per_ip",
]

PROTOCOL_CODES = {"TCP": 0, "UDP": 1, "ICMP": 2, "HTTP": 3, "HTTPS": 4}


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data["timestamp"] = pd.to_datetime(data["timestamp"], errors="coerce")
    data["hour"] = data["timestamp"].dt.hour.fillna(0).astype(int)
    data["protocol_code"] = (
        data["protocol"].str.upper().map(PROTOCOL_CODES).fillna(-1).astype(int)
    )
    data["failed_login"] = (
        data["status"].astype(str).str.lower().isin(["failed", "denied", "error"]).astype(int)
    )
    data["requests_per_ip"] = data.groupby("ip_address")["ip_address"].transform("count")
    for column in ("port", "bytes_sent", "bytes_received"):
        data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0)
    return data[FEATURE_COLUMNS]
