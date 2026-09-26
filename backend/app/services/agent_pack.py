"""
Agent Pack Service — Priority 1 & 2.

Generates the canonical AgentTaskSpec and packages the migration artifacts into:
    CodeShift-Agent-Pack/
    ├── agent_task.json
    ├── implementation-prompt.md
    ├── AGENTS.md
    ├── migration-plan.md
    ├── findings.json
    ├── verification.md
    ├── patch.diff
    └── README.md
"""

from __future__ import annotations

import io
import json
import logging
import zipfile
from pathlib import Path
from typing import Optional

from app.config import get_settings
from app.models.agent_task import (
    AgentTaskSpec,
    ImplementationStep,
    RepositoryContext,
    TaskDetails,
    VerificationSummary,
)
from app.models.baseline import BaselineResult
from app.models.finding import FindingStatus, MigrationFinding
from app.models.migration_plan import MigrationPlan
from app.models.rehearsal import Rehearsal
from app.models.repository_profile import RepositoryProfile
from app.models.twin import TwinResult
from app.models.verification_run import VerificationRun

logger = logging.getLogger(__name__)


def build_agent_task_spec(
    rehearsal: Rehearsal,
    profile: Optional[RepositoryProfile],
    baseline: Optional[BaselineResult],
    plan: Optional[MigrationPlan],
    twin: Optional[TwinResult],
    ver_run: Optional[VerificationRun],
) -> AgentTaskSpec:
    """Build the canonical machine-readable AgentTaskSpec from existing rehearsal data."""
    # Determine overall status
    if ver_run and ver_run.passed:
        overall_status = "VERIFIED"
    elif ver_run and ver_run.requires_human_review:
        overall_status = "REQUIRES_HUMAN_REVIEW"
    elif twin and twin.migration_status.value == "SUCCESS":
        overall_status = "PROPOSED"
    else:
        overall_status = "REQUIRES_HUMAN_REVIEW"

    # Task details
    summary_parts = []
    if plan:
        summary_parts.append(
            f"Upgrade {plan.package} {plan.from_version or ''} -> {plan.to_version}."
        )
    if twin and twin.changed_files:
        summary_parts.append(f"{len(twin.changed_files)} file(s) modified in Twin rehearsal.")
    if ver_run:
        summary_parts.append(
            ver_run.summary or f"Verification status: {overall_status}."
        )

    task = TaskDetails(
        package=rehearsal.target_upgrade.package,
        from_version=rehearsal.target_upgrade.from_version,
        to_version=rehearsal.target_upgrade.to_version,
        status=overall_status,
        summary=" ".join(summary_parts) or "Migration rehearsal handoff.",
    )

    # Repository context
    repository = RepositoryContext(
        name=profile.name if profile else "repository",
        ecosystem=profile.ecosystem.value if profile else "node",
        runtime=profile.runtime if profile else None,
        framework=profile.framework if profile else None,
        package_manager=profile.package_manager.value if profile else "npm",
        source_url=rehearsal.repository.url,
    )

    # Findings - preserve verified / requires_human_review / proposed
    findings: list[MigrationFinding] = []
    if plan and plan.findings:
        for f in plan.findings:
            f_copy = f.model_copy()
            if overall_status == "VERIFIED" and f.status != FindingStatus.REQUIRES_HUMAN_REVIEW:
                f_copy.status = FindingStatus.VERIFIED
            findings.append(f_copy)

    # Implementation steps
    steps: list[ImplementationStep] = []
    step_num = 1

    if plan and plan.planned_actions:
        for action in plan.planned_actions:
            step_status = "PROPOSED"
            if twin and action.id in twin.actions_applied:
                step_status = "VERIFIED" if overall_status == "VERIFIED" else "PROPOSED"
            elif twin and action.id in twin.actions_skipped:
                step_status = "REQUIRES_HUMAN_REVIEW"

            steps.append(
                ImplementationStep(
                    step_number=step_num,
                    action_type=action.action_type.value,
                    description=action.description,
                    target_files=action.target_files,
                    status=step_status,
                    notes=action.command,
                )
            )
            step_num += 1

    # Files to modify
    files_to_modify: list[str] = []
    if twin and twin.changed_files:
        files_to_modify = [cf.path for cf in twin.changed_files]
    elif plan:
        for a in plan.planned_actions:
            for tf in a.target_files:
                if tf not in files_to_modify:
                    files_to_modify.append(tf)

    # Files not to modify
    files_not_to_modify: list[str] = [
        ".git",
        "node_modules",
        "README.md",
    ]

    # Constraints
    constraints = [
        "Never perform broad uncontrolled rewrites; keep changes strictly minimal and targeted.",
        "Ensure peer dependencies align with the target package version.",
        "Verify changes against existing test suites before committing.",
        "Any manual review items must be resolved by a developer or explicit human confirmation.",
    ]

    # Verification summary
    ver_details: list[str] = []
    baseline_passed = baseline.passed if baseline else False
    final_ver_passed = ver_run.passed if ver_run else False
    reg_count = ver_run.verification.regression_count if (ver_run and ver_run.verification) else 0

    if baseline and baseline.test_summary:
        ver_details.append(
            f"Baseline tests: {baseline.test_summary.passed}/{baseline.test_summary.total} passing."
        )
    if ver_run and ver_run.verification and ver_run.verification.test_summary:
        vts = ver_run.verification.test_summary
        ver_details.append(
            f"Final verification tests: {vts.passed}/{vts.total} passing."
        )
    if ver_run and ver_run.summary:
        ver_details.append(ver_run.summary)

    verification = VerificationSummary(
        baseline_passed=baseline_passed,
        final_verification_passed=final_ver_passed,
        regressions_count=reg_count,
        status=overall_status,
        details=ver_details,
    )

    # Acceptance criteria
    acceptance_criteria = [
        f"Package '{rehearsal.target_upgrade.package}' updated to target version '{rehearsal.target_upgrade.to_version}' in package.json.",
        "Deprecated API calls safely migrated to replacement methods.",
        "Repository builds cleanly and test suite passes without regressions.",
    ]
    if twin and twin.manual_items:
        acceptance_criteria.append(
            f"Address {len(twin.manual_items)} manual review item(s) identified during rehearsal."
        )

    return AgentTaskSpec(
        rehearsal_id=rehearsal.id,
        task=task,
        repository=repository,
        findings=findings,
        implementation_plan=steps,
        constraints=constraints,
        files_to_modify=files_to_modify,
        files_not_to_modify=files_not_to_modify,
        verification=verification,
        acceptance_criteria=acceptance_criteria,
    )


