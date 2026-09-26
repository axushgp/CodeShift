"""
Unit tests for domain models.

Verifies that models validate correctly, reject bad data, and expose
the helper methods required by later sessions.
"""

import pytest
from pydantic import ValidationError

from app.models.rehearsal import (
    Rehearsal,
    RehearsalStatus,
    RehearsalStage,
    RepositorySource,
    TargetUpgrade,
)
from app.models.repository_profile import (
    RepositoryProfile,
    Ecosystem,
    PackageManager,
)
from app.models.baseline import (
    BaselineResult,
    CommandResult,
    StepStatus,
    TestRunSummary,
)
from app.models.finding import (
    MigrationFinding,
    FindingType,
    FindingSeverity,
    FindingStatus,
)
from app.models.migration_plan import MigrationPlan, PlannedAction, ActionType
from app.models.verification import VerificationResult, VerificationContext


# ---------------------------------------------------------------------------
# Rehearsal
# ---------------------------------------------------------------------------


class TestRehearsal:
    def test_rehearsal_created_with_defaults(
        self, sample_rehearsal: Rehearsal
    ) -> None:
        assert sample_rehearsal.id is not None
        assert len(sample_rehearsal.id) == 36  # UUID4
        assert sample_rehearsal.status == RehearsalStatus.PENDING
        assert sample_rehearsal.stage == RehearsalStage.INTAKE
        assert sample_rehearsal.created_at is not None
        assert sample_rehearsal.completed_at is None

    def test_rehearsal_requires_repository(self) -> None:
        with pytest.raises(ValidationError):
            Rehearsal(target_upgrade=TargetUpgrade(package="react", to_version="18"))  # type: ignore[call-arg]

    def test_rehearsal_requires_target_upgrade(self) -> None:
        with pytest.raises(ValidationError):
            Rehearsal(repository=RepositorySource(url="https://example.com"))  # type: ignore[call-arg]

    def test_rehearsal_touch_updates_timestamp(
        self, sample_rehearsal: Rehearsal
    ) -> None:
        original_ts = sample_rehearsal.updated_at
        import time
        time.sleep(0.01)
        sample_rehearsal.touch()
        assert sample_rehearsal.updated_at > original_ts

    def test_demo_repository_flag(self) -> None:
        source = RepositorySource(is_demo=True)
        assert source.is_demo is True
        assert source.url is None

    def test_target_upgrade_fields(self) -> None:
        upgrade = TargetUpgrade(package="react", from_version="17", to_version="18")
        assert upgrade.package == "react"
        assert upgrade.from_version == "17"
        assert upgrade.to_version == "18"


# ---------------------------------------------------------------------------
# RepositoryProfile
# ---------------------------------------------------------------------------


class TestRepositoryProfile:
    def test_profile_defaults(self) -> None:
        profile = RepositoryProfile(rehearsal_id="test-id")
        assert profile.ecosystem == Ecosystem.UNKNOWN
        assert profile.package_manager == PackageManager.UNKNOWN
        assert profile.dependencies == {}
        assert profile.dev_dependencies == {}

    def test_profile_with_data(self) -> None:
        profile = RepositoryProfile(
            rehearsal_id="test-id",
            name="demo-app",
            ecosystem=Ecosystem.NODE,
            package_manager=PackageManager.NPM,
            framework="react",
            dependencies={"react": "^17.0.2", "react-dom": "^17.0.2"},
            dev_dependencies={"typescript": "^5.0.0"},
        )
        assert profile.ecosystem == Ecosystem.NODE
        assert "react" in profile.dependencies
        assert profile.framework == "react"

    def test_profile_requires_rehearsal_id(self) -> None:
        with pytest.raises(ValidationError):
            RepositoryProfile()  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# BaselineResult
# ---------------------------------------------------------------------------


class TestBaselineResult:
    def test_baseline_defaults(self) -> None:
        baseline = BaselineResult(rehearsal_id="test-id")
        assert baseline.passed is False
        assert baseline.install is None

    def test_command_result_passed_property(self) -> None:
        result = CommandResult(
            step="install",
            command="npm ci",
            exit_code=0,
            status=StepStatus.PASSED,
        )
        assert result.passed is True

    def test_command_result_failed_property(self) -> None:
        result = CommandResult(
            step="test",
            command="npm test",
            exit_code=1,
            status=StepStatus.FAILED,
        )
        assert result.passed is False

    def test_compute_passed_all_pass(self) -> None:
        baseline = BaselineResult(rehearsal_id="test-id")
        baseline.install = CommandResult(
            step="install", command="npm ci", exit_code=0, status=StepStatus.PASSED
        )
        baseline.test = CommandResult(
            step="test", command="npm test", exit_code=0, status=StepStatus.PASSED
        )
        assert baseline.compute_passed() is True

    def test_compute_passed_one_fails(self) -> None:
        baseline = BaselineResult(rehearsal_id="test-id")
        baseline.install = CommandResult(
            step="install", command="npm ci", exit_code=0, status=StepStatus.PASSED
        )
        baseline.test = CommandResult(
            step="test", command="npm test", exit_code=1, status=StepStatus.FAILED
        )
        assert baseline.compute_passed() is False

    def test_test_summary_all_passing(self) -> None:
        summary = TestRunSummary(total=184, passed=184, failed=0)
        assert summary.all_passing is True

    def test_test_summary_failures(self) -> None:
        summary = TestRunSummary(total=184, passed=176, failed=8)
        assert summary.all_passing is False


# ---------------------------------------------------------------------------
# MigrationFinding
# ---------------------------------------------------------------------------


