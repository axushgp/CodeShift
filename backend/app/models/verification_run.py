"""
VerificationRun model — Session 5.

A VerificationRun persists the complete result of one verify → diagnose → repair
cycle.  Multiple runs can exist per rehearsal (round 1 = post-migration,
round 2 = post-repair).

Persisted as verification_run_{round}.json under the rehearsal directory.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.models.verification import VerificationResult


class RepairRecord(BaseModel):
    """Persisted record of a single repair attempt."""

    step: str
    applied: bool
    changed_files: list[str] = Field(default_factory=list)
    notes: str = ""
    requires_human_review: bool = False


class DiagnosisRecord(BaseModel):
    """Persisted diagnosis for one failure cluster."""

    step: str
    root_cause: str
    migration_relevant: bool = False
    affected_files: list[str] = Field(default_factory=list)
    requires_human_review: bool = True
    confidence: str = "LOW"
    repair_applied: bool = False
    repair_notes: str = ""


class VerificationRun(BaseModel):
    """
    One complete verify → diagnose → repair cycle.

    round=1  post-migration verification
    round=2  post-repair verification
    """

    rehearsal_id: str
    round: int = Field(default=1)

    verification: VerificationResult
    diagnoses: list[DiagnosisRecord] = Field(default_factory=list)
    repairs: list[RepairRecord] = Field(default_factory=list)

    # Final outcome for this round
    passed: bool = Field(default=False)
    requires_human_review: bool = Field(default=False)
    summary: Optional[str] = None
