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
from typing import Optional

from app.models.baseline import (
    BaselineResult,
    BaselineStatus,
    CommandResult,
    StepStatus,
    TestRunSummary,
)
from app.models.repository_profile import PackageManager, RepositoryProfile

logger = logging.getLogger(__name__)

# Per-step timeouts (seconds).
TIMEOUT_INSTALL = 300  # install can be slow
TIMEOUT_BUILD = 180
TIMEOUT_TEST = 180
TIMEOUT_LINT = 60

# Max bytes of output to capture per step to avoid huge payloads.
MAX_OUTPUT_BYTES = 32_768  # 32 KB


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
    Execute *cmd* in *cwd*, capture output, and return a CommandResult.
    """
    command_str = " ".join(cmd)
    logger.info("Running %s: %s", step, command_str)
    start = time.monotonic()

    # On Windows, shell=True is needed for .cmd wrappers and PATH resolution.
    use_shell = platform.system() == "Windows"

    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=use_shell,
        )
        duration = time.monotonic() - start
        stdout = result.stdout[-MAX_OUTPUT_BYTES:] if result.stdout else ""
        stderr = result.stderr[-MAX_OUTPUT_BYTES:] if result.stderr else ""
        status = StepStatus.PASSED if result.returncode == 0 else StepStatus.FAILED
        logger.info("%s finished: exit=%d duration=%.1fs", step, result.returncode, duration)
        return CommandResult(
            step=step,
            command=command_str,
            exit_code=result.returncode,
            stdout=stdout,
            stderr=stderr,
            duration_seconds=round(duration, 2),
            status=status,
        )
    except subprocess.TimeoutExpired:
        duration = time.monotonic() - start
        logger.warning("%s timed out after %ds", step, timeout)
        return CommandResult(
            step=step,
            command=command_str,
            exit_code=-1,
            stdout="",
            stderr=f"Command timed out after {timeout}s.",
            duration_seconds=round(duration, 2),
            status=StepStatus.FAILED,
        )
    except FileNotFoundError as exc:
        logger.warning("%s binary not found: %s", step, exc)
        return CommandResult(
            step=step,
            command=command_str,
            exit_code=-1,
            stdout="",
            stderr=f"Command not found: {cmd[0]}",
            duration_seconds=0.0,
            status=StepStatus.ENVIRONMENT_UNAVAILABLE,
        )


def run_baseline(
    workspace: Path,
    profile: RepositoryProfile,
    rehearsal_id: str,
) -> BaselineResult:
    """
    Run applicable baseline steps for the repository.

    Steps run according to detected package manager and available package.json scripts.
    Distinguishes clearly between PASS, FAIL, SKIPPED_NOT_APPLICABLE, and ENVIRONMENT_UNAVAILABLE.
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
        return result

    # ── Install ──────────────────────────────────────────────────────────────
    install_cmd = [*prefix, "install"]
    if pm == PackageManager.NPM:
        install_cmd = [*prefix, "install", "--prefer-offline"]

    result.install = _run(install_cmd, workspace, TIMEOUT_INSTALL, "install")
    install_ok = result.install.status == StepStatus.PASSED

    # ── Build, Test, Lint ─────────────────────────────────────────────────────
    steps_config = [
        ("build", TIMEOUT_BUILD),
        ("test", TIMEOUT_TEST),
        ("lint", TIMEOUT_LINT),
    ]

    for step_name, timeout in steps_config:
        script_name = _find_script_name(profile, step_name)

        if not script_name:
            logger.info("No '%s' script found — marked as not applicable", step_name)
            step_result = CommandResult(
                step=step_name,
                command=f"{' '.join(prefix)} run {step_name}",
                exit_code=0,
                stderr=f"No '{step_name}' script found in package.json.",
                status=StepStatus.SKIPPED_NOT_APPLICABLE,
            )
        elif not install_ok:
            logger.info("Install failed — not running '%s' script", step_name)
            step_result = CommandResult(
                step=step_name,
                command=f"{' '.join(prefix)} run {script_name}",
                exit_code=-1,
                stderr="Install step failed. Dependent step was not run.",
                status=StepStatus.NOT_RUN,
            )
        else:
            step_result = _run(
                [*prefix, "run", script_name],
                workspace,
                timeout,
                step_name,
            )
            if step_name == "test" and step_result:
                result.test_summary = _parse_test_summary(step_result)

        setattr(result, step_name, step_result)

    result.compute_passed()
    if not install_ok:
        result.notes = "Install step failed. Subsequent steps were not run."

    logger.info(
        "Baseline complete for rehearsal %s: status=%s passed=%s",
        rehearsal_id,
        result.status,
        result.passed,
    )
    return result
