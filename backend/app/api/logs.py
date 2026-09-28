from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.auth.deps import get_current_user
from app.database.session import get_db
from app.models.network_log import NetworkLog
from app.schemas.log import NetworkLogCreate, NetworkLogOut
from app.services.log_import import read_file, save_logs
from app.utils.logger import get_logger

router = APIRouter(prefix="/logs", tags=["logs"], dependencies=[Depends(get_current_user)])
logger = get_logger(__name__)


@router.get("", response_model=list[NetworkLogOut])
def list_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List network logs with pagination."""
    try:
        logger.debug(f"Listing logs with skip={skip}, limit={limit}")
        logs = db.query(NetworkLog).offset(skip).limit(min(limit, 1000)).all()
        logger.info(f"Retrieved {len(logs)} logs")
        return logs
    except SQLAlchemyError as e:
        logger.error(f"Database error listing logs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while listing logs"
        )
    except Exception as e:
        logger.error(f"Unexpected error listing logs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while listing logs"
        )


@router.get("/{log_id}", response_model=NetworkLogOut)
def get_log(log_id: int, db: Session = Depends(get_db)):
    """Get a specific network log by ID."""
    try:
        logger.debug(f"Fetching log with id={log_id}")
        log = db.get(NetworkLog, log_id)
        if not log:
            logger.warning(f"Log not found: id={log_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Log not found"
            )
        return log
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching log {log_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching log"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching log {log_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching log"
        )


@router.post("", response_model=NetworkLogOut, status_code=201)
def add_log(payload: NetworkLogCreate, db: Session = Depends(get_db)):
    """Add a new network log."""
    try:
        logger.info(f"Adding new log for IP: {payload.ip_address}")
        log = NetworkLog(**payload.model_dump())
        db.add(log)
        db.commit()
        db.refresh(log)
        logger.info(f"Successfully added log with id={log.id}")
        return log
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error adding log: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while adding log"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error adding log: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while adding log"
        )


@router.post("/import")
async def import_logs(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import network logs from CSV or JSON file."""
    try:
        logger.info(f"Importing logs from file: {file.filename}")
        content = await file.read()
        df = read_file(content, file.filename)
        imported_count = save_logs(db, df)
        logger.info(f"Successfully imported {imported_count} logs from {file.filename}")
        return {"imported": imported_count}
    except ValueError as exc:
        logger.warning(f"File import validation failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(exc)
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during import: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred during import"
        )
    except Exception as e:
        logger.error(f"Unexpected error during import: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during import"
        )


@router.delete("/{log_id}", status_code=204)
def delete_log(log_id: int, db: Session = Depends(get_db)):
    """Delete a network log by ID."""
    try:
        logger.info(f"Deleting log with id={log_id}")
        log = db.get(NetworkLog, log_id)
        if not log:
            logger.warning(f"Cannot delete log, not found: id={log_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Log not found"
            )
        db.delete(log)
        db.commit()
        logger.info(f"Successfully deleted log with id={log_id}")
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting log {log_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while deleting log"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error deleting log {log_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting log"
        )