def generate_agent_pack_files(
    spec: AgentTaskSpec,
    plan: Optional[MigrationPlan],
    twin: Optional[TwinResult],
    ver_run: Optional[VerificationRun],
) -> dict[str, str]:
    """Generate the 8 canonical files for CodeShift-Agent-Pack/."""
    pkg = spec.task.package
    target_ver = spec.task.to_version
    from_ver = spec.task.from_version or "previous"
    diff_text = (twin.git_diff or "").strip() if twin else ""

    # 1. agent_task.json
    agent_task_json = spec.model_dump_json(indent=2)

    # 2. implementation-prompt.md
    mod_files_str = "\n".join(f"- `{f}`" for f in spec.files_to_modify) or "- (None identified)"
    steps_str = "\n".join(
        f"{s.step_number}. **[{s.action_type}]** {s.description} ({s.status})"
        for s in spec.implementation_plan
    ) or "1. Apply target upgrade."

    crit_str = "\n".join(f"- [ ] {ac}" for ac in spec.acceptance_criteria)

    prompt_md = f"""# Implementation Task: Migrate {pkg} to {target_ver}

You are an expert coding agent. Your task is to apply a verified migration upgrade on this repository from **{pkg} {from_ver}** to **{pkg} {target_ver}**.

## Summary & Status
- **Target Upgrade**: `{pkg}` -> `{target_ver}`
- **Rehearsal Outcome**: **{spec.task.status}**
- **Regressions**: {spec.verification.regressions_count} detected

## Files to Modify
{mod_files_str}

## Implementation Plan
{steps_str}

## Constraints
- Apply only targeted, minimal changes. Do not reformat unrelated files.
- Preserve all existing functionality and ensure the test suite passes.
- Do not modify: {", ".join(spec.files_not_to_modify)}.

## Acceptance Criteria
{crit_str}

## Rehearsed Patch
When available, review `patch.diff` in this pack for the verified changes rehearsed by CodeShift.
"""

    # 3. AGENTS.md
    agents_md = f"""# Agent Instructions for CodeShift Migration

## Purpose
This document guides AI coding agents (Claude Code, Cursor, Copilot, Codex, etc.) executing the migration specified in `agent_task.json`.

## Guidelines
1. **Source of Truth**: Read `agent_task.json` and `migration-plan.md` first.
2. **Deterministic Changes**: Inspect `patch.diff` for pre-verified diffs. Apply the version bumps and codemods exactly as specified.
3. **Targeted Edits**: Only modify files listed in `files_to_modify`.
4. **Verification**: Run the test and lint scripts detected for this repository (`npm test`, `npm run build`).
5. **Human Review**: Check `findings.json` for any items marked `REQUIRES_HUMAN_REVIEW`.
"""

    # 4. migration-plan.md
    findings_rows = []
    for f in spec.findings:
        findings_rows.append(
            f"| {f.severity.value} | {f.type.value} | {f.title} | {f.status.value} |"
        )
    findings_table = (
        "| Severity | Type | Title | Status |\n|---|---|---|---|\n" + "\n".join(findings_rows)
        if findings_rows
        else "No findings recorded."
    )

    migration_plan_md = f"""# Migration Plan: {pkg} {from_ver} -> {target_ver}

## Overview
- **Package**: `{pkg}`
- **From Version**: `{from_ver}`
- **To Version**: `{target_ver}`
- **Overall Status**: **{spec.task.status}**

## Findings
{findings_table}

## Planned Actions
{steps_str}

## Notes
{plan.notes if plan and plan.notes else "Migration plan generated by CodeShift rehearsal."}
"""

    # 5. findings.json
    findings_json = json.dumps([f.model_dump(mode="json") for f in spec.findings], indent=2)

    # 6. verification.md
    ver_details_str = "\n".join(f"- {d}" for d in spec.verification.details) or "- No verification details."
    unresolved_items: list[str] = []
    if twin and twin.manual_items:
        unresolved_items.extend(twin.manual_items)
    if ver_run and ver_run.verification and ver_run.verification.regression_details:
        for reg in ver_run.verification.regression_details:
            if reg not in unresolved_items:
                unresolved_items.append(f"Regression: {reg}")
    if ver_run and ver_run.diagnoses:
        for d in ver_run.diagnoses:
            if d.requires_human_review and not d.repair_applied:
                diag_item = f"Diagnosis [{d.step}]: {d.root_cause}"
                if diag_item not in unresolved_items:
                    unresolved_items.append(diag_item)

    unresolved_str = (
        "\n".join(f"- {item}" for item in unresolved_items)
        if unresolved_items
        else "- None. All items automated or verified."
    )

    ver_md = f"""# Migration Verification Report

## Status: {spec.verification.status}

### Baseline Comparison
- **Baseline Passed**: {'Yes' if spec.verification.baseline_passed else 'No'}
- **Post-Migration Verification Passed**: {'Yes' if spec.verification.final_verification_passed else 'No'}
- **Active Regressions**: {spec.verification.regressions_count}

### Details
{ver_details_str}

### Unresolved Human Review Items
{unresolved_str}
"""

    # 7. patch.diff
    patch_diff = diff_text if diff_text else "# No diff generated or clean workspace.\n"

    # 8. README.md
    readme_md = f"""# CodeShift Agent Pack: {pkg} -> {target_ver}

This package contains the complete handoff specification for migrating **{pkg}** to **{target_ver}**, generated after a full rehearsal in a disposable Twin.

## Contents
- `agent_task.json` — Machine-readable task specification.
- `implementation-prompt.md` — Copy-paste prompt for AI coding agents.
- `AGENTS.md` — Agent behavioral rules and constraints.
- `migration-plan.md` — Detailed migration findings and actions.
- `findings.json` — Raw migration findings.
- `verification.md` — Verification runs, baseline diff, and test results.
- `patch.diff` — Verified unified diff produced inside the Twin.
"""

    return {
        "agent_task.json": agent_task_json,
        "implementation-prompt.md": prompt_md,
        "AGENTS.md": agents_md,
        "migration-plan.md": migration_plan_md,
        "findings.json": findings_json,
        "verification.md": ver_md,
        "patch.diff": patch_diff,
        "README.md": readme_md,
    }


def save_agent_pack(rehearsal_id: str, pack_files: dict[str, str]) -> Path:
    """Save all pack files to data/rehearsals/{id}/agent_pack/."""
    settings = get_settings()
    pack_dir = Path(settings.data_dir) / "rehearsals" / rehearsal_id / "agent_pack"
    pack_dir.mkdir(parents=True, exist_ok=True)

    for filename, content in pack_files.items():
        (pack_dir / filename).write_text(content, encoding="utf-8")

    logger.info("Saved %d Agent Pack files to %s", len(pack_files), pack_dir)
    return pack_dir


def create_agent_pack_zip_bytes(pack_files: dict[str, str]) -> bytes:
    """Create a ZIP archive in memory containing CodeShift-Agent-Pack/."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, content in pack_files.items():
            arcname = f"CodeShift-Agent-Pack/{filename}"
            zf.writestr(arcname, content.encode("utf-8"))
    return buf.getvalue()
