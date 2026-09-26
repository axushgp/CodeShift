"""
Unit tests for Quick Start demo manifest and endpoints.
"""

from fastapi.testclient import TestClient

from app.models.demo import DemoManifest
from app.services import demos as demos_svc
from app.services import store


class TestDemoCatalog:
    def test_catalog_has_three_demos(self) -> None:
        demos = demos_svc.get_all_demos()
        assert len(demos) == 3
        ids = [d.id for d in demos]
        assert "datocms-plugin-iframe-tab" in ids
        assert "vite-react-17-template" in ids
        assert "vite-react17-tailwind" in ids

    def test_demo_manifest_fields(self) -> None:
        demos = demos_svc.get_all_demos()
        for demo in demos:
            assert isinstance(demo, DemoManifest)
            assert demo.id
            assert demo.name
            assert demo.repository_url.startswith("https://github.com/")
            assert demo.description
            assert demo.package == "react"
            assert demo.source_version.startswith("17.")
            assert demo.target_version.startswith("18.")

    def test_get_demo_by_id(self) -> None:
        demo = demos_svc.get_demo_by_id("vite-react-17-template")
        assert demo is not None
        assert demo.name == "Vite React 17 Starter"

        nonexistent = demos_svc.get_demo_by_id("does-not-exist")
        assert nonexistent is None


class TestDemoEndpoints:
    def test_list_demos(self, client: TestClient) -> None:
        resp = client.get("/api/demos")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3
        ids = [d["id"] for d in data]
        assert "datocms-plugin-iframe-tab" in ids

    def test_get_demo_by_id(self, client: TestClient) -> None:
        resp = client.get("/api/demos/datocms-plugin-iframe-tab")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "datocms-plugin-iframe-tab"
        assert data["package"] == "react"

    def test_get_demo_not_found(self, client: TestClient) -> None:
        resp = client.get("/api/demos/not-real")
        assert resp.status_code == 404

    def test_launch_demo_rehearsal(self, client: TestClient, monkeypatch) -> None:
        called = []

        def fake_run_intake(rehearsal_id, source_url, zip_bytes):
            called.append((rehearsal_id, source_url))

        monkeypatch.setattr("app.api.demos._run_intake_pipeline", fake_run_intake)

        resp = client.post("/api/demos/vite-react-17-template/launch")
        assert resp.status_code == 202
        data = resp.json()
        assert "rehearsal" in data
        rehearsal_id = data["rehearsal"]["id"]

        rehearsal = store.load_rehearsal(rehearsal_id)
        assert rehearsal is not None
        assert rehearsal.repository.is_demo is True
        assert rehearsal.target_upgrade.package == "react"
        assert rehearsal.target_upgrade.to_version == "18.0.0"
        assert len(called) == 1
        assert called[0][0] == rehearsal_id

