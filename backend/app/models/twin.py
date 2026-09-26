"""
TwinResult model.

Represents the disposable Twin workspace created for migration execution,
and the result of running the migration inside it.

Persisted as twin_result.json under the rehearsal directory.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TwinMethod(str, Enum):
    """How the Twin was created."""

    GIT_WORKTREE = "GIT_WORKTREE"
    TEMP_COPY = "TEMP_COPY"


class MigrationStatus(str, Enum):
    """Outcome of the migration execution inside the Twin."""

    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"   # some changes applied, some skipped/manual
    FAILED = "FAILED"


class ChangedFile(BaseModel):
    """One file changed during migration."""

    path: str = Field(description="Repository-relative path")
    change_type: str = Field(description="modified | added | deleted")


class TwinResult(BaseModel):
    """
    State of the disposable Twin and the migration that ran inside it.

    Created at TWIN_CREATING, updated at MIGRATING, persisted as twin_result.json.
    Session 5 reads this to run verification and diagnosis.
    """

    rehearsal_id: str = Field(description="Parent rehearsal identifier")

    # Twin location
    method: TwinMethod = Field(description="How the Twin was created")
    twin_path: str = Field(description="Absolute path to the Twin workspace")
    worktree_branch: Optional[str] = Field(
        default=None,
        description="Git branch name used when method is GIT_WORKTREE",
    )
    starting_revision: Optional[str] = Field(
        default=None,
        description="Git commit SHA the Twin started from",
    )

    # Migration outcome
    migration_status: MigrationStatus = Field(default=MigrationStatus.PENDING)
    changed_files: list[ChangedFile] = Field(default_factory=list)
    git_diff: Optional[str] = Field(
        default=None,
        description="Full unified diff of all changes made inside the Twin",
    )
    execution_log: list[str] = Field(
        default_factory=list,
        description="Ordered log of actions taken by the executor",
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Set when migration_status is FAILED",
    )

    # Actions applied / skipped
    actions_applied: list[str] = Field(
        default_factory=list,
        description="PlannedAction IDs that were successfully applied",
    )
    actions_skipped: list[str] = Field(
        default_factory=list,
        description="PlannedAction IDs that were skipped (manual or unsupported)",
    )
    manual_items: list[str] = Field(
        default_factory=list,
        description="Items that require human action — recorded for Session 5+",
    )
