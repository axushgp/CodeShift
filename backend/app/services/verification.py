"""
Verification Engine — Session 5.

Runs the applicable repository checks (install, build, test, lint) inside the
Twin workspace after migration, and compares results against the stored baseline.

Reuses the same _run / _has_script / _pm_bin helpers and timeout constants from
baseline.py — they operate on any workspace directory.

Output:  VerificationResult
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from app.models.baseline import BaselineResult, CommandResult, StepStatus, TestRunSummary
from app.models.repository_profile import PackageManager, RepositoryProfile
from app.models.verification import VerificationContext, VerificationResult

# Re-use helpers from the baseline service — they are workspace-agnostic.
from app.services.baseline import (
    TIMEOUT_BUILD,
    TIMEOUT_INSTALL,
    TIMEOUT_LINT,
    TIMEOUT_TEST,
    _find_script_name,
    _has_script,
    _parse_test_summary,
    _pm_bin,
    _run,
    _which,
    resolve_pm_command_prefix,
)

logger = logging.getLogger(__name__)


def _compute_regressions(
    ver: VerificationResult,
    baseline: BaselineResult,
) -> None:
    """
    Compare each step result against the baseline and populate regression fields.
    """
    regressions: list[str] = []
    test_step_already_regressed = False

    for step_name in ("install", "build", "test", "lint"):
        ver_step: Optional[CommandResult] = getattr(ver, step_name)
        base_step: Optional[CommandResult] = getattr(baseline, step_name)

        if ver_step is None or ver_step.status in (
            StepStatus.SKIPPED,
            StepStatus.SKIPPED_NOT_APPLICABLE,
        ):
            continue
        if base_step is None or base_step.status in (
            StepStatus.SKIPPED,
            StepStatus.SKIPPED_NOT_APPLICABLE,
        ):
            # No baseline for this step — treat as a new failure
            if ver_step.status == StepStatus.FAILED:
                regressions.append(f"{step_name}: FAILED (no baseline)")
                if step_name == "test":
                    test_step_already_regressed = True
            continue

        # Both were run — compare
        if base_step.status == StepStatus.PASSED and ver_step.status == StepStatus.FAILED:
            regressions.append(f"{step_name}: regression (was PASSED, now FAILED)")
            if step_name == "test":
                test_step_already_regressed = True

    # Test count regression — only when the test step didn't already register as a full
    # step-level regression (avoids double-counting one failure as two entries).
    if ver.test_summary and baseline.test_summary and not test_step_already_regressed:
        b = baseline.test_summary
        v = ver.test_summary
        if v.failed > b.failed:
            delta = v.failed - b.failed
            regressions.append(
                f"test: {delta} new failure(s) "
                f"({v.passed}/{v.total} passing vs baseline {b.passed}/{b.total})"
            )

    ver.regression_count = len(regressions)
    ver.regression_details = regressions

    if baseline.test_summary:
        ver.baseline_test_total = baseline.test_summary.total
        ver.baseline_test_passed = baseline.test_summary.passed


def run_verification(
    twin_path: Path,
    profile: RepositoryProfile,
    rehearsal_id: str,
    baseline: BaselineResult,
    context: VerificationContext,
    round_num: int = 1,
) -> VerificationResult:
    """
    Run install/build/test/lint inside the Twin and compare against baseline.

    Only modifies the Twin workspace (installs into twin node_modules).
    The original repository is never touched.
    """
    ver = VerificationResult(
        rehearsal_id=rehearsal_id,
        context=context,
        round=round_num,
    )

    pm = profile.package_manager
    pm_display = pm.value if pm != PackageManager.UNKNOWN else "npm"

    prefix, error = resolve_pm_command_prefix(profile)

    # ── Install ───────────────────────────────────────────────────────────────
    if prefix is not None:
        install_cmd = [*prefix, "install"]
        if pm == PackageManager.NPM:
            install_cmd = [*prefix, "install"]
        ver.install = _run(install_cmd, twin_path, TIMEOUT_INSTALL, "install")
    else:
        ver.install = CommandResult(
            step="install",
            command=f"{pm_display} install",
            exit_code=-1,
            stderr=error or f"Package manager '{pm_display}' not found.",
            status=StepStatus.ENVIRONMENT_UNAVAILABLE,
        )

    install_ok = ver.install is not None and ver.install.status == StepStatus.PASSED

    # ── Build, Test, Lint ─────────────────────────────────────────────────────
    steps_config = [
        ("build", TIMEOUT_BUILD),
        ("test", TIMEOUT_TEST),
        ("lint", TIMEOUT_LINT),
    ]

    for step_name, timeout in steps_config:
        script_name = _find_script_name(profile, step_name)

        if not script_name:
            step_result = CommandResult(
                step=step_name,
                command=f"{(prefix and ' '.join(prefix)) or pm_display} run {step_name}",
                exit_code=0,
                stderr=f"No '{step_name}' script found in package.json.",
                status=StepStatus.SKIPPED_NOT_APPLICABLE,
            )
        elif not install_ok:
            step_result = CommandResult(
                step=step_name,
                command=f"{(prefix and ' '.join(prefix)) or pm_display} run {script_name}",
                exit_code=-1,
                stderr="Install step failed or unavailable.",
                status=StepStatus.NOT_RUN,
            )
        else:
            step_result = _run(
                [*prefix, "run", script_name],
                twin_path,
                timeout,
                step_name,
            )
            if step_name == "test" and step_result:
                ver.test_summary = _parse_test_summary(step_result)

        setattr(ver, step_name, step_result)

    ver.compute_passed()
    _compute_regressions(ver, baseline)

    logger.info(
        "Verification[%s] round=%d rehearsal=%s: passed=%s regressions=%d",
        context.value,
        round_num,
        rehearsal_id,
        ver.passed,
        ver.regression_count,
    )
    return ver
