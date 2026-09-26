"""
Integration tests — FastAPI endpoint tests.

Uses httpx TestClient to exercise the real application stack.
"""

from fastapi.testclient import TestClient


class TestHealthEndpoint:
    def test_health_returns_200(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_structure(self, client: TestClient) -> None:
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"
        assert "app" in data
        assert "version" in data
        assert "environment" in data
        assert "timestamp" in data

    def test_health_app_name(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.json()["app"] == "CodeShift"

    def test_health_content_type(self, client: TestClient) -> None:
        response = client.get("/health")
        assert "application/json" in response.headers["content-type"]

    def test_docs_available(self, client: TestClient) -> None:
        """OpenAPI docs should be reachable (FastAPI default)."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema_available(self, client: TestClient) -> None:
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert schema["info"]["title"] == "CodeShift"


class TestRehearsalsAndAgentPackEndpoints:
    def test_get_nonexistent_rehearsal(self, client: TestClient) -> None:
        response = client.get("/api/rehearsals/nonexistent-id")
        assert response.status_code == 404

    def test_agent_pack_lifecycle(self, client: TestClient, sample_rehearsal) -> None:
        from app.services import store

        store.save_rehearsal(sample_rehearsal)

        # Generate agent pack
        post_resp = client.post(f"/api/rehearsals/{sample_rehearsal.id}/agent-pack")
        assert post_resp.status_code == 200
        data = post_resp.json()
        assert data["rehearsal_id"] == sample_rehearsal.id
        assert "spec" in data
        assert len(data["files"]) == 8

        # Get implementation prompt
        prompt_resp = client.get(
            f"/api/rehearsals/{sample_rehearsal.id}/implementation-prompt"
        )
        assert prompt_resp.status_code == 200
        prompt_data = prompt_resp.json()
        assert "prompt" in prompt_data
        assert "Migrate" in prompt_data["prompt"]

        # Download ZIP
        dl_resp = client.get(
            f"/api/rehearsals/{sample_rehearsal.id}/agent-pack/download"
        )
        assert dl_resp.status_code == 200
        assert dl_resp.headers["content-type"] == "application/zip"
        assert dl_resp.content[:2] == b"PK"

        # Check rehearsal response has agent_task_spec and has_agent_pack
        get_resp = client.get(f"/api/rehearsals/{sample_rehearsal.id}")
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert get_data["has_agent_pack"] is True
        assert get_data["agent_task_spec"] is not None
