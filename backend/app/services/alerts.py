"""Alert generation from detected threats."""
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.threat import Threat

LEVEL_BY_SEVERITY = {"critical": "critical", "high": "warning", "medium": "warning", "low": "info"}


def create_alerts(db: Session, threats: list[Threat]) -> list[Alert]:
    alerts = []
    for threat in threats:
        if threat.severity not in ("high", "critical"):
            continue
        alert = Alert(
            threat_id=threat.id,
            message=(
                f"Threat '{threat.threat_type}' detected (log #{threat.log_id}), "
                f"probability {threat.probability}"
            ),
            level=LEVEL_BY_SEVERITY.get(threat.severity, "info"),
            status="new",
        )
        db.add(alert)
        alerts.append(alert)
    db.commit()
    return alerts
