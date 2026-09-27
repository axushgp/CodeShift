"""
Demos API — List verified Quick Start demo repositories and launch them.

GET  /api/demos              — List verified Quick Start demo configurations
GET  /api/demos/{demo_id}    — Get specific demo configuration
POST /api/demos/{demo_id}/launch — Launch rehearsal using existing CodeShift pipeline
"""

from __future__ import annotations

import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.api.rehearsals import RehearsalResponse, _run_intake_pipeline
from app.models.demo import DemoManifest
from app.models.rehearsal import (
    Rehearsal,
    RehearsalStage,
    RehearsalStatus,
    RepositorySource,
    TargetUpgrade,
)
from app.services import demos as demos_svc
from app.services import store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/demos", tags=["Demos"])


@router.get("", response_model=list[DemoManifest])
async def list_demos() -> list[DemoManifest]:
    """Return all verified Quick Start demo configurations."""
    return demos_svc.get_all_demos()


@router.get("/{demo_id}", response_model=DemoManifest)
async def get_demo(demo_id: str) -> DemoManifest:
    """Return a single demo configuration by ID."""
    demo = demos_svc.get_demo_by_id(demo_id)
    if not demo:
        raise HTTPException(status_code=404, detail=f"Demo '{demo_id}' not found.")
    return demo


@router.post("/{demo_id}/launch", response_model=RehearsalResponse, status_code=202)
async def launch_demo_rehearsal(
    demo_id: str,
    background_tasks: BackgroundTasks,
) -> RehearsalResponse:
    """
    Launch a rehearsal for a verified Quick Start demo.

    Reuses the exact same CodeShift rehearsal pipeline as standard repositories.
    """
    demo = demos_svc.get_demo_by_id(demo_id)
    if not demo:
        raise HTTPException(status_code=404, detail=f"Demo '{demo_id}' not found.")

    rehearsal = Rehearsal(
        repository=RepositorySource(url=demo.repository_url, is_demo=True),
        target_upgrade=TargetUpgrade(
            package=demo.package or "unknown",
            from_version=demo.source_version,
            to_version=demo.target_version or "unknown",
        ),
        status=RehearsalStatus.RUNNING,
        stage=RehearsalStage.INTAKE,
    )
    store.save_rehearsal(rehearsal)

    background_tasks.add_task(
        _run_intake_pipeline,
        rehearsal.id,
        demo.repository_url,
        None,
    )

    logger.info("Launched demo rehearsal %s for demo %s (%s)", rehearsal.id, demo.id, demo.repository_url)
    return RehearsalResponse(rehearsal=rehearsal)
