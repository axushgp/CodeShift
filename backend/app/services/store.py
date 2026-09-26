"""
Rehearsal store — filesystem-backed persistence.

Saves and loads rehearsal state, repository profiles, and baseline results
as JSON files inside the data directory.

Layout:
  data/
    rehearsals/
      {rehearsal_id}/
        rehearsal.json
        repo_profile.json
        baseline.json

No database. No background workers. Simple and safe for the MVP.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.config import get_settings
from app.models.baseline import BaselineResult
from app.models.migration_plan import MigrationPlan
from app.models.rehearsal import Rehearsal, RehearsalStage, RehearsalStatus
from app.models.repository_profile import RepositoryProfile
from app.models.twin import TwinResult
from app.models.verification_run import VerificationRun

logger = logging.getLogger(__name__)


def _rehearsal_dir(rehearsal_id: str) -> Path:
    settings = get_settings()
    return Path(settings.data_dir) / "rehearsals" / rehearsal_id


def _ensure_dir(rehearsal_id: str) -> Path:
    d = _rehearsal_dir(rehearsal_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


# ── Rehearsal ─────────────────────────────────────────────────────────────────

def save_rehearsal(rehearsal: Rehearsal) -> None:
    d = _ensure_dir(rehearsal.id)
    path = d / "rehearsal.json"
    path.write_text(rehearsal.model_dump_json(indent=2), encoding="utf-8")
    logger.debug("Saved rehearsal %s", rehearsal.id)


def load_rehearsal(rehearsal_id: str) -> Optional[Rehearsal]:
    path = _rehearsal_dir(rehearsal_id) / "rehearsal.json"
    if not path.exists():
        return None
    try:
        return Rehearsal.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Failed to load rehearsal %s: %s", rehearsal_id, exc)
        return None


def update_rehearsal_stage(
    rehearsal_id: str,
    stage: RehearsalStage,
    status: RehearsalStatus = RehearsalStatus.RUNNING,
    error_message: Optional[str] = None,
) -> Optional[Rehearsal]:
    rehearsal = load_rehearsal(rehearsal_id)
    if rehearsal is None:
        return None
    rehearsal.stage = stage
    rehearsal.status = status
    rehearsal.error_message = error_message
    rehearsal.touch()
    if status in (RehearsalStatus.COMPLETE, RehearsalStatus.FAILED):
        rehearsal.completed_at = datetime.now(timezone.utc)
    save_rehearsal(rehearsal)
    return rehearsal


# ── Repository Profile ────────────────────────────────────────────────────────

def save_repo_profile(profile: RepositoryProfile) -> None:
    d = _ensure_dir(profile.rehearsal_id)
    path = d / "repo_profile.json"
    path.write_text(profile.model_dump_json(indent=2), encoding="utf-8")
    logger.debug("Saved repo profile for rehearsal %s", profile.rehearsal_id)


def load_repo_profile(rehearsal_id: str) -> Optional[RepositoryProfile]:
    path = _rehearsal_dir(rehearsal_id) / "repo_profile.json"
    if not path.exists():
        return None
    try:
        return RepositoryProfile.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Failed to load repo profile %s: %s", rehearsal_id, exc)
        return None


# ── Baseline Result ───────────────────────────────────────────────────────────

def save_baseline(baseline: BaselineResult) -> None:
    d = _ensure_dir(baseline.rehearsal_id)
    path = d / "baseline.json"
    path.write_text(baseline.model_dump_json(indent=2), encoding="utf-8")
    logger.debug("Saved baseline for rehearsal %s", baseline.rehearsal_id)


def load_baseline(rehearsal_id: str) -> Optional[BaselineResult]:
    path = _rehearsal_dir(rehearsal_id) / "baseline.json"
    if not path.exists():
        return None
    try:
        return BaselineResult.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Failed to load baseline %s: %s", rehearsal_id, exc)
        return None


# ── Migration Plan ────────────────────────────────────────────────────────────

def save_migration_plan(plan: MigrationPlan) -> None:
    d = _ensure_dir(plan.rehearsal_id)
    path = d / "migration_plan.json"
    path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")
    logger.debug("Saved migration plan for rehearsal %s", plan.rehearsal_id)


def load_migration_plan(rehearsal_id: str) -> Optional[MigrationPlan]:
    path = _rehearsal_dir(rehearsal_id) / "migration_plan.json"
    if not path.exists():
        return None
    try:
        return MigrationPlan.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Failed to load migration plan %s: %s", rehearsal_id, exc)
        return None


# ── Twin Result ───────────────────────────────────────────────────────────────

def save_twin_result(twin: TwinResult) -> None:
    d = _ensure_dir(twin.rehearsal_id)
    path = d / "twin_result.json"
    path.write_text(twin.model_dump_json(indent=2), encoding="utf-8")
    logger.debug("Saved twin result for rehearsal %s", twin.rehearsal_id)


def load_twin_result(rehearsal_id: str) -> Optional[TwinResult]:
    path = _rehearsal_dir(rehearsal_id) / "twin_result.json"
    if not path.exists():
        return None
    try:
        return TwinResult.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Failed to load twin result %s: %s", rehearsal_id, exc)
        return None


# ── Verification Run ──────────────────────────────────────────────────────────

def save_verification_run(run: VerificationRun) -> None:
    d = _ensure_dir(run.rehearsal_id)
    path = d / f"verification_run_{run.round}.json"
    path.write_text(run.model_dump_json(indent=2), encoding="utf-8")
    logger.debug(
        "Saved verification run round=%d for rehearsal %s", run.round, run.rehearsal_id
    )


def load_verification_run(rehearsal_id: str, round_num: int = 1) -> Optional[VerificationRun]:
    path = _rehearsal_dir(rehearsal_id) / f"verification_run_{round_num}.json"
    if not path.exists():
        return None
    try:
        return VerificationRun.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning(
            "Failed to load verification run %s round=%d: %s", rehearsal_id, round_num, exc
        )
        return None


def load_latest_verification_run(rehearsal_id: str) -> Optional[VerificationRun]:
    """Return the highest-round VerificationRun persisted for this rehearsal."""
    d = _rehearsal_dir(rehearsal_id)
    runs: list[VerificationRun] = []
    for p in d.glob("verification_run_*.json"):
        try:
            vr = VerificationRun.model_validate_json(p.read_text(encoding="utf-8"))
            runs.append(vr)
        except Exception:
            continue
    if not runs:
        return None
    return max(runs, key=lambda r: r.round)
