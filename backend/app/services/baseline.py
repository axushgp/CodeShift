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

from app.models.baseline import BaselineResult, CommandResult, StepStatus
from app.models.repository_profile import PackageManager, RepositoryProfile

logger = logging.getLogger(__name__)

# Per-step timeouts (seconds).
TIMEOUT_INSTALL = 300  # npm install can be slow
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

    # On Windows, shell=True is needed for npm/yarn/pnpm .cmd wrappers.
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
            status=StepStatus.SKIPPED,
        )


def _has_script(profile: RepositoryProfile, script_name: str) -> bool:
    """Return True if package.json contains a script with the given name."""
    manifest = profile.raw_manifest or {}
    scripts = manifest.get("scripts") or {}
    return script_name in scripts


def run_baseline(
    workspace: Path,
    profile: RepositoryProfile,
    rehearsal_id: str,
) -> BaselineResult:
    """
    Run applicable baseline steps for the repository.

    Steps run only when a relevant script exists in package.json or
    the package manager binary is available.
    """
    result = BaselineResult(rehearsal_id=rehearsal_id)

    pm = profile.package_manager
    pm_bin = _pm_bin(pm)

    # ── Install ──────────────────────────────────────────────────────────────
    # Always attempt install if the package manager binary is available.
    if _which(pm_bin) is not None:
        install_cmd = [pm_bin, "install", "--prefer-offline"] if pm == PackageManager.NPM else [pm_bin, "install"]
        if pm == PackageManager.NPM:
            install_cmd = ["npm", "install", "--prefer-offline"]
        elif pm == PackageManager.YARN:
            install_cmd = ["yarn", "install", "--frozen-lockfile"]
        elif pm == PackageManager.PNPM:
            install_cmd = ["pnpm", "install", "--frozen-lockfile"]
        elif pm == PackageManager.BUN:
            install_cmd = ["bun", "install"]
        result.install = _run(install_cmd, workspace, TIMEOUT_INSTALL, "install")
    else:
        logger.info("Package manager '%s' not available — skipping install", pm_bin)
        result.install = CommandResult(
            step="install",
            command=f"{pm_bin} install",
            exit_code=-1,
            stderr=f"Package manager '{pm_bin}' not found on PATH.",
            status=StepStatus.SKIPPED,
        )

    # Only continue with build/test/lint if install succeeded or was skipped.
    install_ok = result.install is None or result.install.status in (
        StepStatus.PASSED,
        StepStatus.SKIPPED,
    )

    # ── Build ─────────────────────────────────────────────────────────────────
    if install_ok and _has_script(profile, "build") and _which(pm_bin) is not None:
        result.build = _run([pm_bin, "run", "build"], workspace, TIMEOUT_BUILD, "build")
    else:
        if not _has_script(profile, "build"):
            logger.info("No 'build' script found — skipping build")
        result.build = CommandResult(
            step="build",
            command=f"{pm_bin} run build",
            exit_code=0,
            status=StepStatus.SKIPPED,
        )

    # ── Test ──────────────────────────────────────────────────────────────────
    if install_ok and _has_script(profile, "test") and _which(pm_bin) is not None:
        result.test = _run([pm_bin, "run", "test"], workspace, TIMEOUT_TEST, "test")
    else:
        if not _has_script(profile, "test"):
            logger.info("No 'test' script found — skipping test")
        result.test = CommandResult(
            step="test",
            command=f"{pm_bin} run test",
            exit_code=0,
            status=StepStatus.SKIPPED,
        )

    # ── Lint ──────────────────────────────────────────────────────────────────
    if install_ok and _has_script(profile, "lint") and _which(pm_bin) is not None:
        result.lint = _run([pm_bin, "run", "lint"], workspace, TIMEOUT_LINT, "lint")
    else:
        if not _has_script(profile, "lint"):
            logger.info("No 'lint' script found — skipping lint")
        result.lint = CommandResult(
            step="lint",
            command=f"{pm_bin} run lint",
            exit_code=0,
            status=StepStatus.SKIPPED,
        )

    result.compute_passed()
    logger.info(
        "Baseline complete for rehearsal %s: passed=%s", rehearsal_id, result.passed
    )
    return result
