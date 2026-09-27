"""
Unit tests for Quick Start default demo catalog and endpoints.
"""

from fastapi.testclient import TestClient

from app.models.demo import DemoManifest
from app.services import demos as demos_svc
from app.services import store


class TestDemoCatalog:
    def test_catalog_has_three_default_demos(self) -> None:
        demos = demos_svc.get_all_demos()
        assert len(demos) == 3
        ids = [d.id for d in demos]
        assert "howtotax" in ids
        assert "datocms-plugin-iframe-tab" in ids
        assert "game-rock-paper-scissors" in ids

    def test_demo_manifest_fields_and_urls(self) -> None:
        expected_urls = {
            "howtotax": "https://github.com/taepras/howtotax",
            "datocms-plugin-iframe-tab": "https://github.com/thebuilder/datocms-plugin-iframe-tab",
            "game-rock-paper-scissors": "https://github.com/masajid390/game-rock-paper-scissors",
        }
        demos = demos_svc.get_all_demos()
        for demo in demos:
            assert isinstance(demo, DemoManifest)
            assert demo.id in expected_urls
            assert demo.repository_url == expected_urls[demo.id]
            assert demo.name
            assert demo.description is not None

    def test_get_demo_by_id(self) -> None:
        demo = demos_svc.get_demo_by_id("howtotax")
        assert demo is not None
        assert demo.name == "HowToTax"
        assert demo.repository_url == "https://github.com/taepras/howtotax"

        rps_demo = demos_svc.get_demo_by_id("game-rock-paper-scissors")
        assert rps_demo is not None
        assert rps_demo.name == "Rock Paper Scissors"
        assert rps_demo.repository_url == "https://github.com/masajid390/game-rock-paper-scissors"

        nonexistent = demos_svc.get_demo_by_id("does-not-exist")
        assert nonexistent is None


class TestDemoEndpoints:
    def test_list_demos(self, client: TestClient) -> None:
        resp = client.get("/api/demos")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3
        urls = [d["repository_url"] for d in data]
        assert "https://github.com/taepras/howtotax" in urls
        assert "https://github.com/thebuilder/datocms-plugin-iframe-tab" in urls
        assert "https://github.com/masajid390/game-rock-paper-scissors" in urls

    def test_get_demo_by_id(self, client: TestClient) -> None:
        resp = client.get("/api/demos/datocms-plugin-iframe-tab")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "datocms-plugin-iframe-tab"
        assert data["repository_url"] == "https://github.com/thebuilder/datocms-plugin-iframe-tab"
        assert data["package"] == "react"

    def test_get_demo_not_found(self, client: TestClient) -> None:
        resp = client.get("/api/demos/not-real")
        assert resp.status_code == 404

    def test_launch_demo_rehearsal_creates_new_run_each_time(
        self, client: TestClient, monkeypatch
    ) -> None:
        called = []

        def fake_run_intake(rehearsal_id, source_url, zip_bytes):
            called.append((rehearsal_id, source_url))

        monkeypatch.setattr("app.api.demos._run_intake_pipeline", fake_run_intake)

        # Launch run 1
        resp1 = client.post("/api/demos/howtotax/launch")
        assert resp1.status_code == 202
        id1 = resp1.json()["rehearsal"]["id"]

        # Launch run 2
        resp2 = client.post("/api/demos/howtotax/launch")
        assert resp2.status_code == 202
        id2 = resp2.json()["rehearsal"]["id"]

        # Confirm fresh rehearsal is created each time (no reuse)
        assert id1 != id2
        assert len(called) == 2
        assert called[0] == (id1, "https://github.com/taepras/howtotax")
        assert called[1] == (id2, "https://github.com/taepras/howtotax")

        r1 = store.load_rehearsal(id1)
        assert r1 is not None
        assert r1.repository.url == "https://github.com/taepras/howtotax"
        assert r1.repository.is_demo is True
        assert r1.target_upgrade.package == "react"
        assert r1.target_upgrade.from_version == "17.0.2"
        assert r1.target_upgrade.to_version == "18.0.0"

    def test_launch_game_rock_paper_scissors_demo(
        self, client: TestClient, monkeypatch
    ) -> None:
        called = []

        def fake_run_intake(rehearsal_id, source_url, zip_bytes):
            called.append((rehearsal_id, source_url))

        monkeypatch.setattr("app.api.demos._run_intake_pipeline", fake_run_intake)

        resp = client.post("/api/demos/game-rock-paper-scissors/launch")
        assert resp.status_code == 202
        r_id = resp.json()["rehearsal"]["id"]
        assert len(called) == 1
        assert called[0] == (r_id, "https://github.com/masajid390/game-rock-paper-scissors")

        rehearsal = store.load_rehearsal(r_id)
        assert rehearsal is not None
        assert rehearsal.repository.url == "https://github.com/masajid390/game-rock-paper-scissors"
        assert rehearsal.repository.is_demo is True

