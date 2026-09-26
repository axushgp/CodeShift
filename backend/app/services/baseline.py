"""
Baseline Verifier.

Runs the applicable baseline commands (install, build, test, lint) against
the repository in the given workspace. Captures stdout/stderr, exit codes,
and populates a BaselineResult.

Only runs commands that are detectable from package.json scripts/structure.
Uses subprocess timeouts. Does NOT modify the workspace.
"""

from __future__ import annotations

import logging
import platform
import shutil
import subprocess
import time
from pathlib import Path
import os
import signal
from typing import Callable, Optional

from app.models.baseline import (
    BaselineResult,
    BaselineStatus,
    CommandResult,
    StepStatus,
    TestRunSummary,
)
from app.models.repository_profile import PackageManager, RepositoryProfile
from app.services import store

logger = logging.getLogger(__name__)

# Max bytes of output to capture per step to avoid huge payloads.
MAX_OUTPUT_BYTES = 32_768  # 32 KB


def get_baseline_timeout(step: str) -> int:
    """
    Get the execution timeout in seconds for a baseline step (install, build, test, lint).
    Priority:
      1. BASELINE_<STEP>_TIMEOUT environment variable (e.g. BASELINE_INSTALL_TIMEOUT)
      2. CODESHIFT_BASELINE_<STEP>_TIMEOUT / settings.baseline_<step>_timeout
      3. Sensible defaults: INSTALL=180s, BUILD=120s, TEST=120s, LINT=120s
    """
    env_key = f"BASELINE_{step.upper()}_TIMEOUT"
    env_val = os.getenv(env_key)
    if env_val is not None:
        try:
            return max(1, int(env_val))
        except ValueError:
            logger.warning("Invalid value for %s: %s, falling back to config", env_key, env_val)

    try:
        from app.config import get_settings

        settings = get_settings()
        attr_name = f"baseline_{step.lower()}_timeout"
        val = getattr(settings, attr_name, None)
        if val is not None:
            return max(1, int(val))
    except Exception:
        pass

    defaults = {
        "install": 180,
        "build": 120,
        "test": 120,
        "lint": 120,
    }
    return defaults.get(step.lower(), 120)


# Module-level defaults for backward compatibility (e.g. verification.py)
TIMEOUT_INSTALL = get_baseline_timeout("install")
TIMEOUT_BUILD = get_baseline_timeout("build")
TIMEOUT_TEST = get_baseline_timeout("test")
TIMEOUT_LINT = get_baseline_timeout("lint")


