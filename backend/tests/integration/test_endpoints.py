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
