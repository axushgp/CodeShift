"""
Unit tests for Target Discovery Service and Migrations API.
"""

from pathlib import Path
from fastapi.testclient import TestClient

from app.models.repository_profile import Ecosystem, PackageManager, RepositoryProfile, SourceStructure
from app.services import target_discovery as discovery_svc


class TestTargetDiscovery:
    def test_react_17_detection_and_target_options(self) -> None:
        profile = RepositoryProfile(
            rehearsal_id="test-react-17",
            name="my-react-app",
            ecosystem=Ecosystem.NODE,
            framework="react",
            runtime="node@20.10.0",
            package_manager=PackageManager.YARN,
            dependencies={"react": "^17.0.2", "react-dom": "^17.0.2"},
            dev_dependencies={"vite": "^3.0.0"},
            structure=SourceStructure(),
        )

        res = discovery_svc.discover_migration_targets(profile)

        # Framework detection
        assert res["detected_framework"]["id"] == "react"
        assert res["detected_framework"]["name"] == "React"
        assert res["detected_version"] == "17.0.2"

        # Tooling detection
        assert res["tooling"]["build_tool"] == "Vite"
        assert "yarn" in res["tooling"]["package_manager"].lower()

        # Upgrade targets
        upgrade = res["upgrade_target"]
        assert upgrade["has_certified_recipe"] is True
        assert upgrade["recommended_target"] == "18.0.0"

        options = upgrade["options"]
        assert len(options) >= 2
        rec_opt = next(o for o in options if o["is_recommended"])
        assert "18" in rec_opt["target_version"]
        assert rec_opt["has_certified_recipe"] is True
        assert rec_opt["recipe"] == "react_17_to_18"

    def test_vue_framework_detection_ai_assisted(self) -> None:
        profile = RepositoryProfile(
            rehearsal_id="test-vue-2",
            name="my-vue-app",
            ecosystem=Ecosystem.NODE,
            framework="vue",
            package_manager=PackageManager.NPM,
            dependencies={"vue": "~2.6.14"},
            structure=SourceStructure(),
        )

        res = discovery_svc.discover_migration_targets(profile)
        assert res["detected_framework"]["id"] == "vue"
        assert res["detected_version"] == "2.6.14"

        upgrade = res["upgrade_target"]
        assert upgrade["has_certified_recipe"] is False
        rec_opt = next(o for o in upgrade["options"] if o["is_recommended"])
        assert "3" in rec_opt["target_version"]
        assert rec_opt["has_certified_recipe"] is False

    def test_unknown_framework_does_not_crash(self) -> None:
        profile = RepositoryProfile(
            rehearsal_id="test-unknown",
            name="plain-js-app",
            ecosystem=Ecosystem.NODE,
            framework=None,
            package_manager=PackageManager.NPM,
            dependencies={"lodash": "^4.17.21"},
            structure=SourceStructure(),
        )

        res = discovery_svc.discover_migration_targets(profile)
        assert res["detected_framework"]["id"] == "unknown"
        upgrade = res["upgrade_target"]
        assert upgrade["has_certified_recipe"] is False
        assert len(upgrade["options"]) >= 1


class TestMigrationsApi:
    def test_get_options_by_framework(self, client: TestClient) -> None:
        resp = client.get("/api/migrations/options?framework=react&version=17.0.2")
        assert resp.status_code == 200
        data = resp.json()
        assert data["detected_framework"]["id"] == "react"
        assert data["upgrade_target"]["has_certified_recipe"] is True
        assert data["upgrade_target"]["recommended_target"] == "18.0.0"

    def test_get_options_missing_params(self, client: TestClient) -> None:
        resp = client.get("/api/migrations/options")
        assert resp.status_code == 400

    def test_discover_missing_url(self, client: TestClient) -> None:
        resp = client.post("/api/migrations/discover", json={})
        assert resp.status_code == 400
