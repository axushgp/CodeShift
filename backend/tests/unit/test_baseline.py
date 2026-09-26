"""
Unit tests for Baseline Execution, Timeouts, Process Cleanup, and State Transitions.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.models.baseline import (
    BaselineResult,
    BaselineStatus,
    CommandResult,
    StepStatus,
)
from app.models.repository_profile import PackageManager, RepositoryProfile
from app.services import baseline as baseline_svc
from app.services.baseline import (
    _kill_process_tree,
    _run,
    get_baseline_timeout,
    run_baseline,
)


class TestBaselineTimeoutsAndConfig:
    def test_default_timeouts(self):
        """Sensible defaults: INSTALL=180s, BUILD=120s, TEST=120s, LINT=120s."""
        with patch.dict(os.environ, {}, clear=True):
            assert get_baseline_timeout("install") == 180
            assert get_baseline_timeout("build") == 120
            assert get_baseline_timeout("test") == 120
            assert get_baseline_timeout("lint") == 120

    def test_environment_variable_override(self):
        """Environment variables BASELINE_<STEP>_TIMEOUT must override defaults."""
        custom_env = {
            "BASELINE_INSTALL_TIMEOUT": "240",
            "BASELINE_BUILD_TIMEOUT": "90",
            "BASELINE_TEST_TIMEOUT": "45",
            "BASELINE_LINT_TIMEOUT": "30",
        }
        with patch.dict(os.environ, custom_env, clear=False):
            assert get_baseline_timeout("install") == 240
            assert get_baseline_timeout("build") == 90
            assert get_baseline_timeout("test") == 45
            assert get_baseline_timeout("lint") == 30


class TestCommandExecutionAndProcessCleanup:
    def test_successful_command(self, tmp_path: Path):
        """Command completes with code 0 -> PASSED with duration and stdout."""
        cmd = ["node", "-e", "console.log('success output')"]
        result = _run(cmd, tmp_path, timeout=10, step="test")

        assert result.status == StepStatus.PASSED
        assert result.exit_code == 0
        assert "success output" in result.stdout
        assert result.duration_seconds is not None
        assert result.duration_seconds >= 0.0

    def test_command_failure_reports_failed_not_timeout(self, tmp_path: Path):
        """Command exiting with non-zero code is reported as FAILED, not TIMEOUT."""
        cmd = ["node", "-e", "console.error('error message'); process.exit(2)"]
        result = _run(cmd, tmp_path, timeout=10, step="test")

        assert result.status == StepStatus.FAILED
        assert result.exit_code == 2
        assert "error message" in result.stderr

    def test_command_timeout_and_process_cleanup(self, tmp_path: Path):
        """Command exceeding timeout triggers _kill_process_tree and returns TIMEOUT status."""
        mock_proc = MagicMock()
        mock_proc.pid = 99999
        mock_proc.poll.return_value = None
        mock_proc.communicate.side_effect = [
            subprocess.TimeoutExpired(cmd=["test"], timeout=1),
            ("partial stdout", "partial stderr"),
        ]

        with patch("subprocess.Popen", return_value=mock_proc):
            with patch("app.services.baseline._kill_process_tree") as mock_kill:
                result = _run(["long", "running"], tmp_path, timeout=1, step="test")

                # Verify _kill_process_tree was called on the Popen object
                mock_kill.assert_called_once_with(mock_proc)
                assert result.status == StepStatus.TIMEOUT
                assert result.exit_code == -1
                assert "Command timed out after 1s." in result.stderr

    def test_kill_process_tree_windows(self):
        """On Windows, _kill_process_tree invokes taskkill /F /T /PID."""
        mock_proc = MagicMock()
        mock_proc.pid = 12345
        mock_proc.poll.return_value = None

        with patch("platform.system", return_value="Windows"):
            with patch("subprocess.run") as mock_subrun:
                _kill_process_tree(mock_proc)
                mock_subrun.assert_called_once_with(
                    ["taskkill", "/F", "/T", "/PID", "12345"],
                    capture_output=True,
                    check=False,
                    timeout=10,
                )
                mock_proc.kill.assert_called_once()


class TestBaselineStateTransitionsAndCallbacks:
    def test_active_step_and_progress_callback(self, tmp_path: Path):
        """run_baseline invokes on_step_start and persists active_step at each phase."""
        profile = RepositoryProfile(
            rehearsal_id="reh-progress",
            package_manager=PackageManager.NPM,
            raw_manifest={"scripts": {"build": "build-cmd", "test": "test-cmd"}},
        )

        steps_called = []

        def on_step(step_name: str, desc: str):
            steps_called.append((step_name, desc))

        def fake_run(cmd, cwd, timeout, step):
            return CommandResult(
                step=step,
                command=" ".join(cmd),
                exit_code=0,
                status=StepStatus.PASSED,
                duration_seconds=0.1,
            )

        with patch("app.services.baseline._which", return_value="/bin/npm"):
            with patch("app.services.baseline._run", side_effect=fake_run):
                baseline = run_baseline(
                    tmp_path,
                    profile,
                    "reh-progress",
                    on_step_start=on_step,
                )

        assert baseline.status == BaselineStatus.PASS
        assert baseline.passed is True
        assert baseline.active_step is None  # Idle upon completion

        # Verify all steps were reported in order
        step_names = [s[0] for s in steps_called]
        assert step_names == ["install", "build", "test"]

    def test_baseline_timeout_stops_subsequent_steps(self, tmp_path: Path):
        """If install times out, subsequent steps are not run and baseline status is TIMEOUT."""
        profile = RepositoryProfile(
            rehearsal_id="reh-timeout",
            package_manager=PackageManager.NPM,
            raw_manifest={"scripts": {"build": "build-cmd", "test": "test-cmd"}},
        )

        def fake_run(cmd, cwd, timeout, step):
            if step == "install":
                return CommandResult(
                    step=step,
                    command=" ".join(cmd),
                    exit_code=-1,
                    stderr=f"Command timed out after {timeout}s.",
                    status=StepStatus.TIMEOUT,
                    duration_seconds=float(timeout),
                )
            return CommandResult(step=step, command=" ".join(cmd), exit_code=0, status=StepStatus.PASSED)

        with patch("app.services.baseline._which", return_value="/bin/npm"):
            with patch("app.services.baseline._run", side_effect=fake_run):
                baseline = run_baseline(tmp_path, profile, "reh-timeout")

        assert baseline.status == BaselineStatus.TIMEOUT
        assert baseline.passed is False
        assert baseline.install.status == StepStatus.TIMEOUT
        assert "timed out" in (baseline.notes or "")
        # Build and test were not executed
        assert baseline.build is None
        assert baseline.test is None
