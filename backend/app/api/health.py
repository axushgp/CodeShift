"""
Health check endpoint.

GET /health — confirms the backend is running and returns basic info.
"""

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    environment: str
    timestamp: str


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
    """
    Returns a structured health response.

    This endpoint confirms the backend is running and exposes basic
    application metadata. It does not check external services.
    """
    settings = get_settings()
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
