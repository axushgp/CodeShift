"""
MigrationFinding model.

A MigrationFinding is the central internal object representing one
migration issue discovered during analysis, execution, or verification.

Traceability chain (architecture.md §8):
    Evidence → Finding → PlannedAction → ChangedFiles → Verification

Status values mirror architecture.md:
    VERIFIED | PROPOSED | REQUIRES_HUMAN_REVIEW
"""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class FindingType(str, Enum):
    """Category of a migration finding."""

    BREAKING_CHANGE = "BREAKING_CHANGE"
    DEPRECATED_API = "DEPRECATED_API"
    CONFIGURATION_CHANGE = "CONFIGURATION_CHANGE"
    DEPENDENCY_CONFLICT = "DEPENDENCY_CONFLICT"
    TYPE_ERROR = "TYPE_ERROR"
    BUILD_FAILURE = "BUILD_FAILURE"
    TEST_FAILURE = "TEST_FAILURE"
    LINT_FAILURE = "LINT_FAILURE"
    MANUAL_MIGRATION_REQUIRED = "MANUAL_MIGRATION_REQUIRED"
    INFORMATIONAL = "INFORMATIONAL"


class FindingSeverity(str, Enum):
    """Impact severity of a finding."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class FindingStatus(str, Enum):
    """
    Lifecycle status of a finding.

    Mirrors architecture.md §8 and §15:
        VERIFIED          — confirmed fixed and verified in Twin
        PROPOSED          — proposed fix not yet verified
        REQUIRES_HUMAN_REVIEW — cannot be auto-resolved
        OPEN              — identified, not yet addressed
        IN_PROGRESS       — being actively addressed
    """

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    PROPOSED = "PROPOSED"
    VERIFIED = "VERIFIED"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"


class MigrationFinding(BaseModel):
    """
    One migration issue/finding discovered during the rehearsal.

    Each finding carries evidence so the traceability chain can be
    preserved through repair and into the AgentTaskSpec (Session 6+).
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique finding identifier",
    )
    type: FindingType
    severity: FindingSeverity

    title: str = Field(description="Short human-readable title for the finding")
    reason: str = Field(description="Why this is a finding / what needs to change")
    evidence: Optional[str] = Field(
        default=None,
        description="Raw evidence: error message, code snippet, diff fragment, etc.",
    )
    required_action: str = Field(
        description="What must be done to resolve this finding"
    )

    affected_files: list[str] = Field(
        default_factory=list,
        description="Repository-relative paths of affected files",
    )

    status: FindingStatus = Field(default=FindingStatus.OPEN)

    # Populated when the finding is linked to a planned action
    planned_action_id: Optional[str] = Field(default=None)

    # Set when the finding has been verified after repair
    verification_note: Optional[str] = Field(default=None)
