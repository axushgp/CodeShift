"""
Migrations API — Target Discovery & Migration Knowledge Registry Endpoints.

Endpoints:
- POST /api/migrations/discover      — Analyze repository from URL or uploaded ZIP to detect framework, version, and target options.
- GET  /api/migrations/options       — Get migration target options for a framework/version or rehearsal.
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.services import intake as intake_svc
from app.services import scanner as scanner_svc
from app.services import store
from app.services import target_discovery as discovery_svc

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/migrations", tags=["Migrations"])

# In-memory discovery workspace cache (maps discovery_id -> workspace_path)
# Allows immediate start_rehearsal without re-cloning
_DISCOVERY_WORKSPACES: dict[str, str] = {}


def get_cached_discovery_workspace(discovery_id: str) -> Optional[str]:
    """Retrieve and pop cached workspace path for a discovery_id if available."""
    return _DISCOVERY_WORKSPACES.get(discovery_id)


# ── Schemas ───────────────────────────────────────────────────────────────────

class DiscoverTargetsRequest(BaseModel):
    repository_url: Optional[str] = None
    framework: Optional[str] = None
    version: Optional[str] = None


class TargetOption(BaseModel):
    target_version: str
    label: str
    badge: Optional[str] = None
    is_recommended: bool = False
    has_certified_recipe: bool = False
    recipe: Optional[str] = None
    description: str = ""


class UpgradeTargetInfo(BaseModel):
    current: str
    recommended_target: Optional[str] = None
    has_certified_recipe: bool = False
    options: list[TargetOption]


class FrameworkInfo(BaseModel):
    id: str
    name: str
    package: str


class ToolingInfo(BaseModel):
    build_tool: str
    runtime: str
    package_manager: str


class DiscoverTargetsResponse(BaseModel):
    discovery_id: Optional[str] = None
    detected_framework: FrameworkInfo
    detected_version: str
    raw_version: Optional[str] = None
    tooling: ToolingInfo
    upgrade_target: UpgradeTargetInfo
    knowledge_updated: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/discover", response_model=DiscoverTargetsResponse)
async def discover_targets_from_url(
    req: DiscoverTargetsRequest,
) -> DiscoverTargetsResponse:
    """
    Analyze a public Git repository URL to detect the technology stack,
    current framework version, surrounding tooling, and data-driven migration target options.
    """
    if not req.repository_url or not req.repository_url.strip():
        raise HTTPException(status_code=400, detail="repository_url is required for discovery.")

    discovery_id = f"disc-{uuid.uuid4().hex[:10]}"
    url = req.repository_url.strip()

    try:
        # Clone repository
        workspace = intake_svc.clone_repository(url)
        _DISCOVERY_WORKSPACES[discovery_id] = str(workspace)

        # Scan repository
        profile = scanner_svc.scan_repository(workspace, rehearsal_id=discovery_id)
        profile.source_url = url

        # Discover targets
        result = discovery_svc.discover_migration_targets(profile)
        result["discovery_id"] = discovery_id
        return DiscoverTargetsResponse(**result)
    except Exception as exc:
        logger.exception("Failed to discover migration targets for %s: %s", url, exc)
        raise HTTPException(status_code=500, detail=f"Target discovery failed: {exc}") from exc


@router.post("/discover-zip", response_model=DiscoverTargetsResponse)
async def discover_targets_from_zip(
    zip_file: UploadFile = File(...),
) -> DiscoverTargetsResponse:
    """
    Analyze an uploaded repository ZIP file to detect technology stack and target options.
    """
    if not zip_file.filename:
        raise HTTPException(status_code=400, detail="ZIP file must have a filename.")

    discovery_id = f"disc-{uuid.uuid4().hex[:10]}"
    try:
        content = await zip_file.read()
        workspace = intake_svc.unpack_zip(content)
        _DISCOVERY_WORKSPACES[discovery_id] = str(workspace)

        profile = scanner_svc.scan_repository(workspace, rehearsal_id=discovery_id)
        result = discovery_svc.discover_migration_targets(profile)
        result["discovery_id"] = discovery_id
        return DiscoverTargetsResponse(**result)
    except Exception as exc:
        logger.exception("Failed to discover migration targets from ZIP: %s", exc)
        raise HTTPException(status_code=500, detail=f"Target discovery from ZIP failed: {exc}") from exc


@router.get("/options", response_model=DiscoverTargetsResponse)
async def get_migration_options(
    rehearsal_id: Optional[str] = None,
    framework: Optional[str] = None,
    version: Optional[str] = None,
) -> DiscoverTargetsResponse:
    """
    Retrieve migration target options for an existing rehearsal, or query options
    by framework name and version string.
    """
    if rehearsal_id:
        profile = store.load_repo_profile(rehearsal_id)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Rehearsal profile {rehearsal_id} not found.")
        result = discovery_svc.discover_migration_targets(profile)
        result["discovery_id"] = rehearsal_id
        return DiscoverTargetsResponse(**result)

    if framework:
        fw_dict = discovery_svc.find_framework_by_package(framework)
        from app.models.repository_profile import RepositoryProfile, Ecosystem, PackageManager
        dummy_profile = RepositoryProfile(
            rehearsal_id="query",
            ecosystem=Ecosystem.NODE,
            framework=framework,
            package_manager=PackageManager.NPM,
            dependencies={fw_dict.get("package", framework): version or "latest"} if fw_dict else {framework: version or "latest"},
        )
        result = discovery_svc.discover_migration_targets(dummy_profile)
        return DiscoverTargetsResponse(**result)

    raise HTTPException(status_code=400, detail="Either rehearsal_id or framework parameter must be provided.")
