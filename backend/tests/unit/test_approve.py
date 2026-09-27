"""
Unit tests for rehearsal approval endpoint (human review acknowledgement).
"""

from fastapi.testclient import TestClient

from app.models.rehearsal import Rehearsal, RehearsalStage, RehearsalStatus, RepositorySource, TargetUpgrade
from app.services import store


def test_approve_rehearsal_endpoint(client: TestClient) -> None:
    rehearsal = Rehearsal(
        repository=RepositorySource(url="https://github.com/example/repo"),
        target_upgrade=TargetUpgrade(package="react", to_version="18.0.0"),
        status=RehearsalStatus.REQUIRES_HUMAN_REVIEW,
        stage=RehearsalStage.REQUIRES_HUMAN_REVIEW,
    )
    store.save_rehearsal(rehearsal)

    resp = client.post(f"/api/rehearsals/{rehearsal.id}/approve")
    assert resp.status_code == 200
    data = resp.json()
    assert data["rehearsal"]["status"] == "COMPLETE"
    assert data["rehearsal"]["stage"] == "COMPLETE"

    loaded = store.load_rehearsal(rehearsal.id)
    assert loaded is not None
    assert loaded.status == RehearsalStatus.COMPLETE
    assert loaded.stage == RehearsalStage.COMPLETE


def test_approve_nonexistent_rehearsal_404(client: TestClient) -> None:
    resp = client.post("/api/rehearsals/nonexistent-id/approve")
    assert resp.status_code == 404
