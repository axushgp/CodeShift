"""
MigrationPlan model.

Represents the complete migration analysis: what needs to change, why,
and how. Produced by the Migration Intelligence + Watsonx analysis stage.
Persisted as migration_plan.json.
"""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.models.finding import MigrationFinding


class ActionType(str, Enum):
    """Mechanism by which a planned action will be applied."""

    CODEMOD = "CODEMOD"
    AST_TRANSFORM = "AST_TRANSFORM"
    VERSION_BUMP = "VERSION_BUMP"
    CONFIG_CHANGE = "CONFIG_CHANGE"
    MANUAL = "MANUAL"
    WATSONX_SEMANTIC = "WATSONX_SEMANTIC"


class PlannedAction(BaseModel):
    """
    A concrete action to apply during migration.

    Maps one or more MigrationFindings to a specific change mechanism.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    finding_ids: list[str] = Field(
        default_factory=list,
        description="IDs of MigrationFindings this action resolves",
    )
    action_type: ActionType
    description: str = Field(description="Human-readable description of what will change")
    target_files: list[str] = Field(
        default_factory=list,
        description="Repository-relative paths that will be modified",
    )
    # Command or codemod to run (if deterministic)
    command: Optional[str] = Field(default=None)
    # Patch content (if pre-computed)
    patch: Optional[str] = Field(default=None)


class MigrationPlan(BaseModel):
    """
    The complete migration analysis and execution plan.

    Created by the Migration Intelligence stage (Session 3+).
    Persisted as migration_plan.json.
    """

    rehearsal_id: str = Field(description="Parent rehearsal identifier")

    # What is being migrated
    package: str = Field(description="Package being upgraded, e.g. 'react'")
    from_version: Optional[str] = None
    to_version: str = Field(description="Target version")
    framework: Optional[str] = Field(default=None, description="Primary framework name, e.g. 'React'")
    migration_path: Optional[str] = Field(default=None, description="Human-readable migration path, e.g. 'React 17 -> React 18'")
    recipe_id: Optional[str] = Field(default=None, description="Certified recipe identifier if available")

    # Analysis results
    findings: list[MigrationFinding] = Field(default_factory=list)
    planned_actions: list[PlannedAction] = Field(default_factory=list)

    # Summary
    total_findings: int = Field(default=0)
    critical_findings: int = Field(default=0)
    requires_human_review: bool = Field(default=False)

    # Source context
    knowledge_sources: list[str] = Field(
        default_factory=list,
        description="Migration knowledge files consulted",
    )
    watsonx_model: Optional[str] = Field(
        default=None, description="Watsonx model ID used for analysis"
    )

    notes: Optional[str] = None

    def recompute_summary(self) -> None:
        """Recompute derived summary fields from findings list."""
        from app.models.finding import FindingSeverity, FindingStatus

        self.total_findings = len(self.findings)
        self.critical_findings = sum(
            1 for f in self.findings if f.severity == FindingSeverity.CRITICAL
        )
        self.requires_human_review = any(
            f.status == FindingStatus.REQUIRES_HUMAN_REVIEW for f in self.findings
        )