def _kill_process_tree(proc: subprocess.Popen) -> None:
    """
    Kill the process and all of its descendants cross-platform.
    On Windows, uses taskkill /F /T /PID to terminate the entire process tree
    (including child Node/npm/cmd processes) so no orphan processes remain.
    On POSIX, uses os.killpg to terminate the process group.
    """
    if proc.poll() is not None:
        return

    pid = proc.pid
    logger.debug("Terminating process tree for PID %s", pid)

    if platform.system() == "Windows":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                capture_output=True,
                check=False,
                timeout=10,
            )
        except Exception as exc:
            logger.warning("taskkill failed for PID %s: %s", pid, exc)
    else:
        try:
            pgid = os.getpgid(pid)
            os.killpg(pgid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        except Exception as exc:
            logger.warning("killpg failed for PID %s: %s", pid, exc)

    try:
        proc.kill()
    except Exception:
        pass
    try:
        proc.wait(timeout=3)
    except Exception:
        pass


def _pm_bin(pm: PackageManager) -> str:
    """Return the CLI binary name for a package manager."""
    mapping = {
        PackageManager.NPM: "npm",
        PackageManager.YARN: "yarn",
        PackageManager.PNPM: "pnpm",
        PackageManager.BUN: "bun",
    }
    return mapping.get(pm, "npm")


def _which(binary: str) -> Optional[str]:
    """Return full path to *binary* if available, else None."""
    return shutil.which(binary)


def resolve_pm_command_prefix(
    profile: RepositoryProfile,
) -> tuple[Optional[list[str]], Optional[str]]:
    """
    Resolve the CLI command prefix to invoke the detected package manager.

    If the detected package manager is not installed directly:
    - Attempt lightweight supported bootstrap (Corepack preferred, npx fallback).
    - Use the package manager version requested by package.json when explicitly specified.
    - If unavailable and cannot be bootstrapped without installing software globally,
      returns (None, error_reason).
    """
    pm = profile.package_manager
    version = profile.package_manager_version

    if pm == PackageManager.NPM:
        if _which("npm") is not None:
            return ["npm"], None
        return None, "npm binary not found on PATH."

    if pm == PackageManager.YARN:
        # Prefer Corepack when yarn binary is missing OR version is explicitly requested
        if _which("corepack") is not None:
            if version:
                return ["corepack", f"yarn@{version}"], None
            return ["corepack", "yarn"], None
        if _which("yarn") is not None:
            return ["yarn"], None
        if _which("npx") is not None:
            spec = f"yarn@{version}" if version else "yarn"
            return ["npx", "--yes", spec], None
        return (
            None,
            f"Package manager 'yarn'{' (' + version + ')' if version else ''} is required, but neither yarn, corepack, nor npx is available.",
        )

    if pm == PackageManager.PNPM:
        # Prefer Corepack when pnpm binary is missing OR version is explicitly requested
        if _which("corepack") is not None:
            if version:
                return ["corepack", f"pnpm@{version}"], None
            return ["corepack", "pnpm"], None
        if _which("pnpm") is not None:
            return ["pnpm"], None
        if _which("npx") is not None:
            spec = f"pnpm@{version}" if version else "pnpm"
            return ["npx", "--yes", spec], None
        return (
            None,
            f"Package manager 'pnpm'{' (' + version + ')' if version else ''} is required, but neither pnpm, corepack, nor npx is available.",
        )

    if pm == PackageManager.BUN:
        if _which("bun") is not None:
            return ["bun"], None
        return None, "Package manager 'bun' is required by repository, but bun is not installed on PATH."

    # Unknown or fallback: default to npm if available
    if _which("npm") is not None:
        return ["npm"], None
    return None, "No supported package manager found on PATH."


def _find_script_name(profile: RepositoryProfile, step_name: str) -> Optional[str]:
    """
    Find the actual script name in package.json for step_name ('build', 'test', 'lint').
    Matches exact name first, then candidate scripts detected by the repository scanner.
    """
    manifest = profile.raw_manifest or {}
    scripts = manifest.get("scripts") or profile.relevant_scripts or {}
    if step_name in scripts:
        return step_name
    if step_name == "build" and profile.build_scripts:
        return profile.build_scripts[0].name
    if step_name == "test" and profile.test_scripts:
        return profile.test_scripts[0].name
    if step_name == "lint" and profile.lint_scripts:
        return profile.lint_scripts[0].name
    return None


def _has_script(profile: RepositoryProfile, script_name: str) -> bool:
    """Return True if package.json contains a script for the given step."""
    return _find_script_name(profile, script_name) is not None


def _parse_test_summary(result: CommandResult) -> Optional[TestRunSummary]:
    """
    Attempt to parse a test summary from combined stdout+stderr.

    Handles common Jest/Vitest patterns:
      Tests: 176 passed, 8 failed, 184 total
      Test Suites: 2 failed, 10 passed, 12 total
    Falls back gracefully to None when not parseable.
    """
    import re

    text = (result.stdout or "") + "\n" + (result.stderr or "")

    m = re.search(
        r"Tests?:.*?(\d+)\s+passed.*?(\d+)\s+failed.*?(\d+)\s+total",
        text,
        re.IGNORECASE,
    )
    if m:
        return TestRunSummary(
            passed=int(m.group(1)),
            failed=int(m.group(2)),
            total=int(m.group(3)),
        )

    m = re.search(r"(\d+)\s+passed.*?(\d+)\s+failed", text, re.IGNORECASE)
    if m:
        passed = int(m.group(1))
        failed = int(m.group(2))
        return TestRunSummary(passed=passed, failed=failed, total=passed + failed)

    m = re.search(r"(\d+)\s+tests?\s+(?:passed|run|complete)", text, re.IGNORECASE)
    if m:
        total = int(m.group(1))
        return TestRunSummary(passed=total, failed=0, total=total)

    return None


def _run(
    cmd: list[str],
    cwd: Path,
    timeout: int,
    step: str,
) -> CommandResult:
    """
    Execute *cmd* in *cwd*, capture output, enforce timeout with full tree termination,
    and return a CommandResult.
    """
    command_str = " ".join(cmd)
    logger.info("Running %s (timeout=%ds): %s", step, timeout, command_str)
    start = time.monotonic()

    # On Windows, shell=True is needed for .cmd wrappers and PATH resolution.
    use_shell = platform.system() == "Windows"

    sub_env = {
        **os.environ,
        "CI": "true",
        "CONTINUOUS_INTEGRATION": "true",
        "DEBIAN_FRONTEND": "noninteractive",
        "npm_config_yes": "true",
        "npm_config_update_notifier": "false",
        "npm_config_audit": "false",
        "npm_config_fund": "false",
        "YARN_ENABLE_IMMUTABLE_INSTALLS": "false",
    }

    proc = None
    timed_out = False
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=use_shell,
            env=sub_env,
            start_new_session=(platform.system() != "Windows"),
        )
        try:
            stdout_data, stderr_data = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            logger.warning(
                "%s timed out after %ds (PID %s), terminating process tree...",
                step,
                timeout,
                proc.pid,
            )
            _kill_process_tree(proc)
            try:
                stdout_data, stderr_data = proc.communicate(timeout=5)
            except Exception:
                stdout_data, stderr_data = "", ""

        duration = time.monotonic() - start
        stdout = (stdout_data or "")[-MAX_OUTPUT_BYTES:]
        stderr = (stderr_data or "")[-MAX_OUTPUT_BYTES:]

        if timed_out:
            timeout_msg = f"Command timed out after {timeout}s."
            stderr = f"{timeout_msg}\n{stderr}".strip() if stderr else timeout_msg
            return CommandResult(
                step=step,
                command=command_str,
                exit_code=-1,
                stdout=stdout,
                stderr=stderr,
                duration_seconds=round(duration, 2),
                status=StepStatus.TIMEOUT,
            )

        status = StepStatus.PASSED if proc.returncode == 0 else StepStatus.FAILED
        logger.info("%s finished: exit=%d duration=%.1fs", step, proc.returncode, duration)
        return CommandResult(
            step=step,
            command=command_str,
            exit_code=proc.returncode,
            stdout=stdout,
            stderr=stderr,
            duration_seconds=round(duration, 2),
            status=status,
        )
    except FileNotFoundError as exc:
        duration = time.monotonic() - start
        logger.warning("%s binary not found: %s", step, exc)
        return CommandResult(
            step=step,
            command=command_str,
            exit_code=-1,
            stdout="",
            stderr=f"Command not found: {cmd[0]}",
            duration_seconds=round(duration, 2),
            status=StepStatus.ENVIRONMENT_UNAVAILABLE,
        )
    except Exception as exc:
        duration = time.monotonic() - start
        logger.exception("Error executing %s (%s)", step, command_str)
        if proc is not None:
            _kill_process_tree(proc)
        return CommandResult(
            step=step,
            command=command_str,
            exit_code=-1,
            stdout="",
            stderr=f"Execution error: {exc}",
            duration_seconds=round(duration, 2),
            status=StepStatus.FAILED,
        )


