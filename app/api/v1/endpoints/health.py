import time
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.schemas.base import HealthResponse, ReadinessCheckResponse
from app.config import settings
from app.logging_config import get_logger

logger = get_logger("api.health")
router = APIRouter()

# Track startup time for uptime calculation
startup_time = time.time()


@router.get("/", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint that verifies system components.

    Returns:
        - API status
        - Current timestamp
        - Version information
        - Uptime in seconds
        - Database connectivity
    """
    try:
        # Test database connectivity
        db.execute(text("SELECT 1"))

        current_time = datetime.now()
        uptime = time.time() - startup_time

        logger.info("Health check successful", extra={
            "uptime_seconds": uptime,
            "timestamp": current_time.isoformat()
        })

        return HealthResponse(
            status="healthy",
            timestamp=current_time,
            version=settings.version,
            uptime_seconds=uptime
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            version=settings.version,
            uptime_seconds=time.time() - startup_time
        )


@router.get("/readiness", response_model=ReadinessCheckResponse)
def readiness_check(db: Session = Depends(get_db)):
    """Kubernetes-style readiness probe."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not ready", "error": str(e)}


@router.get("/liveness", response_model=ReadinessCheckResponse)
def liveness_check():
    """Kubernetes-style liveness probe."""
    return {"status": "alive"}