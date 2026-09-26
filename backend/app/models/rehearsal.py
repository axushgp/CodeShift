"""
Rehearsal model.

A Rehearsal represents one complete end-to-end migration rehearsal run.
It tracks the repository being migrated, the target upgrade, the current
stage, overall status, and timing.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RehearsalStatus(str, Enum):
    """Top-level lifecycle status of a rehearsal."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"


class RehearsalStage(str, Enum):
    """
    Granular workflow stage within a rehearsal.

    Mirrors the locked end-to-end workflow from architecture.md:
    INTAKE → SCANNING → BASELINING → ANALYZING → TWIN_CREATING
    → MIGRATING → VERIFYING → DIAGNOSING → REPAIRING
    → FINALIZING → COMPLETE
    """

    INTAKE = "INTAKE"
    SCANNING = "SCANNING"
    BASELINING = "BASELINING"
    ANALYZING = "ANALYZING"
    TWIN_CREATING = "TWIN_CREATING"
    MIGRATING = "MIGRATING"
    VERIFYING = "VERIFYING"
    DIAGNOSING = "DIAGNOSING"
    REPAIRING = "REPAIRING"
    FINALIZING = "FINALIZING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"


class RepositorySource(BaseModel):
    """Describes where the repository comes from."""

    url: Optional[str] = Field(
        default=None,
        description="Public Git repository URL (for live mode)",
    )
    zip_path: Optional[str] = Field(
        default=None,
        description="Local path to a repository ZIP (for zip-upload mode)",
    )
    local_path: Optional[str] = Field(
        default=None,
        description="Resolved local working path after cloning/extraction",
    )
    is_demo: bool = Field(
        default=False,
        description="True when using the pre-loaded demo repository",
    )


class TargetUpgrade(BaseModel):
    """The upgrade the rehearsal is rehearsing."""

    package: str = Field(description="Package or runtime being upgraded, e.g. 'react'")
    from_version: Optional[str] = Field(
        default=None,
        description="Version being upgraded from (detected from repo when absent)",
    )
    to_version: str = Field(description="Target version to upgrade to, e.g. '18'")
    ecosystem: Optional[str] = Field(
        default=None,
        description="Ecosystem hint, e.g. 'node', 'python'",
    )


class Rehearsal(BaseModel):
    """
    A single CodeShift migration rehearsal.

    Created at intake and updated as the rehearsal progresses through stages.
    Persisted as JSON on the filesystem.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique rehearsal identifier",
    )
    status: RehearsalStatus = Field(default=RehearsalStatus.PENDING)
    stage: RehearsalStage = Field(default=RehearsalStage.INTAKE)

    repository: RepositorySource
    target_upgrade: TargetUpgrade

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    completed_at: Optional[datetime] = None

    error_message: Optional[str] = Field(
        default=None,
        description="Set when status is FAILED",
    )
    active_operation: Optional[str] = Field(
        default=None,
        description="Currently active operation or command description for UI progress",
    )

    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)