def run_baseline(
    workspace: Path,
    profile: RepositoryProfile,
    rehearsal_id: str,
    on_step_start: Optional[Callable[[str, str], None]] = None,
) -> BaselineResult:
    """
    Run applicable baseline steps for the repository.

    Steps run according to detected package manager and available package.json scripts.
    Distinguishes clearly between PASS, FAIL, TIMEOUT, SKIPPED_NOT_APPLICABLE, and ENVIRONMENT_UNAVAILABLE.
    Persists progress incrementally and terminates entire process trees on timeout.
    """
    result = BaselineResult(rehearsal_id=rehearsal_id)
    pm = profile.package_manager
    pm_display = pm.value if pm != PackageManager.UNKNOWN else "npm"

    prefix, error = resolve_pm_command_prefix(profile)

    # ── Package manager unavailable in environment ───────────────────────────
    if prefix is None:
        reason = error or f"Package manager '{pm_display}' not available in environment."
        logger.warning("Baseline unavailable for %s: %s", rehearsal_id, reason)
        result.install = CommandResult(
            step="install",
            command=f"{pm_display} install",
            exit_code=-1,
            stderr=reason,
            status=StepStatus.ENVIRONMENT_UNAVAILABLE,
        )
        for step in ("build", "test", "lint"):
            script_name = _find_script_name(profile, step)
            if script_name:
                cmd_res = CommandResult(
                    step=step,
                    command=f"{pm_display} run {script_name}",
                    exit_code=-1,
                    stderr=reason,
                    status=StepStatus.ENVIRONMENT_UNAVAILABLE,
                )
            else:
                cmd_res = CommandResult(
                    step=step,
                    command=f"{pm_display} run {step}",
                    exit_code=0,
                    stderr=f"No '{step}' script found in package.json.",
                    status=StepStatus.SKIPPED_NOT_APPLICABLE,
                )
            setattr(result, step, cmd_res)

        result.status = BaselineStatus.ENVIRONMENT_UNAVAILABLE
        result.passed = False
        result.notes = f"Environment unavailable: {reason}"
        store.save_baseline(result)
        return result

    # ── Install ──────────────────────────────────────────────────────────────
    install_timeout = get_baseline_timeout("install")
    install_cmd = [*prefix, "install"]
    if pm == PackageManager.NPM:
        install_cmd = [*prefix, "install", "--prefer-offline", "--no-audit", "--no-fund"]

    result.active_step = "install"
    store.save_baseline(result)
    if on_step_start:
        on_step_start("install", f"Installing dependencies with {pm_display}...")

    result.install = _run(install_cmd, workspace, install_timeout, "install")
    store.save_baseline(result)

    install_ok = result.install.status == StepStatus.PASSED

    # If install timed out or had environment issue, stop immediately
    if result.install.status == StepStatus.TIMEOUT:
        result.status = BaselineStatus.TIMEOUT
        result.passed = False
        result.notes = f"Install step timed out after {install_timeout}s. Subsequent steps were not run."
        result.active_step = None
        store.save_baseline(result)
        return result

    if result.install.status == StepStatus.ENVIRONMENT_UNAVAILABLE:
        result.status = BaselineStatus.ENVIRONMENT_UNAVAILABLE
        result.passed = False
        result.notes = f"Environment error during install: {result.install.stderr}"
        result.active_step = None
        store.save_baseline(result)
        return result

    # ── Build, Test, Lint ─────────────────────────────────────────────────────
    steps_config = [
        ("build", "Building repository"),
        ("test", "Running tests"),
        ("lint", "Linting repository"),
    ]

    for step_name, step_desc in steps_config:
        script_name = _find_script_name(profile, step_name)
        timeout = get_baseline_timeout(step_name)

        if not script_name:
            logger.info("No '%s' script found — marked as not applicable", step_name)
            step_result = CommandResult(
                step=step_name,
                command=f"{' '.join(prefix)} run {step_name}",
                exit_code=0,
                stderr=f"No '{step_name}' script found in package.json.",
                status=StepStatus.SKIPPED_NOT_APPLICABLE,
            )
            setattr(result, step_name, step_result)
            store.save_baseline(result)
        elif not install_ok:
            logger.info("Install failed — not running '%s' script", step_name)
            step_result = CommandResult(
                step=step_name,
                command=f"{' '.join(prefix)} run {script_name}",
                exit_code=-1,
                stderr="Install step failed. Dependent step was not run.",
                status=StepStatus.NOT_RUN,
            )
            setattr(result, step_name, step_result)
            store.save_baseline(result)
        else:
            result.active_step = step_name
            store.save_baseline(result)
            if on_step_start:
                on_step_start(step_name, f"{step_desc} ({script_name})...")

            step_result = _run(
                [*prefix, "run", script_name],
                workspace,
                timeout,
                step_name,
            )
            if step_name == "test" and step_result:
                result.test_summary = _parse_test_summary(step_result)

            setattr(result, step_name, step_result)
            store.save_baseline(result)

    result.active_step = None
    result.compute_passed()
    if not install_ok:
        result.notes = "Install step failed. Subsequent steps were not run."

    store.save_baseline(result)
    logger.info(
        "Baseline complete for rehearsal %s: status=%s passed=%s",
        rehearsal_id,
        result.status,
        result.passed,
    )
    return result
