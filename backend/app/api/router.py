from fastapi import APIRouter

from app.api import alerts, analysis, auth, logs, ml

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(logs.router)
api_router.include_router(analysis.router)
api_router.include_router(ml.router)
api_router.include_router(alerts.router)
