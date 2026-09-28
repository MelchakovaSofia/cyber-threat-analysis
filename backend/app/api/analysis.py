from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.database.session import get_db
from app.models.ml_model import MLModel
from app.models.network_log import NetworkLog
from app.models.threat import Threat
from app.ml.predictor import load_model, predict
from app.schemas.log import NetworkLogOut
from app.schemas.threat import DashboardStats, ThreatDetail, ThreatOut
from app.services.alerts import create_alerts
from app.services.analysis import dashboard_stats, logs_dataframe, rule_based_findings, save_threats

router = APIRouter(prefix="/analysis", tags=["analysis"], dependencies=[Depends(get_current_user)])


@router.post("/run")
def run_analysis(db: Session = Depends(get_db)):
    df = logs_dataframe(db)
    if df.empty:
        raise HTTPException(status_code=400, detail="No logs to analyse")

    active = db.query(MLModel).filter(MLModel.is_active.is_(True)).first()
    if not active:
        raise HTTPException(status_code=400, detail="No active ML model, train one first")

    predictions = predict(load_model(active.path), df)
    threats = save_threats(db, predictions)
    alerts = create_alerts(db, threats)
    return {
        "analysed": len(df),
        "threats": len(threats),
        "alerts": len(alerts),
        "rule_based": rule_based_findings(df),
    }


@router.get("/results", response_model=list[ThreatOut])
def results(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return (
        db.query(Threat)
        .order_by(Threat.created_at.desc())
        .offset(skip)
        .limit(min(limit, 1000))
        .all()
    )


@router.get("/results/{threat_id}", response_model=ThreatDetail)
def result_detail(threat_id: int, db: Session = Depends(get_db)):
    threat = db.get(Threat, threat_id)
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    log = db.get(NetworkLog, threat.log_id)
    return ThreatDetail(
        threat=ThreatOut.model_validate(threat),
        log=NetworkLogOut.model_validate(log) if log else None,
    )


@router.get("/stats", response_model=DashboardStats)
def stats(db: Session = Depends(get_db)):
    return dashboard_stats(db)
