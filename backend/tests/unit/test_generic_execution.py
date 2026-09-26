"""
Unit tests for generic repository intake and baseline execution.

Verifies:
- Package manager determination order (packageManager field -> lockfile -> npm fallback)
- Support for npm, yarn, pnpm, bun
- Package manager availability resolution and Corepack bootstrapping
- Baseline execution without requiring all four scripts (Repository A, B, C)
- Truthful result semantics: PASS, FAIL, SKIPPED_NOT_APPLICABLE, ENVIRONMENT_UNAVAILABLE
"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from app.models.baseline import (
    BaselineResult,
    BaselineStatus,
    CommandResult,
    StepStatus,
)
from app.models.repository_profile import (
    Ecosystem,
    PackageManager,
    RepositoryProfile,
    ScriptInfo,
)
from app.services import baseline as baseline_svc
from app.services import scanner as scanner_svc


# ---------------------------------------------------------------------------
# 1. Scanner Package Manager Detection & Profile Tests
# ---------------------------------------------------------------------------


class TestScannerPackageManagerDetection:
    def test_detect_from_packagemanager_field_yarn(self, tmp_path: Path) -> None:
        pkg = {
            "name": "my-yarn-app",
            "packageManager": "yarn@3.8.0+sha224.9... ",
            "scripts": {"build": "webpack", "test": "jest"},
        }
        (tmp_path / "package.json").write_text(json.dumps(pkg), encoding="utf-8")
        # Even if package-lock exists, packageManager field takes precedence
        (tmp_path / "package-lock.json").write_text("{}", encoding="utf-8")

        profile = scanner_svc.scan_repository(tmp_path, "reh-1")
        assert profile.package_manager == PackageManager.YARN
        assert profile.package_manager_version == "3.8.0"
        assert profile.lockfile == "package-lock.json"
        assert profile.environment_requirements.get("packageManager") == pkg["packageManager"]
        assert "build" in profile.relevant_scripts
        assert "test" in profile.relevant_scripts

    def test_detect_from_packagemanager_field_pnpm(self, tmp_path: Path) -> None:
        pkg = {
            "name": "pnpm-app",
            "packageManager": "pnpm@8.6.0",
            "engines": {"node": ">=18", "pnpm": ">=8"},
        }
        (tmp_path / "package.json").write_text(json.dumps(pkg), encoding="utf-8")

        profile = scanner_svc.scan_repository(tmp_path, "reh-2")
        assert profile.package_manager == PackageManager.PNPM
        assert profile.package_manager_version == "8.6.0"
        assert profile.environment_requirements.get("engines.node") == ">=18"
        assert profile.environment_requirements.get("engines.pnpm") == ">=8"
        assert profile.runtime == "node@>=18"

    def test_detect_from_packagemanager_field_bun(self, tmp_path: Path) -> None:
        pkg = {"name": "bun-app", "packageManager": "bun@1.1.0"}
        (tmp_path / "package.json").write_text(json.dumps(pkg), encoding="utf-8")

        profile = scanner_svc.scan_repository(tmp_path, "reh-bun")
        assert profile.package_manager == PackageManager.BUN
        assert profile.package_manager_version == "1.1.0"

    def test_detect_from_lockfile_yarn(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").write_text(json.dumps({"name": "yarn-app"}), encoding="utf-8")
        (tmp_path / "yarn.lock").write_text("", encoding="utf-8")

        profile = scanner_svc.scan_repository(tmp_path, "reh-3")
        assert profile.package_manager == PackageManager.YARN
        assert profile.lockfile == "yarn.lock"

    def test_detect_from_lockfile_pnpm(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").write_text(json.dumps({"name": "pnpm-app"}), encoding="utf-8")
        (tmp_path / "pnpm-lock.yaml").write_text("", encoding="utf-8")

        profile = scanner_svc.scan_repository(tmp_path, "reh-4")
        assert profile.package_manager == PackageManager.PNPM
        assert profile.lockfile == "pnpm-lock.yaml"

    def test_detect_from_lockfile_bun_lock(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").write_text(json.dumps({"name": "bun-app"}), encoding="utf-8")
        (tmp_path / "bun.lock").write_text("", encoding="utf-8")

        profile = scanner_svc.scan_repository(tmp_path, "reh-5")
        assert profile.package_manager == PackageManager.BUN
        assert profile.lockfile == "bun.lock"

    def test_detect_from_lockfile_bun_lockb(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").write_text(json.dumps({"name": "bun-app"}), encoding="utf-8")
        (tmp_path / "bun.lockb").write_text("", encoding="utf-8")

        profile = scanner_svc.scan_repository(tmp_path, "reh-6")
        assert profile.package_manager == PackageManager.BUN
        assert profile.lockfile == "bun.lockb"

    def test_detect_from_lockfile_npm(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").write_text(json.dumps({"name": "npm-app"}), encoding="utf-8")
        (tmp_path / "package-lock.json").write_text("{}", encoding="utf-8")

        profile = scanner_svc.scan_repository(tmp_path, "reh-7")
        assert profile.package_manager == PackageManager.NPM
        assert profile.lockfile == "package-lock.json"

    def test_fallback_to_npm_when_no_lockfile(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").write_text(json.dumps({"name": "plain-app"}), encoding="utf-8")

        profile = scanner_svc.scan_repository(tmp_path, "reh-8")
        assert profile.package_manager == PackageManager.NPM
        assert profile.lockfile is None


# ---------------------------------------------------------------------------
# 2. Package Manager Availability & Resolution Tests
# ---------------------------------------------------------------------------


class TestPackageManagerAvailability:
    def test_yarn_bootstraps_via_corepack_when_yarn_not_on_path(self) -> None:
        profile = RepositoryProfile(
            rehearsal_id="reh-cp",
            package_manager=PackageManager.YARN,
            package_manager_version="1.22.19",
        )

        with patch("shutil.which") as mock_which:
            mock_which.side_effect = lambda b: "C:\\Node\\corepack.cmd" if b == "corepack" else None

            prefix, error = baseline_svc.resolve_pm_command_prefix(profile)
            assert error is None
            assert prefix == ["corepack", "yarn@1.22.19"]

    def test_pnpm_bootstraps_via_corepack_when_pnpm_not_on_path(self) -> None:
        profile = RepositoryProfile(
            rehearsal_id="reh-pnpm-cp",
            package_manager=PackageManager.PNPM,
            package_manager_version="8.6.0",
        )

        with patch("shutil.which") as mock_which:
            mock_which.side_effect = lambda b: "C:\\Node\\corepack.cmd" if b == "corepack" else None

            prefix, error = baseline_svc.resolve_pm_command_prefix(profile)
            assert error is None
            assert prefix == ["corepack", "pnpm@8.6.0"]

    def test_yarn_falls_back_to_npx_when_corepack_missing(self) -> None:
        profile = RepositoryProfile(
            rehearsal_id="reh-npx",
            package_manager=PackageManager.YARN,
            package_manager_version="1.22.19",
        )

        with patch("shutil.which") as mock_which:
            mock_which.side_effect = lambda b: "C:\\Node\\npx.cmd" if b == "npx" else None

            prefix, error = baseline_svc.resolve_pm_command_prefix(profile)
            assert error is None
            assert prefix == ["npx", "--yes", "yarn@1.22.19"]

    def test_bun_returns_environment_unavailable_when_not_installed(self) -> None:
        profile = RepositoryProfile(
            rehearsal_id="reh-bun-missing",
            package_manager=PackageManager.BUN,
        )

        with patch("shutil.which", return_value=None):
            prefix, error = baseline_svc.resolve_pm_command_prefix(profile)
            assert prefix is None
            assert error is not None
            assert "bun" in error.lower()


# ---------------------------------------------------------------------------
# 3. Baseline Execution & Result Semantics Tests
# ---------------------------------------------------------------------------


class TestBaselineExecutionAndSemantics:
    def test_repository_a_install_build_test(self, tmp_path: Path) -> None:
        """Repository A: has install + build + test (no lint) -> PASS."""
        profile = RepositoryProfile(
            rehearsal_id="reh-a",
            package_manager=PackageManager.NPM,
            raw_manifest={"scripts": {"build": "webpack", "test": "vitest"}},
        )

        def fake_run(cmd, cwd, timeout, step):
            return CommandResult(
                step=step, command=" ".join(cmd), exit_code=0, status=StepStatus.PASSED
            )

        with patch("app.services.baseline._which", return_value="/bin/npm"):
            with patch("app.services.baseline._run", side_effect=fake_run):
                baseline = baseline_svc.run_baseline(tmp_path, profile, "reh-a")

        assert baseline.status == BaselineStatus.PASS
        assert baseline.passed is True
        assert baseline.install.status == StepStatus.PASSED
        assert baseline.build.status == StepStatus.PASSED
        assert baseline.test.status == StepStatus.PASSED
        assert baseline.lint.status == StepStatus.SKIPPED_NOT_APPLICABLE

    def test_repository_b_install_test(self, tmp_path: Path) -> None:
        """Repository B: has install + test (no build, no lint) -> PASS."""
        profile = RepositoryProfile(
            rehearsal_id="reh-b",
            package_manager=PackageManager.NPM,
            raw_manifest={"scripts": {"test": "jest"}},
        )

        def fake_run(cmd, cwd, timeout, step):
            return CommandResult(
                step=step, command=" ".join(cmd), exit_code=0, status=StepStatus.PASSED
            )

        with patch("app.services.baseline._which", return_value="/bin/npm"):
            with patch("app.services.baseline._run", side_effect=fake_run):
                baseline = baseline_svc.run_baseline(tmp_path, profile, "reh-b")

        assert baseline.status == BaselineStatus.PASS
        assert baseline.passed is True
        assert baseline.install.status == StepStatus.PASSED
        assert baseline.test.status == StepStatus.PASSED
        assert baseline.build.status == StepStatus.SKIPPED_NOT_APPLICABLE
        assert baseline.lint.status == StepStatus.SKIPPED_NOT_APPLICABLE

    def test_repository_c_install_build_lint(self, tmp_path: Path) -> None:
        """Repository C: has install + build + lint (no test) -> PASS."""
        profile = RepositoryProfile(
            rehearsal_id="reh-c",
            package_manager=PackageManager.NPM,
            raw_manifest={"scripts": {"build": "tsc", "lint": "eslint ."}},
        )

        def fake_run(cmd, cwd, timeout, step):
            return CommandResult(
                step=step, command=" ".join(cmd), exit_code=0, status=StepStatus.PASSED
            )

        with patch("app.services.baseline._which", return_value="/bin/npm"):
            with patch("app.services.baseline._run", side_effect=fake_run):
                baseline = baseline_svc.run_baseline(tmp_path, profile, "reh-c")

        assert baseline.status == BaselineStatus.PASS
        assert baseline.passed is True
        assert baseline.install.status == StepStatus.PASSED
        assert baseline.build.status == StepStatus.PASSED
        assert baseline.lint.status == StepStatus.PASSED
        assert baseline.test.status == StepStatus.SKIPPED_NOT_APPLICABLE

    def test_baseline_environment_unavailable(self, tmp_path: Path) -> None:
        """When package manager cannot be found or bootstrapped -> ENVIRONMENT_UNAVAILABLE."""
        profile = RepositoryProfile(
            rehearsal_id="reh-unavail",
            package_manager=PackageManager.BUN,
            raw_manifest={"scripts": {"build": "bun build", "test": "bun test"}},
        )

        with patch("app.services.baseline._which", return_value=None):
            baseline = baseline_svc.run_baseline(tmp_path, profile, "reh-unavail")

        assert baseline.status == BaselineStatus.ENVIRONMENT_UNAVAILABLE
        assert baseline.passed is False
        assert baseline.install.status == StepStatus.ENVIRONMENT_UNAVAILABLE
        assert baseline.build.status == StepStatus.ENVIRONMENT_UNAVAILABLE
        assert baseline.test.status == StepStatus.ENVIRONMENT_UNAVAILABLE
        assert baseline.lint.status == StepStatus.SKIPPED_NOT_APPLICABLE
        assert "Environment unavailable" in (baseline.notes or "")

    def test_baseline_step_failure(self, tmp_path: Path) -> None:
        """When an executed script fails -> FAIL."""
        profile = RepositoryProfile(
            rehearsal_id="reh-fail",
            package_manager=PackageManager.NPM,
            raw_manifest={"scripts": {"test": "npm test"}},
        )

        def fake_run(cmd, cwd, timeout, step):
            if step == "install":
                return CommandResult(step=step, command=" ".join(cmd), exit_code=0, status=StepStatus.PASSED)
            return CommandResult(step=step, command=" ".join(cmd), exit_code=1, stderr="1 test failed", status=StepStatus.FAILED)

        with patch("app.services.baseline._which", return_value="/bin/npm"):
            with patch("app.services.baseline._run", side_effect=fake_run):
                baseline = baseline_svc.run_baseline(tmp_path, profile, "reh-fail")

        assert baseline.status == BaselineStatus.FAIL
        assert baseline.passed is False
        assert baseline.install.status == StepStatus.PASSED
        assert baseline.test.status == StepStatus.FAILED
