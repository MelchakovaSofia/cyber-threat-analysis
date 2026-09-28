"""Network activity analysis and threat persistence."""
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.network_log import NetworkLog
from app.models.threat import Threat

FAILED_LOGIN_LIMIT = 5
REQUEST_LIMIT_PER_IP = 500


def logs_dataframe(db: Session, limit: int = 100_000) -> pd.DataFrame:
    rows = db.query(NetworkLog).limit(limit).all()
    return pd.DataFrame(
        [
            {
                "id": row.id,
                "ip_address": row.ip_address,
                "timestamp": row.timestamp,
                "protocol": row.protocol,
                "port": row.port,
                "bytes_sent": row.bytes_sent,
                "bytes_received": row.bytes_received,
                "status": row.status,
            }
            for row in rows
        ]
    )


def rule_based_findings(df: pd.DataFrame) -> list[dict]:
    """Simple heuristics used alongside the ML model."""
    if df.empty:
        return []
    findings = []
    failed = df[df["status"].astype(str).str.lower().isin(["failed", "denied"])]
    for ip, count in failed.groupby("ip_address").size().items():
        if count >= FAILED_LOGIN_LIMIT:
            findings.append(
                {
                    "ip_address": ip,
                    "threat_type": "brute_force",
                    "description": f"{count} failed login attempts from {ip}",
                    "severity": "high",
                }
            )
    for ip, count in df.groupby("ip_address").size().items():
        if count >= REQUEST_LIMIT_PER_IP:
            findings.append(
                {
                    "ip_address": ip,
                    "threat_type": "flood",
                    "description": f"{count} requests from {ip}",
                    "severity": "medium",
                }
            )
    return findings


def save_threats(db: Session, predictions: list[dict], threshold: float = 0.5) -> list[Threat]:
    threats = []
    for item in predictions:
        if item["probability"] < threshold:
            continue
        threat = Threat(
            log_id=item["log_id"],
            threat_type=item["threat_type"],
            probability=item["probability"],
            severity=item["severity"],
            description=f"Detected by ML model, probability {item['probability']}",
        )
        db.add(threat)
        threats.append(threat)
    db.commit()
    return threats


def dashboard_stats(db: Session) -> dict:
    analyzed = db.query(func.count(NetworkLog.id)).scalar() or 0
    detected = db.query(func.count(Threat.id)).scalar() or 0
    open_alerts = db.query(func.count(Alert.id)).filter(Alert.status == "new").scalar() or 0

    top_ips = [
        {"ip_address": ip, "count": count}
        for ip, count in db.query(NetworkLog.ip_address, func.count(NetworkLog.id))
        .group_by(NetworkLog.ip_address)
        .order_by(func.count(NetworkLog.id).desc())
        .limit(10)
        .all()
    ]
    activity = [
        {"hour": int(hour), "count": count}
        for hour, count in db.query(
            func.extract("hour", NetworkLog.timestamp), func.count(NetworkLog.id)
        )
        .group_by(func.extract("hour", NetworkLog.timestamp))
        .all()
    ]
    by_type = [
        {"threat_type": threat_type, "count": count}
        for threat_type, count in db.query(Threat.threat_type, func.count(Threat.id))
        .group_by(Threat.threat_type)
        .all()
    ]
    ratio = (detected / analyzed) if analyzed else 0
    risk = "high" if ratio > 0.2 else "medium" if ratio > 0.05 else "low"
    return {
        "analyzed_events": analyzed,
        "detected_threats": detected,
        "open_alerts": open_alerts,
        "risk_level": risk,
        "top_ips": top_ips,
        "activity_by_hour": activity,
        "threats_by_type": by_type,
    }
