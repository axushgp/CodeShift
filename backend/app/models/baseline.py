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
    TIMEOUT = "TIMEOUT"
    SKIPPED = "SKIPPED"
    SKIPPED_NOT_APPLICABLE = "SKIPPED_NOT_APPLICABLE"
    ENVIRONMENT_UNAVAILABLE = "ENVIRONMENT_UNAVAILABLE"
    NOT_RUN = "NOT_RUN"


class BaselineStatus(str, Enum):
    """Overall outcome of repository baseline verification."""

    PASS = "PASS"
    FAIL = "FAIL"
    TIMEOUT = "TIMEOUT"
    SKIPPED_NOT_APPLICABLE = "SKIPPED_NOT_APPLICABLE"
    ENVIRONMENT_UNAVAILABLE = "ENVIRONMENT_UNAVAILABLE"


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

    # Overall baseline status
    status: BaselineStatus = Field(
        default=BaselineStatus.FAIL,
        description="Overall baseline status: PASS, FAIL, TIMEOUT, SKIPPED_NOT_APPLICABLE, ENVIRONMENT_UNAVAILABLE",
    )

    # Active step in progress (e.g. 'install', 'build', 'test', 'lint')
    active_step: Optional[str] = Field(
        default=None,
        description="Name of the currently running baseline step, or None if idle/completed",
    )

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
        Recompute the passed flag and overall status from individual step results.

        Distinguishes clearly between:
          - PASS: All applicable executed steps passed (at least one passed, none failed/unavailable/timed out).
          - TIMEOUT: Any executed step timed out.
          - FAIL: Any applicable executed step failed.
          - SKIPPED_NOT_APPLICABLE: No steps were applicable.
          - ENVIRONMENT_UNAVAILABLE: Package manager or execution environment was missing.
        """
        steps = [s for s in [self.install, self.build, self.test, self.lint] if s]

        if any(s.status == StepStatus.ENVIRONMENT_UNAVAILABLE for s in steps):
            self.status = BaselineStatus.ENVIRONMENT_UNAVAILABLE
            self.passed = False
            return False

        if any(s.status == StepStatus.TIMEOUT for s in steps):
            self.status = BaselineStatus.TIMEOUT
            self.passed = False
            return False

        if any(s.status == StepStatus.FAILED for s in steps):
            self.status = BaselineStatus.FAIL
            self.passed = False
            return False

        passed_steps = [s for s in steps if s.status == StepStatus.PASSED]
        if passed_steps:
            self.status = BaselineStatus.PASS
            self.passed = True
            return True

        if steps and all(
            s.status in (StepStatus.SKIPPED, StepStatus.SKIPPED_NOT_APPLICABLE, StepStatus.NOT_RUN)
            for s in steps
        ):
            self.status = BaselineStatus.SKIPPED_NOT_APPLICABLE
            self.passed = True
            return True

        if not steps:
            self.status = BaselineStatus.PASS
            self.passed = True
            return True

        self.status = BaselineStatus.FAIL
        self.passed = False
        return False