class TestMigrationFinding:
    def test_finding_created(self, sample_finding: MigrationFinding) -> None:
        assert sample_finding.id is not None
        assert sample_finding.type == FindingType.BREAKING_CHANGE
        assert sample_finding.severity == FindingSeverity.HIGH
        assert sample_finding.status == FindingStatus.OPEN
        assert "src/index.tsx" in sample_finding.affected_files

    def test_finding_requires_mandatory_fields(self) -> None:
        with pytest.raises(ValidationError):
            MigrationFinding(  # missing required fields
                type=FindingType.BREAKING_CHANGE,
            )  # type: ignore[call-arg]

    def test_finding_status_values(self) -> None:
        """All FindingStatus values from architecture.md must exist."""
        assert FindingStatus.VERIFIED
        assert FindingStatus.PROPOSED
        assert FindingStatus.REQUIRES_HUMAN_REVIEW
        assert FindingStatus.OPEN
        assert FindingStatus.IN_PROGRESS

    def test_finding_severity_values(self) -> None:
        assert FindingSeverity.CRITICAL
        assert FindingSeverity.HIGH
        assert FindingSeverity.MEDIUM
        assert FindingSeverity.LOW


# ---------------------------------------------------------------------------
# MigrationPlan
# ---------------------------------------------------------------------------


class TestMigrationPlan:
    def test_plan_defaults(self) -> None:
        plan = MigrationPlan(
            rehearsal_id="test-id",
            package="react",
            to_version="18",
        )
        assert plan.findings == []
        assert plan.planned_actions == []
        assert plan.requires_human_review is False

    def test_plan_recompute_summary(self, sample_finding: MigrationFinding) -> None:
        plan = MigrationPlan(
            rehearsal_id="test-id",
            package="react",
            to_version="18",
            findings=[sample_finding],
        )
        plan.recompute_summary()
        assert plan.total_findings == 1
        assert plan.requires_human_review is False

    def test_plan_recompute_requires_human_review(
        self, sample_finding: MigrationFinding
    ) -> None:
        sample_finding.status = FindingStatus.REQUIRES_HUMAN_REVIEW
        plan = MigrationPlan(
            rehearsal_id="test-id",
            package="react",
            to_version="18",
            findings=[sample_finding],
        )
        plan.recompute_summary()
        assert plan.requires_human_review is True

    def test_planned_action(self) -> None:
        action = PlannedAction(
            action_type=ActionType.CODEMOD,
            description="Run react-codemod replace-render-with-createroot",
            target_files=["src/index.tsx"],
            command="npx react-codemod replace-render-with-createroot",
        )
        assert action.id is not None
        assert action.action_type == ActionType.CODEMOD


# ---------------------------------------------------------------------------
# VerificationResult
# ---------------------------------------------------------------------------


class TestVerificationResult:
    def test_verification_defaults(self) -> None:
        result = VerificationResult(
            rehearsal_id="test-id",
            context=VerificationContext.POST_MIGRATION,
        )
        assert result.passed is False
        assert result.regression_count == 0
        assert result.round == 1

    def test_verification_compute_passed(self) -> None:
        result = VerificationResult(
            rehearsal_id="test-id",
            context=VerificationContext.POST_REPAIR,
            round=2,
        )
        result.test = CommandResult(
            step="test", command="npm test", exit_code=0, status=StepStatus.PASSED
        )
        assert result.compute_passed() is True

    def test_verification_context_values(self) -> None:
        assert VerificationContext.POST_MIGRATION
        assert VerificationContext.POST_REPAIR
        assert VerificationContext.FINAL


# ---------------------------------------------------------------------------
# AgentTaskSpec & Agent Pack
# ---------------------------------------------------------------------------

from app.models.agent_task import AgentTaskSpec, TaskDetails, RepositoryContext, VerificationSummary
from app.services.agent_pack import build_agent_task_spec, generate_agent_pack_files, create_agent_pack_zip_bytes


class TestAgentTaskSpec:
    def test_agent_task_spec_creation(self) -> None:
        spec = AgentTaskSpec(
            rehearsal_id="rehearsal-123",
            task=TaskDetails(
                package="react",
                from_version="17",
                to_version="18",
                status="VERIFIED",
            ),
            repository=RepositoryContext(
                name="my-app",
                ecosystem="node",
                package_manager="npm",
            ),
            constraints=["Do not modify other files"],
            files_to_modify=["package.json", "src/index.js"],
            files_not_to_modify=[".git", "node_modules"],
            verification=VerificationSummary(
                baseline_passed=True,
                final_verification_passed=True,
                regressions_count=0,
                status="VERIFIED",
            ),
            acceptance_criteria=["All tests pass"],
        )
        assert spec.task.package == "react"
        assert spec.task.status == "VERIFIED"
        assert len(spec.files_to_modify) == 2

    def test_generate_pack_files_and_zip(self, sample_rehearsal: Rehearsal) -> None:
        spec = build_agent_task_spec(
            rehearsal=sample_rehearsal,
            profile=None,
            baseline=None,
            plan=None,
            twin=None,
            ver_run=None,
        )
        assert spec.task.package == sample_rehearsal.target_upgrade.package
        files = generate_agent_pack_files(spec, None, None, None)

        expected_files = [
            "agent_task.json",
            "implementation-prompt.md",
            "AGENTS.md",
            "migration-plan.md",
            "findings.json",
            "verification.md",
            "patch.diff",
            "README.md",
        ]
        for ef in expected_files:
            assert ef in files
            assert len(files[ef]) > 0

        zip_bytes = create_agent_pack_zip_bytes(files)
        assert len(zip_bytes) > 0
        assert zip_bytes[:2] == b"PK"  # Valid ZIP signature
