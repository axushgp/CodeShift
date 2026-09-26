"""
AgentTaskSpec model.

The canonical machine-readable specification produced by CodeShift to hand off
a verified migration task to another coding agent (architecture.md §15).

Preserves status distinctions:
    VERIFIED | PROPOSED | REQUIRES_HUMAN_REVIEW
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field

from app.models.finding import MigrationFinding


class TaskDetails(BaseModel):
    """Core task metadata and upgrade targets."""

    package: str = Field(description="Package or runtime being upgraded")
    from_version: Optional[str] = Field(
        default=None, description="Starting version (detected or specified)"
    )
    to_version: str = Field(description="Target version")
    status: str = Field(
        default="PROPOSED",
        description="Overall migration state: VERIFIED | PROPOSED | REQUIRES_HUMAN_REVIEW",
    )
    summary: Optional[str] = Field(
        default=None, description="Executive summary of the migration rehearsal"
    )


class RepositoryContext(BaseModel):
    """Key repository profile details relevant for the coding agent."""

    name: Optional[str] = None
    ecosystem: str = "node"
    runtime: Optional[str] = None
    framework: Optional[str] = None
    package_manager: str = "npm"
    source_url: Optional[str] = None


class ImplementationStep(BaseModel):
    """An individual implementation action for the agent to perform or inspect."""

    step_number: int
    action_type: str
    description: str
    target_files: list[str] = Field(default_factory=list)
    status: str = "PROPOSED"
    notes: Optional[str] = None


class VerificationSummary(BaseModel):
    """Verification results comparing baseline to post-migration and post-repair states."""

    baseline_passed: bool = False
    final_verification_passed: bool = False
    regressions_count: int = 0
    status: str = "PROPOSED"
    details: list[str] = Field(default_factory=list)


class AgentTaskSpec(BaseModel):
    """
    Canonical machine-readable handoff specification.

    Source of truth for the Agent Pack and standalone coding agents.
    """

    rehearsal_id: str
    task: TaskDetails
    repository: RepositoryContext
    findings: list[MigrationFinding] = Field(default_factory=list)
    implementation_plan: list[ImplementationStep] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    files_to_modify: list[str] = Field(default_factory=list)
    files_not_to_modify: list[str] = Field(default_factory=list)
    verification: VerificationSummary
    acceptance_criteria: list[str] = Field(default_factory=list)
