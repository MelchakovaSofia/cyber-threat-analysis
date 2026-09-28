from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel

from app.auth.deps import get_current_user
from app.database.session import get_db
from app.models.alert import Alert
from app.schemas.threat import AlertOut
from app.utils.logger import get_logger

router = APIRouter(prefix="/alerts", tags=["alerts"], dependencies=[Depends(get_current_user)])
logger = get_logger(__name__)


class AlertUpdate(BaseModel):
    status: str


@router.get("", response_model=list[AlertOut])
def list_alerts(status: str | None = None, db: Session = Depends(get_db)):
    """List alerts with optional status filter."""
    try:
        logger.debug(f"Listing alerts with status filter: {status}")
        query = db.query(Alert)
        if status:
            query = query.filter(Alert.status == status)
        alerts = query.order_by(Alert.created_at.desc()).limit(500).all()
        logger.info(f"Retrieved {len(alerts)} alerts")
        return alerts
    except SQLAlchemyError as e:
        logger.error(f"Database error listing alerts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while listing alerts"
        )
    except Exception as e:
        logger.error(f"Unexpected error listing alerts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while listing alerts"
        )


@router.patch("/{alert_id}", response_model=AlertOut)
def update_status(alert_id: int, update: AlertUpdate, db: Session = Depends(get_db)):
    """Update alert status via request body."""
    try:
        logger.info(f"Updating alert {alert_id} status to {update.status}")
        alert = db.get(Alert, alert_id)
        if not alert:
            logger.warning(f"Alert not found: {alert_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Alert not found"
            )
        alert.status = update.status
        db.commit()
        db.refresh(alert)
        logger.info(f"Alert {alert_id} status updated successfully")
        return alert
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating alert {alert_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while updating alert"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error updating alert {alert_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating alert"
        )
