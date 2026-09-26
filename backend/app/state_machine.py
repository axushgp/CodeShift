"""
Rehearsal state machine.

Manages valid stage transitions for a Rehearsal, enforcing the locked
end-to-end workflow from architecture.md:

    INTAKE → SCANNING → BASELINING → ANALYZING → TWIN_CREATING
    → MIGRATING → VERIFYING → DIAGNOSING → REPAIRING
    → FINALIZING → COMPLETE

Terminal states: COMPLETE, FAILED, REQUIRES_HUMAN_REVIEW

Later sessions add the actual work performed at each stage. The state
machine only controls transitions.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from app.models.rehearsal import Rehearsal, RehearsalStage, RehearsalStatus
from app.logging_config import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Valid forward transitions
# ---------------------------------------------------------------------------
_TRANSITIONS: dict[RehearsalStage, list[RehearsalStage]] = {
    RehearsalStage.INTAKE: [RehearsalStage.SCANNING, RehearsalStage.FAILED],
    RehearsalStage.SCANNING: [RehearsalStage.BASELINING, RehearsalStage.FAILED],
    RehearsalStage.BASELINING: [
        RehearsalStage.ANALYZING,
        RehearsalStage.REQUIRES_HUMAN_REVIEW,
        RehearsalStage.FAILED,
    ],
    RehearsalStage.ANALYZING: [
        RehearsalStage.TWIN_CREATING,
        RehearsalStage.REQUIRES_HUMAN_REVIEW,
        RehearsalStage.FAILED,
    ],
    RehearsalStage.TWIN_CREATING: [RehearsalStage.MIGRATING, RehearsalStage.FAILED],
    RehearsalStage.MIGRATING: [RehearsalStage.VERIFYING, RehearsalStage.FAILED],
    RehearsalStage.VERIFYING: [
        RehearsalStage.FINALIZING,  # all tests pass
        RehearsalStage.DIAGNOSING,  # failures detected
        RehearsalStage.REQUIRES_HUMAN_REVIEW,
        RehearsalStage.FAILED,
    ],
    RehearsalStage.DIAGNOSING: [
        RehearsalStage.REPAIRING,
        RehearsalStage.FINALIZING,
        RehearsalStage.REQUIRES_HUMAN_REVIEW,
        RehearsalStage.FAILED,
    ],
    RehearsalStage.REPAIRING: [
        RehearsalStage.VERIFYING,  # re-verify after repair
        RehearsalStage.FINALIZING,
        RehearsalStage.REQUIRES_HUMAN_REVIEW,
        RehearsalStage.FAILED,
    ],
    RehearsalStage.FINALIZING: [
        RehearsalStage.COMPLETE,
        RehearsalStage.REQUIRES_HUMAN_REVIEW,
        RehearsalStage.FAILED,
    ],
    # Terminal stages — no outgoing transitions
    RehearsalStage.COMPLETE: [],
    RehearsalStage.FAILED: [],
    RehearsalStage.REQUIRES_HUMAN_REVIEW: [],
}

# Stages that map to RUNNING status
_RUNNING_STAGES = {
    RehearsalStage.SCANNING,
    RehearsalStage.BASELINING,
    RehearsalStage.ANALYZING,
    RehearsalStage.TWIN_CREATING,
    RehearsalStage.MIGRATING,
    RehearsalStage.VERIFYING,
    RehearsalStage.DIAGNOSING,
    RehearsalStage.REPAIRING,
    RehearsalStage.FINALIZING,
}


class InvalidTransitionError(Exception):
    """Raised when a requested stage transition is not permitted."""

    def __init__(self, from_stage: RehearsalStage, to_stage: RehearsalStage) -> None:
        super().__init__(
            f"Invalid transition: {from_stage.value} → {to_stage.value}"
        )
        self.from_stage = from_stage
        self.to_stage = to_stage


class RehearsalStateMachine:
    """
    Controls stage transitions for a single Rehearsal.

    Usage:
        sm = RehearsalStateMachine(rehearsal)
        sm.transition(RehearsalStage.SCANNING)   # advances stage
        sm.fail("Something went wrong")           # moves to FAILED
    """

    def __init__(self, rehearsal: Rehearsal) -> None:
        self._rehearsal = rehearsal

    @property
    def rehearsal(self) -> Rehearsal:
        return self._rehearsal

    @property
    def current_stage(self) -> RehearsalStage:
        return self._rehearsal.stage

    def can_transition(self, to_stage: RehearsalStage) -> bool:
        """Return True if transitioning to to_stage is permitted."""
        allowed = _TRANSITIONS.get(self._rehearsal.stage, [])
        return to_stage in allowed

    def transition(self, to_stage: RehearsalStage) -> None:
        """
        Advance the rehearsal to to_stage.

        Raises InvalidTransitionError if the transition is not permitted.
        """
        if not self.can_transition(to_stage):
            raise InvalidTransitionError(self._rehearsal.stage, to_stage)

        logger.info(
            "Rehearsal %s: %s → %s",
            self._rehearsal.id,
            self._rehearsal.stage.value,
            to_stage.value,
        )

        self._rehearsal.stage = to_stage
        self._rehearsal.touch()

        # Derive top-level status from stage
        if to_stage == RehearsalStage.COMPLETE:
            self._rehearsal.status = RehearsalStatus.COMPLETE
            self._rehearsal.completed_at = datetime.now(timezone.utc)
        elif to_stage == RehearsalStage.FAILED:
            self._rehearsal.status = RehearsalStatus.FAILED
        elif to_stage == RehearsalStage.REQUIRES_HUMAN_REVIEW:
            self._rehearsal.status = RehearsalStatus.REQUIRES_HUMAN_REVIEW
        elif to_stage == RehearsalStage.INTAKE:
            self._rehearsal.status = RehearsalStatus.PENDING
        elif to_stage in _RUNNING_STAGES:
            self._rehearsal.status = RehearsalStatus.RUNNING

    def fail(self, reason: Optional[str] = None) -> None:
        """
        Move the rehearsal to FAILED regardless of current stage.

        This is a special escape hatch for unexpected errors.
        """
        logger.error(
            "Rehearsal %s: forcing FAILED from %s — %s",
            self._rehearsal.id,
            self._rehearsal.stage.value,
            reason or "no reason given",
        )
        self._rehearsal.stage = RehearsalStage.FAILED
        self._rehearsal.status = RehearsalStatus.FAILED
        self._rehearsal.error_message = reason
        self._rehearsal.touch()

    def allowed_next_stages(self) -> list[RehearsalStage]:
        """Return the list of stages this rehearsal can move to next."""
        return list(_TRANSITIONS.get(self._rehearsal.stage, []))
