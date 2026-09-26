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
    _has_script,
    _pm_bin,
    _run,
    _which,
)

logger = logging.getLogger(__name__)


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

    # Jest style: "Tests: N passed, M failed, T total"
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

    # Vitest style: "✓ N | × M" or "N passed | M failed"
    m = re.search(r"(\d+)\s+passed.*?(\d+)\s+failed", text, re.IGNORECASE)
    if m:
        passed = int(m.group(1))
        failed = int(m.group(2))
        return TestRunSummary(passed=passed, failed=failed, total=passed + failed)

    # Minimal: just total from "N tests"
    m = re.search(r"(\d+)\s+tests?\s+(?:passed|run|complete)", text, re.IGNORECASE)
    if m:
        total = int(m.group(1))
        return TestRunSummary(passed=total, failed=0, total=total)

    return None


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

        if ver_step is None or ver_step.status == StepStatus.SKIPPED:
            continue
        if base_step is None or base_step.status == StepStatus.SKIPPED:
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
    pm_bin = _pm_bin(pm)

    # ── Install ───────────────────────────────────────────────────────────────
    if _which(pm_bin) is not None:
        install_cmd = ["npm", "install"] if pm == PackageManager.NPM else [pm_bin, "install"]
        ver.install = _run(install_cmd, twin_path, TIMEOUT_INSTALL, "install")
    else:
        ver.install = CommandResult(
            step="install",
            command=f"{pm_bin} install",
            exit_code=-1,
            stderr=f"Package manager '{pm_bin}' not found.",
            status=StepStatus.SKIPPED,
        )

    install_ok = ver.install is None or ver.install.status in (
        StepStatus.PASSED,
        StepStatus.SKIPPED,
    )

    # ── Build ─────────────────────────────────────────────────────────────────
    if install_ok and _has_script(profile, "build") and _which(pm_bin) is not None:
        ver.build = _run([pm_bin, "run", "build"], twin_path, TIMEOUT_BUILD, "build")
    else:
        ver.build = CommandResult(
            step="build",
            command=f"{pm_bin} run build",
            exit_code=0,
            status=StepStatus.SKIPPED,
        )

    # ── Test ──────────────────────────────────────────────────────────────────
    if install_ok and _has_script(profile, "test") and _which(pm_bin) is not None:
        ver.test = _run([pm_bin, "run", "test"], twin_path, TIMEOUT_TEST, "test")
        if ver.test:
            ver.test_summary = _parse_test_summary(ver.test)
    else:
        ver.test = CommandResult(
            step="test",
            command=f"{pm_bin} run test",
            exit_code=0,
            status=StepStatus.SKIPPED,
        )

    # ── Lint ──────────────────────────────────────────────────────────────────
    if install_ok and _has_script(profile, "lint") and _which(pm_bin) is not None:
        ver.lint = _run([pm_bin, "run", "lint"], twin_path, TIMEOUT_LINT, "lint")
    else:
        ver.lint = CommandResult(
            step="lint",
            command=f"{pm_bin} run lint",
            exit_code=0,
            status=StepStatus.SKIPPED,
        )

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
