"""
CodeShift FastAPI application.

Responsibilities:
- Application factory
- Router registration
- Exception handlers
- CORS (development)
- Startup logging
"""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.logging_config import configure_logging
from app.api import health
from app.api import rehearsals
from app.api import demos

# Configure logging before anything else
configure_logging()
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Repository Migration Rehearsal System",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS — permissive in development, locked down for production
    origins = (
        ["*"] if settings.environment == "development" else ["http://localhost:5173"]
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health.router)
    app.include_router(rehearsals.router)
    app.include_router(demos.router)

    # Global exception handler
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unhandled exception on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "detail": "An unexpected error occurred.",
            },
        )

    @app.on_event("startup")  # noqa: FastAPI deprecation
    async def on_startup() -> None:
        logger.info(
            "%s v%s starting in %s mode",
            settings.app_name,
            settings.app_version,
            settings.environment,
        )

    return app


# Module-level app instance used by uvicorn
app = create_app()
