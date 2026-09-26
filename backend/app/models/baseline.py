"""
BaselineResult model.

Represents the repository's known-good state before migration begins.
The baseline is critical: migration failures must be distinguished from
pre-existing failures.

Produced by the Baseline Verifier (Session 2+).
Persisted as baseline.json inside the rehearsal data directory.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class StepStatus(str, Enum):
    """Outcome of a single baseline/verification step."""

    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    NOT_RUN = "NOT_RUN"


class CommandResult(BaseModel):
    """Result of a single command execution (install, build, test, lint)."""

    step: str = Field(description="Step name, e.g. 'install', 'build', 'test', 'lint'")
    command: str = Field(description="Exact command that was run")
    exit_code: int = Field(description="Process exit code")
    stdout: str = Field(default="")
    stderr: str = Field(default="")
    duration_seconds: Optional[float] = None
    status: StepStatus = Field(default=StepStatus.NOT_RUN)

    @property
    def passed(self) -> bool:
        return self.status == StepStatus.PASSED


class TestRunSummary(BaseModel):
    """Parsed test result summary."""

    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration_seconds: Optional[float] = None

    @property
    def all_passing(self) -> bool:
        return self.failed == 0 and self.total > 0


class BaselineResult(BaseModel):
    """
    Pre-migration baseline state of the repository.

    Captures install, build, test, and lint results so that post-migration
    verification can compute a meaningful diff.
    """

    rehearsal_id: str = Field(description="Parent rehearsal identifier")

    # Step results
    install: Optional[CommandResult] = None
    build: Optional[CommandResult] = None
    test: Optional[CommandResult] = None
    lint: Optional[CommandResult] = None

    # Parsed test summary from the test step
    test_summary: Optional[TestRunSummary] = None

    # Overall pass/fail
    passed: bool = Field(
        default=False,
        description="True only when all executed steps passed",
    )

    notes: Optional[str] = Field(
        default=None,
        description="Human-readable notes about baseline anomalies",
    )

    def compute_passed(self) -> bool:
        """
        Recompute the passed flag from individual step results.
        A step that was not run (NOT_RUN / None) does not fail the baseline.
        """
        steps = [s for s in [self.install, self.build, self.test, self.lint] if s]
        self.passed = all(s.status == StepStatus.PASSED for s in steps)
        return self.passed
