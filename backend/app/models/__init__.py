"""
CodeShift domain models package.

These are the core typed models shared throughout the CodeShift backend.
All models use Pydantic v2 for validation and serialization.
"""

from app.models.rehearsal import (
    Rehearsal,
    RehearsalStatus,
    RehearsalStage,
    TargetUpgrade,
    RepositorySource,
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
from app.models.migration_plan import MigrationPlan, PlannedAction
from app.models.twin import TwinResult, TwinMethod, MigrationStatus, ChangedFile
from app.models.verification import VerificationResult, VerificationContext
from app.models.verification_run import VerificationRun, DiagnosisRecord, RepairRecord

__all__ = [
    # Rehearsal
    "Rehearsal",
    "RehearsalStatus",
    "RehearsalStage",
    "TargetUpgrade",
    "RepositorySource",
    # Repository Profile
    "RepositoryProfile",
    "Ecosystem",
    "PackageManager",
    # Baseline
    "BaselineResult",
    "CommandResult",
    "StepStatus",
    "TestRunSummary",
    # Finding
    "MigrationFinding",
    "FindingType",
    "FindingSeverity",
    "FindingStatus",
    # Migration Plan
    "MigrationPlan",
    "PlannedAction",
    # Twin
    "TwinResult",
    "TwinMethod",
    "MigrationStatus",
    "ChangedFile",
    # Verification
    "VerificationResult",
    "VerificationContext",
    # Verification Run (Session 5)
    "VerificationRun",
    "DiagnosisRecord",
    "RepairRecord",
]
