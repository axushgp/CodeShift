"""
Unit tests for the rehearsal state machine.

Verifies valid and invalid transitions, status derivation, fail escape
hatch, and terminal state enforcement.
"""

import pytest

from app.models.rehearsal import RehearsalStage, RehearsalStatus
from app.state_machine import RehearsalStateMachine, InvalidTransitionError


class TestStateMachineTransitions:
    def test_initial_stage_is_intake(
        self, sample_state_machine: RehearsalStateMachine
    ) -> None:
        assert sample_state_machine.current_stage == RehearsalStage.INTAKE

    def test_valid_intake_to_scanning(
        self, sample_state_machine: RehearsalStateMachine
    ) -> None:
        sample_state_machine.transition(RehearsalStage.SCANNING)
        assert sample_state_machine.current_stage == RehearsalStage.SCANNING
        assert sample_state_machine.rehearsal.status == RehearsalStatus.RUNNING

    def test_full_happy_path(
        self, sample_state_machine: RehearsalStateMachine
    ) -> None:
        """Walk the complete happy-path workflow end to end."""
        path = [
            RehearsalStage.SCANNING,
            RehearsalStage.BASELINING,
            RehearsalStage.ANALYZING,
            RehearsalStage.TWIN_CREATING,
            RehearsalStage.MIGRATING,
            RehearsalStage.VERIFYING,
            RehearsalStage.FINALIZING,
            RehearsalStage.COMPLETE,
        ]
        for stage in path:
            sample_state_machine.transition(stage)

        assert sample_state_machine.current_stage == RehearsalStage.COMPLETE
        assert sample_state_machine.rehearsal.status == RehearsalStatus.COMPLETE
        assert sample_state_machine.rehearsal.completed_at is not None

    def test_verify_diagnose_repair_verify_path(
        self, sample_state_machine: RehearsalStateMachine
    ) -> None:
        """Walk the verify → diagnose → repair → re-verify path."""
        for stage in [
            RehearsalStage.SCANNING,
            RehearsalStage.BASELINING,
            RehearsalStage.ANALYZING,
            RehearsalStage.TWIN_CREATING,
            RehearsalStage.MIGRATING,
            RehearsalStage.VERIFYING,
            RehearsalStage.DIAGNOSING,
            RehearsalStage.REPAIRING,
            RehearsalStage.VERIFYING,
            RehearsalStage.FINALIZING,
            RehearsalStage.COMPLETE,
        ]:
            sample_state_machine.transition(stage)

        assert sample_state_machine.rehearsal.status == RehearsalStatus.COMPLETE

    def test_invalid_transition_raises(
        self, sample_state_machine: RehearsalStateMachine
    ) -> None:
        with pytest.raises(InvalidTransitionError) as exc_info:
            sample_state_machine.transition(RehearsalStage.MIGRATING)
        assert exc_info.value.from_stage == RehearsalStage.INTAKE
        assert exc_info.value.to_stage == RehearsalStage.MIGRATING

    def test_no_transition_from_complete(
        self, sample_state_machine: RehearsalStateMachine
    ) -> None:
        # Walk to COMPLETE
        for stage in [
            RehearsalStage.SCANNING,
            RehearsalStage.BASELINING,
            RehearsalStage.ANALYZING,
            RehearsalStage.TWIN_CREATING,
            RehearsalStage.MIGRATING,
            RehearsalStage.VERIFYING,
            RehearsalStage.FINALIZING,
            RehearsalStage.COMPLETE,
        ]:
            sample_state_machine.transition(stage)

        # COMPLETE is terminal
        with pytest.raises(InvalidTransitionError):
            sample_state_machine.transition(RehearsalStage.SCANNING)

    def test_can_transition_to_failed_from_any_running_stage(
        self, sample_state_machine: RehearsalStateMachine
    ) -> None:
        sample_state_machine.transition(RehearsalStage.SCANNING)
        assert sample_state_machine.can_transition(RehearsalStage.FAILED)

    def test_can_transition_returns_false_for_invalid(
        self, sample_state_machine: RehearsalStateMachine
    ) -> None:
        assert sample_state_machine.can_transition(RehearsalStage.COMPLETE) is False

    def test_allowed_next_stages_from_intake(
        self, sample_state_machine: RehearsalStateMachine
    ) -> None:
        allowed = sample_state_machine.allowed_next_stages()
        assert RehearsalStage.SCANNING in allowed
        assert RehearsalStage.FAILED in allowed

    def test_requires_human_review_transition(
        self, sample_state_machine: RehearsalStateMachine
    ) -> None:
        sample_state_machine.transition(RehearsalStage.SCANNING)
        sample_state_machine.transition(RehearsalStage.BASELINING)
        sample_state_machine.transition(RehearsalStage.REQUIRES_HUMAN_REVIEW)
        assert sample_state_machine.rehearsal.status == RehearsalStatus.REQUIRES_HUMAN_REVIEW


class TestStateMachineFail:
    def test_fail_from_any_stage(
        self, sample_state_machine: RehearsalStateMachine
    ) -> None:
        sample_state_machine.fail("Something went wrong")
        assert sample_state_machine.current_stage == RehearsalStage.FAILED
        assert sample_state_machine.rehearsal.status == RehearsalStatus.FAILED
        assert sample_state_machine.rehearsal.error_message == "Something went wrong"

    def test_fail_sets_stage_to_failed(
        self, sample_state_machine: RehearsalStateMachine
    ) -> None:
        sample_state_machine.transition(RehearsalStage.SCANNING)
        sample_state_machine.fail("Scanner crashed")
        assert sample_state_machine.current_stage == RehearsalStage.FAILED

    def test_fail_without_reason(
        self, sample_state_machine: RehearsalStateMachine
    ) -> None:
        sample_state_machine.fail()
        assert sample_state_machine.rehearsal.error_message is None
        assert sample_state_machine.current_stage == RehearsalStage.FAILED
