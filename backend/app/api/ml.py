from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, require_admin
from app.database.session import get_db
from app.models.ml_model import MLModel
from app.ml.predictor import load_model, predict
from app.ml.trainer import train_model
from app.schemas.ml import MLModelOut, PredictionOut, PredictRequest, TrainRequest, TrainResult
from app.services.analysis import logs_dataframe

router = APIRouter(prefix="/ml", tags=["machine-learning"])


@router.post("/train", response_model=TrainResult, dependencies=[Depends(require_admin)])
def train(payload: TrainRequest, db: Session = Depends(get_db)):
    df = logs_dataframe(db)
    if df.empty:
        raise HTTPException(status_code=400, detail="No training data")
    try:
        metrics = train_model(df, payload.model_name, payload.test_size)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    db.query(MLModel).update({MLModel.is_active: False})
    record = MLModel(
        model_name=metrics["model_name"],
        version=metrics["version"],
        accuracy=metrics["accuracy"],
        path=metrics["path"],
        is_active=True,
    )
    db.add(record)
    db.commit()
    return TrainResult(**{k: v for k, v in metrics.items() if k != "path"})


@router.get("/models", response_model=list[MLModelOut], dependencies=[Depends(get_current_user)])
def list_models(db: Session = Depends(get_db)):
    return db.query(MLModel).order_by(MLModel.created_at.desc()).all()


@router.post("/models/{model_id}/activate", dependencies=[Depends(require_admin)])
def activate(model_id: int, db: Session = Depends(get_db)):
    model = db.get(MLModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    db.query(MLModel).update({MLModel.is_active: False})
    model.is_active = True
    db.commit()
    return {"activated": model_id}


@router.post("/predict", response_model=list[PredictionOut], dependencies=[Depends(get_current_user)])
def run_prediction(payload: PredictRequest, db: Session = Depends(get_db)):
    active = db.query(MLModel).filter(MLModel.is_active.is_(True)).first()
    if not active:
        raise HTTPException(status_code=400, detail="No active model")
    df = logs_dataframe(db)
    if payload.log_ids:
        df = df[df["id"].isin(payload.log_ids)]
    if df.empty:
        raise HTTPException(status_code=400, detail="No logs found")
    return predict(load_model(active.path), df)
