import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.config import settings
from app.database.session import Base, engine
from app.utils.logger import get_logger

logger = get_logger()

@asynccontextmanager
async def lifespan(_: FastAPI):
    # Use Alembic migrations for production set AUTO_MIGRATE=false
    # For development, set AUTO_MIGRATE=true to auto-create tables
    auto_migrate = os.getenv("AUTO_MIGRATE", "false").lower() == "true"
    if auto_migrate:
        logger.info("Auto-creating database tables (development mode)")
        Base.metadata.create_all(bind=engine)
    else:
        logger.info("Application started - use Alembic migrations for database setup")
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode")
    yield


app = FastAPI(
    title=settings.app_name, 
    version="0.1.0", 
    docs_url="/docs", 
    lifespan=lifespan,
    openapi_url="/openapi.json"
)

# Configure CORS with settings from config
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "error": str(exc) if settings.environment == "development" else "An unexpected error occurred"}
    )

app.include_router(api_router)


@app.get("/health", tags=["system"])
def health() -> dict:
    return {"status": "ok", "environment": settings.environment}
