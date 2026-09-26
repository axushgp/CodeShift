"""
Shared test fixtures and helpers.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.models.rehearsal import Rehearsal, RepositorySource, TargetUpgrade
from app.models.finding import (
    MigrationFinding,
    FindingType,
    FindingSeverity,
    FindingStatus,
)
from app.state_machine import RehearsalStateMachine


@pytest.fixture
def app():
    """Return a configured FastAPI test application."""
    return create_app()


@pytest.fixture
def client(app):
    """Return a synchronous TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_repository_source() -> RepositorySource:
    return RepositorySource(
        url="https://github.com/example/demo-app",
        is_demo=False,
    )


@pytest.fixture
def sample_target_upgrade() -> TargetUpgrade:
    return TargetUpgrade(
        package="react",
        from_version="17",
        to_version="18",
        ecosystem="node",
    )


@pytest.fixture
def sample_rehearsal(
    sample_repository_source: RepositorySource,
    sample_target_upgrade: TargetUpgrade,
) -> Rehearsal:
    return Rehearsal(
        repository=sample_repository_source,
        target_upgrade=sample_target_upgrade,
    )


@pytest.fixture
def sample_state_machine(sample_rehearsal: Rehearsal) -> RehearsalStateMachine:
    return RehearsalStateMachine(sample_rehearsal)


@pytest.fixture
def sample_finding() -> MigrationFinding:
    return MigrationFinding(
        type=FindingType.BREAKING_CHANGE,
        severity=FindingSeverity.HIGH,
        title="React 18 root API change",
        reason="ReactDOM.render() is removed in React 18",
        evidence="import ReactDOM from 'react-dom';\nReactDOM.render(<App />, root);",
        required_action="Replace ReactDOM.render() with createRoot().render()",
        affected_files=["src/index.tsx"],
        status=FindingStatus.OPEN,
    )
