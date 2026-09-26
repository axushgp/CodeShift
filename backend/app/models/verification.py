"""
VerificationResult model.

Represents a verification run performed after migration or repair.
The system tracks multiple verification rounds so the history:
    184/184 → 176/184 → 184/184
is preserved (architecture.md §11).
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.models.baseline import CommandResult, StepStatus, TestRunSummary


class VerificationContext(str, Enum):
    """When during the rehearsal was this verification run."""

    POST_MIGRATION = "POST_MIGRATION"
    POST_REPAIR = "POST_REPAIR"
    FINAL = "FINAL"


class VerificationResult(BaseModel):
    """
    Result of a verification run inside the Twin after migration or repair.

    Mirrors BaselineResult structure so results can be diff'd directly.
    """

    rehearsal_id: str = Field(description="Parent rehearsal identifier")
    context: VerificationContext = Field(
        description="When this verification was performed"
    )
    round: int = Field(
        default=1, description="Verification round number (1 = first post-migration)"
    )

    # Step results
    install: Optional[CommandResult] = None
    build: Optional[CommandResult] = None
    test: Optional[CommandResult] = None
    lint: Optional[CommandResult] = None

    # Parsed test summary
    test_summary: Optional[TestRunSummary] = None

    # Overall
    passed: bool = Field(default=False)

    # Regressions (failures not present at baseline)
    regression_count: int = Field(
        default=0,
        description="Number of new failures compared to baseline",
    )
    regression_details: list[str] = Field(
        default_factory=list,
        description="Human-readable list of regressions",
    )

    # Baseline comparison
    baseline_test_total: Optional[int] = Field(
        default=None, description="Baseline total test count for comparison"
    )
    baseline_test_passed: Optional[int] = Field(
        default=None, description="Baseline passing test count for comparison"
    )

    notes: Optional[str] = None

    def compute_passed(self) -> bool:
        """Recompute passed from individual steps."""
        steps = [s for s in [self.install, self.build, self.test, self.lint] if s]
        self.passed = all(s.status == StepStatus.PASSED for s in steps)
        return self.passed
