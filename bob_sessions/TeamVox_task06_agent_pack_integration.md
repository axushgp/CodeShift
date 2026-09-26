# # Final Session - Agent Pack + End-to-End Integration

This is the final implementation session for CodeShift-Final v1.0.

First inspect the existing implementation from Sessions 1-5 and read `architecture.md`.

Use the existing architecture and code.
Do not redesign or refactor unrelated parts.

## OBJECTIVE

Finish the existing CodeShift product so the already-built pipeline works end-to-end:

Repository
→ Scan
→ Baseline
→ Migration Analysis
→ Twin
→ Migration
→ Verification
→ Diagnosis / Repair
→ Final Result
→ AgentTaskSpec
→ Agent Pack

Focus ONLY on completing missing integration and handoff functionality.

## 1. AgentTaskSpec

Create the minimum canonical machine-readable AgentTaskSpec from the existing rehearsal data.

It must include:

- task
- repository
- findings
- implementation_plan
- constraints
- files_to_modify
- files_not_to_modify
- verification
- acceptance_criteria

Preserve existing statuses:

- VERIFIED
- PROPOSED
- REQUIRES_HUMAN_REVIEW

Do not duplicate data unnecessarily.
The AgentTaskSpec is the source of truth for the generated pack.

## 2. Agent Pack

Generate:

CodeShift-Agent-Pack/
├── agent_task.json
├── implementation-prompt.md
├── AGENTS.md
├── migration-plan.md
├── findings.json
├── verification.md
├── patch.diff
└── README.md

Use the existing migration, diagnosis, repair, verification, and diff data.

The implementation prompt must be directly usable by another coding agent.

The verification file must clearly show the final verification result and unresolved human-review items.

The patch file should contain the existing Twin diff when available.

## 3. Minimal API

Add only the minimum endpoint(s) required to:

- generate the Agent Pack for a completed rehearsal
- download the generated pack

Reuse the existing filesystem persistence.

Do not add a database, queue, or new service architecture.

## 4. Final Frontend Integration

Use the existing frontend.

Make the full existing backend workflow usable from the UI.

Only add what is necessary to:

- trigger the stages already implemented
- show important migration findings
- show verification/final status
- provide `Copy Implementation Prompt`
- provide `Download Agent Pack`

Do NOT redesign the UI.

## 5. End-to-End Wiring

Check the existing rehearsal/state flow and fix only the integration gaps preventing:

Repository
→ Baseline
→ Analyze
→ Twin/Migrate
→ Verify
→ Diagnose/Repair
→ Final state
→ Agent Pack

from working coherently.

Do not reimplement working services.

Do not change the architecture.

## 6. Demo Reliability

Ensure there is a simple reliable way to demonstrate the completed flow using the existing React 17 → React 18 scenario.

If a Demo Mode already exists, make sure it works.

If it does not exist, create only the smallest possible deterministic demo path required to exercise the existing workflow.

Do not introduce new infrastructure.

## IMPORTANT CONSTRAINTS

Do NOT implement:

- new migration intelligence
- new Watsonx features
- new AST system
- new verification algorithms
- new repair strategies
- multi-language support
- authentication
- GitHub OAuth
- RAG/vector database
- additional LLMs
- databases
- microservices
- major UI redesign
- large test suites
- extensive documentation
- speculative abstractions

Do not refactor unrelated Sessions 1-5 code.

Do not replace working implementations.

Reuse what already exists.

## EFFICIENCY

This is the final integration task.

Prioritize working product functionality over polish.

Make the smallest changes necessary.

Do not add libraries unless absolutely required.

Do not create tests or documentation beyond what is directly required for the Agent Pack output.

Run only the minimum checks needed to catch integration/build/runtime regressions.

If an existing component already works, leave it alone.

## COMPLETION

The session is complete when the existing CodeShift implementation can demonstrate:

repository
→ scan
→ baseline
→ migration analysis
→ Twin
→ migration
→ verification
→ diagnosis/repair
→ final status
→ AgentTaskSpec
→ CodeShift-Agent-Pack

and the UI exposes:

Copy Implementation Prompt
Download Agent Pack

Fix any integration issues necessary for this flow.

Then STOP.

Do not add new features after the end-to-end flow works.

---

**Status:** error  **Date:** 2026-09-26

---

### 👤 User

# Final Session - Agent Pack + End-to-End Integration

This is the final implementation session for CodeShift-Final v1.0.

First inspect the existing implementation from Sessions 1-5 and read `architecture.md`.

Use the existing architecture and code.
Do not redesign or refactor unrelated parts.

## OBJECTIVE

Finish the existing CodeShift product so the already-built pipeline works end-to-end:

Repository
→ Scan
→ Baseline
→ Migration Analysis
→ Twin
→ Migration
→ Verification
→ Diagnosis / Repair
→ Final Result
→ AgentTaskSpec
→ Agent Pack

Focus ONLY on completing missing integration and handoff functionality.

## 1. AgentTaskSpec

Create the minimum canonical machine-readable AgentTaskSpec from the existing rehearsal data.

It must include:

- task
- repository
- findings
- implementation_plan
- constraints
- files_to_modify
- files_not_to_modify
- verification
- acceptance_criteria

Preserve existing statuses:

- VERIFIED
- PROPOSED
- REQUIRES_HUMAN_REVIEW

Do not duplicate data unnecessarily.
The AgentTaskSpec is the source of truth for the generated pack.

## 2. Agent Pack

Generate:

CodeShift-Agent-Pack/
├── agent_task.json
├── implementation-prompt.md
├── AGENTS.md
├── migration-plan.md
├── findings.json
├── verification.md
├── patch.diff
└── README.md

Use the existing migration, diagnosis, repair, verification, and diff data.

The implementation prompt must be directly usable by another coding agent.

The verification file must clearly show the final verification result and unresolved human-review items.

The patch file should contain the existing Twin diff when available.

## 3. Minimal API

Add only the minimum endpoint(s) required to:

- generate the Agent Pack for a completed rehearsal
- download the generated pack

Reuse the existing filesystem persistence.

Do not add a database, queue, or new service architecture.

## 4. Final Frontend Integration

Use the existing frontend.

Make the full existing backend workflow usable from the UI.

Only add what is necessary to:

- trigger the stages already implemented
- show important migration findings
- show verification/final status
- provide `Copy Implementation Prompt`
- provide `Download Agent Pack`

Do NOT redesign the UI.

## 5. End-to-End Wiring

Check the existing rehearsal/state flow and fix only the integration gaps preventing:

Repository
→ Baseline
→ Analyze
→ Twin/Migrate
→ Verify
→ Diagnose/Repair
→ Final state
→ Agent Pack

from working coherently.

Do not reimplement working services.

Do not change the architecture.

## 6. Demo Reliability

Ensure there is a simple reliable way to demonstrate the completed flow using the existing React 17 → React 18 scenario.

If a Demo Mode already exists, make sure it works.

If it does not exist, create only the smallest possible deterministic demo path required to exercise the existing workflow.

Do not introduce new infrastructure.

## IMPORTANT CONSTRAINTS

Do NOT implement:

- new migration intelligence
- new Watsonx features
- new AST system
- new verification algorithms
- new repair strategies
- multi-language support
- authentication
- GitHub OAuth
- RAG/vector database
- additional LLMs
- databases
- microservices
- major UI redesign
- large test suites
- extensive documentation
- speculative abstractions

Do not refactor unrelated Sessions 1-5 code.

Do not replace working implementations.

Reuse what already exists.

## EFFICIENCY

This is the final integration task.

Prioritize working product functionality over polish.

Make the smallest changes necessary.

Do not add libraries unless absolutely required.

Do not create tests or documentation beyond what is directly required for the Agent Pack output.

Run only the minimum checks needed to catch integration/build/runtime regressions.

If an existing component already works, leave it alone.

## COMPLETION

The session is complete when the existing CodeShift implementation can demonstrate:

repository
→ scan
→ baseline
→ migration analysis
→ Twin
→ migration
→ verification
→ diagnosis/repair
→ final status
→ AgentTaskSpec
→ CodeShift-Agent-Pack

and the UI exposes:

Copy Implementation Prompt
Download Agent Pack

Fix any integration issues necessary for this flow.

Then STOP.

Do not add new features after the end-to-end flow works.

---

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[-] Inspect existing codebase: read architecture.md and explore Sessions 1-5 implementation
[ ] Understand current state: identify integration gaps
[ ] Implement AgentTaskSpec model and generation logic
[ ] Implement Agent Pack generation (files + ZIP)
[ ] Add minimal API endpoints (generate + download pack)
[ ] Wire frontend: trigger stages, show findings/status, Copy Prompt, Download Pack
[ ] Fix end-to-end integration gaps in rehearsal state flow
[ ] Add/verify Demo Mode for React 17→18 scenario
[ ] Run validation checks


### 🤖 Assistant

> 🔧 called: read_file, list_files

Let me start by reading the architecture and exploring the existing implementation.

> 🔧 **list_files** — .

> 🔧 **read_file** — architecture.md

### 🤖 Assistant

> 🔧 called: read_file, list_files



> 🔧 **read_file** — architecture.md

> 🔧 **list_files** — backend

### 🤖 Assistant

> 🔧 called: read_file, list_files



> 🔧 **read_file** — architecture.md

> 🔧 **list_files** — backend/app

### 🤖 Assistant

> 🔧 called: read_file, read_file

Now let me read the key existing files to understand what's already implemented:

> 🔧 **read_file** — backend/app/main.py

> 🔧 **read_file** — backend/app/api/rehearsals.py

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — backend/app/api/rehearsals.py

> 🔧 **read_file** — backend/app/models/__init__.py

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — backend/app/api/rehearsals.py

> 🔧 **read_file** — backend/app/services/store.py

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — backend/app/api/rehearsals.py

> 🔧 **read_file** — backend/app/models/rehearsal.py

### 🤖 Assistant

> 🔧 called: read_file, read_file

Now let me read the remaining key service and model files:

> 🔧 **read_file** — backend/app/models/verification_run.py

> 🔧 **read_file** — backend/app/models/finding.py

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — backend/app/models/migration_plan.py

> 🔧 **read_file** — backend/app/models/twin.py

### 🤖 Assistant

> 🔧 called: list_files, read_file

Now let me look at the frontend:

> 🔧 **list_files** — frontend/src

> 🔧 **read_file** — frontend/src/App.tsx

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — frontend/src/types/index.ts

> 🔧 **read_file** — frontend/src/api/client.ts

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — backend/app/services/migration.py

> 🔧 **read_file** — backend/app/config.py

### 🤖 Assistant

> 🔧 called: read_file, read_file

Now let me check the architecture for Demo Mode section and read the migration knowledge:

> 🔧 **read_file** — architecture.md

> 🔧 **read_file** — backend/app/migration_knowledge/node/react_17_to_18.json

### 🤖 Assistant

> 🔧 called: read_file, read_file

Now I have a comprehensive picture. Let me look at the remaining services for context:

> 🔧 **read_file** — backend/app/services/watsonx_client.py

> 🔧 **read_file** — frontend/src/components/RehearsalForm.tsx

### 🤖 Assistant

> 🔧 called: read_file, read_file

Now I have a thorough understanding of the existing implementation. Let me also quickly check the diagnosis, repair, and verification services:

> 🔧 **read_file** — backend/app/services/diagnosis.py

> 🔧 **read_file** — backend/app/services/verification.py

### 🤖 Assistant

> 🔧 called: update_todo_list

I now have enough context. Let me plan and implement:

1. **AgentTaskSpec model** (backend model)
2. **Agent Pack generation service** 
3. **Demo Mode** (deterministic, no Watsonx needed)
4. **New API endpoints** (generate + download pack)
5. **Frontend integration** (analyze/migrate/verify triggers, findings panel, Copy Prompt, Download Pack)
6. **Wire `RehearsalResponse`** to include missing fields (migration_plan, twin_result, verification_run) in types

> 🔧 **update_todo_list** — 
[x] Inspect existing codebase: read architecture.md and explore Sessions 1-5 implementation
[-] Understand current state: identify integration gaps
[ ] Implement AgentTaskSpec model and generation logic
[ ] Implement Agent Pack generation (files + ZIP)
[ ] Add minimal API endpoints (generate + download pack)
[ ] Wire frontend: trigger stages, show findings/status, Copy Prompt, Download Pack
[ ] Fix end-to-end integration gaps in rehearsal state flow
[ ] Add/verify Demo Mode for React 17→18 scenario
[ ] Run validation checks


### 🤖 Assistant

> 🔧 called: update_todo_list

**Key integration gaps identified:**

1. **Frontend `RehearsalResponse` type** - missing `migration_plan`, `twin_result`, `verification_run` - frontend can't show them
2. **Frontend** - no buttons/UI for `analyze`, `migrate`, `verify` stages - workflow is stuck at baseline  
3. **Frontend** - no findings panel, no verification panel, no Copy/Download buttons
4. **Backend** - no `AgentTaskSpec` model  
5. **Backend** - no Agent Pack generation service
6. **Backend** - no `/agent-pack` endpoint (generate + download)
7. **Backend** - no Demo Mode (deterministic path bypassing Watsonx)
8. **Backend** - `_run_verify_pipeline` leaves stage as `MIGRATING/COMPLETE` instead of properly transitioning after migration completes (line 176-180 says `MIGRATING` stage but status `COMPLETE` - so UI can't know when to trigger verify)

Let me now implement everything:

> 🔧 **update_todo_list** — 
[x] Inspect existing codebase: read architecture.md and explore Sessions 1-5 implementation
[x] Understand current state: identify integration gaps
[-] Implement AgentTaskSpec model and generation logic
[ ] Implement Agent Pack generation service (files + ZIP)
[ ] Add minimal API endpoints (generate + download pack + demo)
[ ] Fix end-to-end integration gaps (stage transitions, demo mode in analyze)
[ ] Wire frontend types + API client (add missing types + calls)
[ ] Wire frontend UI (stage workflow buttons, findings, verification, Copy/Download)
[ ] Run validation checks


### 🤖 Assistant

> 🔧 called: write_file



> 🔧 **write_file** — backend/app/models/agent_task_spec.py

### 🤖 Assistant

> 🔧 called: write_file

Now create the Agent Pack generation service:

> 🔧 **write_file** — """
Agent Pack generation service — Session 6.

Builds an AgentTaskSpec from completed rehearsal data, then generates
the full CodeShift-Agent-Pack directory and a ZIP archive.

Pack layout:
  CodeShift-Agent-Pack/
  ├── agent_task.json
  ├── implementation-prompt.md
  ├── AGENTS.md
  ├── migration-plan.md
  ├── findings.json
  ├── verification.md
  ├── patch.diff
  └── README.md

No new infrastructure — reads existing persisted JSON files via the store.
"""

from __future__ import annotations

import io
import json
import logging
import zipfile
from pathlib import Path
from typing import Optional

from app.models.agent_task_spec import (
    AcceptanceCriterion,
    AgentTaskSpec,
    AgentVerification,
    OverallOutcome,
)
from app.models.baseline import BaselineResult
from app.models.finding import FindingStatus, MigrationFinding
from app.models.migration_plan import MigrationPlan
from app.models.rehearsal import Rehearsal, RehearsalStatus
from app.models.repository_profile import RepositoryProfile
from app.models.twin import TwinResult
from app.models.verification_run import VerificationRun

logger = logging.getLogger(__name__)


class AgentPackError(Exception):
    """Raised when an Agent Pack cannot be generated."""


# ── AgentTaskSpec builder ─────────────────────────────────────────────────────

def build_agent_task_spec(
    rehearsal: Rehearsal,
    profile: Optional[RepositoryProfile],
    baseline: Optional[BaselineResult],
    plan: Optional[MigrationPlan],
    twin: Optional[TwinResult],
    verification_run: Optional[VerificationRun],
) -> AgentTaskSpec:
    """Assemble an AgentTaskSpec from the rehearsal pipeline outputs."""

    target = rehearsal.target_upgrade

    # ── task ─────────────────────────────────────────────────────────────────
    task = {
        "description": (
            f"Upgrade {target.package} from "
            f"{target.from_version or 'current'} to {target.to_version}."
        ),
        "package": target.package,
        "from_version": target.from_version,
        "to_version": target.to_version,
        "rehearsal_status": rehearsal.status.value,
    }

    # ── repository ────────────────────────────────────────────────────────────
    repository: dict = {
        "url": rehearsal.repository.url,
        "is_demo": rehearsal.repository.is_demo,
    }
    if profile:
        repository.update(
            {
                "name": profile.name,
                "ecosystem": profile.ecosystem.value if hasattr(profile.ecosystem, "value") else profile.ecosystem,
                "framework": profile.framework,
                "runtime": profile.runtime,
                "package_manager": profile.package_manager.value if hasattr(profile.package_manager, "value") else profile.package_manager,
            }
        )

    # ── findings ──────────────────────────────────────────────────────────────
    findings: list[MigrationFinding] = plan.findings if plan else []

    # Update statuses from verification results
    if verification_run and verification_run.passed:
        for f in findings:
            if f.status == FindingStatus.PROPOSED:
                f.status = FindingStatus.VERIFIED
    elif verification_run and verification_run.requires_human_review:
        # Mark anything unresolved as REQUIRES_HUMAN_REVIEW
        for f in findings:
            if f.status == FindingStatus.PROPOSED:
                f.status = FindingStatus.REQUIRES_HUMAN_REVIEW

    # ── implementation_plan ────────────────────────────────────────────────────
    impl_plan = []
    if plan:
        for action in plan.planned_actions:
            impl_plan.append(
                {
                    "id": action.id,
                    "action_type": action.action_type.value
                    if hasattr(action.action_type, "value")
                    else action.action_type,
                    "description": action.description,
                    "target_files": action.target_files,
                    "command": action.command,
                }
            )

    # ── files_to_modify / files_not_to_modify ─────────────────────────────────
    files_to_modify: list[str] = []
    if twin:
        files_to_modify = [cf.path for cf in twin.changed_files]
    if not files_to_modify and plan:
        # Fall back to planned action targets
        for action in plan.planned_actions:
            files_to_modify.extend(action.target_files)
    files_to_modify = sorted(set(files_to_modify))

    files_not_to_modify: list[str] = []
    if twin:
        files_not_to_modify.append(twin.twin_path)  # never touch the original
    # Always protect lockfile-adjacent paths
    if profile:
        if profile.lockfile:
            files_not_to_modify.append(profile.lockfile)

    # ── constraints ────────────────────────────────────────────────────────────
    constraints: list[str] = [
        "Do not modify the original repository during implementation.",
        f"Target: {target.package} {target.to_version}",
        "Run the full test suite after each significant change.",
        "Do not introduce unrelated refactors — only migration-required changes.",
    ]
    if plan and plan.knowledge_sources:
        constraints.append(
            "Follow official migration guide: " + "; ".join(plan.knowledge_sources)
        )

    # ── verification summary ───────────────────────────────────────────────────
    outcome = _determine_outcome(rehearsal, verification_run)
    regressions_found = 0
    regressions_resolved = 0
    unresolved = 0
    ver_summary = None
    human_review_items: list[str] = []

    if verification_run:
        ver_summary = verification_run.summary
        regressions_found = verification_run.verification.regression_count or 0
        if verification_run.passed:
            regressions_resolved = regressions_found
        else:
            unresolved = regressions_found
        for d in verification_run.diagnoses:
            if d.requires_human_review:
                human_review_items.append(
                    f"{d.step}: {d.root_cause}"
                )

    verification = AgentVerification(
        outcome=outcome,
        rounds=verification_run.round if verification_run else 0,
        regressions_found=regressions_found,
        regressions_resolved=regressions_resolved,
        unresolved_regressions=unresolved,
        summary=ver_summary,
        human_review_items=human_review_items,
    )

    # ── acceptance_criteria ────────────────────────────────────────────────────
    criteria = _build_acceptance_criteria(
        target, baseline, verification_run, findings
    )

    # ── patch diff ────────────────────────────────────────────────────────────
    patch_diff = twin.git_diff if twin else None

    return AgentTaskSpec(
        rehearsal_id=rehearsal.id,
        task=task,
        repository=repository,
        findings=findings,
        implementation_plan=impl_plan,
        constraints=constraints,
        files_to_modify=files_to_modify,
        files_not_to_modify=files_not_to_modify,
        verification=verification,
        acceptance_criteria=criteria,
        patch_diff=patch_diff,
        watsonx_model=plan.watsonx_model if plan else None,
        knowledge_sources=plan.knowledge_sources if plan else [],
    )


def _determine_outcome(
    rehearsal: Rehearsal,
    verification_run: Optional[VerificationRun],
) -> OverallOutcome:
    if rehearsal.status == RehearsalStatus.REQUIRES_HUMAN_REVIEW:
        return OverallOutcome.REQUIRES_HUMAN_REVIEW
    if rehearsal.status == RehearsalStatus.COMPLETE:
        if verification_run and verification_run.passed:
            return OverallOutcome.VERIFIED
        return OverallOutcome.PROPOSED
    return OverallOutcome.PROPOSED


def _build_acceptance_criteria(
    target,
    baseline: Optional[BaselineResult],
    verification_run: Optional[VerificationRun],
    findings: list[MigrationFinding],
) -> list[AcceptanceCriterion]:
    criteria = []

    # Criterion: package version updated
    criteria.append(
        AcceptanceCriterion(
            id="ac-version-bump",
            description=f"{target.package} updated to {target.to_version} in package.json",
            status=FindingStatus.PROPOSED.value,
        )
    )

    # Criterion: all critical findings resolved
    critical = [f for f in findings if f.severity.value == "CRITICAL" if hasattr(f.severity, "value")]
    if not critical:
        critical = [f for f in findings if getattr(f.severity, "value", f.severity) == "CRITICAL"]
    for f in critical:
        status = f.status.value if hasattr(f.status, "value") else str(f.status)
        criteria.append(
            AcceptanceCriterion(
                id=f"ac-finding-{f.id[:8]}",
                description=f"Resolved: {f.title}",
                status=status,
            )
        )

    # Criterion: tests passing (compared to baseline)
    if baseline and verification_run:
        base_summary = None
        if baseline.test and baseline.test.test_summary:
            base_summary = baseline.test.test_summary

        if base_summary:
            criteria.append(
                AcceptanceCriterion(
                    id="ac-tests-passing",
                    description=(
                        f"Test suite passes at baseline level "
                        f"({base_summary.passed}/{base_summary.total} tests passing)"
                    ),
                    status=FindingStatus.VERIFIED.value
                    if (verification_run.passed)
                    else FindingStatus.REQUIRES_HUMAN_REVIEW.value,
                )
            )
        else:
            criteria.append(
                AcceptanceCriterion(
                    id="ac-tests-passing",
                    description="All tests pass after migration",
                    status=FindingStatus.VERIFIED.value
                    if verification_run.passed
                    else FindingStatus.REQUIRES_HUMAN_REVIEW.value,
                )
            )
    else:
        criteria.append(
            AcceptanceCriterion(
                id="ac-tests-passing",
                description="All tests pass after migration",
                status=FindingStatus.PROPOSED.value,
            )
        )

    # Criterion: no new lint errors
    criteria.append(
        AcceptanceCriterion(
            id="ac-no-lint-errors",
            description="No new lint errors introduced by migration",
            status=FindingStatus.PROPOSED.value,
        )
    )

    return criteria


# ── Agent Pack file generators ────────────────────────────────────────────────

def _render_implementation_prompt(spec: AgentTaskSpec) -> str:
    """Render the implementation-prompt.md — directly usable by a coding agent."""
    t = spec.task
    lines: list[str] = [
        "# CodeShift Migration Implementation Prompt",
        "",
        "## Task",
        "",
        t["description"],
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| Package | `{t['package']}` |",
        f"| From version | `{t.get('from_version') or 'current'}` |",
        f"| To version | `{t['to_version']}` |",
        f"| Rehearsal status | `{t['rehearsal_status']}` |",
        "",
    ]

    if spec.repository.get("url"):
        lines += [
            "## Repository",
            "",
            f"- **URL**: {spec.repository['url']}",
            f"- **Ecosystem**: {spec.repository.get('ecosystem', 'unknown')}",
            f"- **Framework**: {spec.repository.get('framework', 'unknown')}",
            "",
        ]

    lines += [
        "## Constraints",
        "",
    ]
    for c in spec.constraints:
        lines.append(f"- {c}")
    lines.append("")

    lines += [
        "## Files to Modify",
        "",
    ]
    if spec.files_to_modify:
        for f in spec.files_to_modify:
            lines.append(f"- `{f}`")
    else:
        lines.append("- *(determined from findings — see migration-plan.md)*")
    lines.append("")

    if spec.files_not_to_modify:
        lines += [
            "## Files NOT to Modify",
            "",
        ]
        for f in spec.files_not_to_modify:
            lines.append(f"- `{f}`")
        lines.append("")

    lines += [
        "## Findings",
        "",
        "| # | Severity | Title | Status | Required Action |",
        "|---|----------|-------|--------|-----------------|",
    ]
    for i, f in enumerate(spec.findings, 1):
        severity = f.severity.value if hasattr(f.severity, "value") else str(f.severity)
        status = f.status.value if hasattr(f.status, "value") else str(f.status)
        title = f.title.replace("|", "\\|")
        action = f.required_action[:80].replace("|", "\\|")
        lines.append(f"| {i} | {severity} | {title} | {status} | {action} |")
    lines.append("")

    lines += [
        "## Implementation Plan",
        "",
    ]
    for i, action in enumerate(spec.implementation_plan, 1):
        lines.append(f"### {i}. {action['description']}")
        lines.append(f"- **Type**: `{action['action_type']}`")
        if action.get("command"):
            lines.append(f"- **Command**: `{action['command']}`")
        if action.get("target_files"):
            lines.append(f"- **Target files**: {', '.join(f'`{f}`' for f in action['target_files'])}")
        lines.append("")

    lines += [
        "## Acceptance Criteria",
        "",
    ]
    for ac in spec.acceptance_criteria:
        status_icon = "✅" if ac.status == "VERIFIED" else ("⚠️" if ac.status == "REQUIRES_HUMAN_REVIEW" else "📋")
        lines.append(f"- {status_icon} **[{ac.status}]** {ac.description}")
    lines.append("")

    lines += [
        "## Verification",
        "",
        f"**Outcome**: {spec.verification.outcome.value}",
        "",
    ]
    if spec.verification.summary:
        lines.append(spec.verification.summary)
        lines.append("")
    if spec.verification.human_review_items:
        lines += [
            "### Items Requiring Human Review",
            "",
        ]
        for item in spec.verification.human_review_items:
            lines.append(f"- ⚠️ {item}")
        lines.append("")

    if spec.patch_diff:
        lines += [
            "## Patch",
            "",
            "A diff produced during the CodeShift rehearsal is available in `patch.diff`.",
            "Apply it as a reference or starting point — validate against your repository.",
            "",
        ]

    lines += [
        "---",
        "",
        "*Generated by CodeShift — Repository Migration Rehearsal System*",
        "",
    ]

    return "\n".join(lines)


def _render_agents_md(spec: AgentTaskSpec) -> str:
    """AGENTS.md — context for agentic coding environments."""
    return f"""# AGENTS.md — CodeShift Migration Context

## What This Pack Is

This Agent Pack was generated by **CodeShift**, a repository migration rehearsal system.

CodeShift rehearsed the migration in a disposable Twin workspace before touching the
original repository. This pack contains everything you need to implement the migration.

## Migration Task

{spec.task['description']}

## Verification Outcome

**{spec.verification.outcome.value}**

{spec.verification.summary or ''}

## Key Files

| File | Purpose |
|------|---------|
| `agent_task.json` | Machine-readable full task specification |
| `implementation-prompt.md` | Human/agent implementation instructions |
| `migration-plan.md` | Detailed migration plan from CodeShift analysis |
| `findings.json` | Structured migration findings (JSON) |
| `verification.md` | Verification results from the rehearsal Twin |
| `patch.diff` | Git diff from the rehearsal Twin (reference) |

## Important Constraints

{chr(10).join(f'- {c}' for c in spec.constraints)}

## Human Review Required

{"Yes — see verification.md for unresolved items." if spec.verification.human_review_items else "No — all issues were resolved in the rehearsal Twin."}
"""


def _render_migration_plan_md(spec: AgentTaskSpec) -> str:
    """migration-plan.md — full migration plan in markdown."""
    lines = [
        "# Migration Plan",
        "",
        f"**Package**: `{spec.task['package']}`  ",
        f"**From**: `{spec.task.get('from_version') or 'current'}`  ",
        f"**To**: `{spec.task['to_version']}`  ",
        "",
        "## Summary",
        "",
        f"- Total findings: {len(spec.findings)}",
        f"- Critical findings: {sum(1 for f in spec.findings if getattr(f.severity, 'value', f.severity) == 'CRITICAL')}",
        f"- Planned actions: {len(spec.implementation_plan)}",
        f"- Outcome: **{spec.verification.outcome.value}**",
        "",
        "## Findings",
        "",
    ]
    if spec.findings:
        for f in spec.findings:
            severity = f.severity.value if hasattr(f.severity, "value") else str(f.severity)
            status = f.status.value if hasattr(f.status, "value") else str(f.status)
            ftype = f.type.value if hasattr(f.type, "value") else str(f.type)
            lines += [
                f"### {f.title}",
                "",
                f"- **Type**: {ftype}",
                f"- **Severity**: {severity}",
                f"- **Status**: {status}",
                f"- **Reason**: {f.reason}",
                f"- **Required action**: {f.required_action}",
            ]
            if f.affected_files:
                lines.append(f"- **Affected files**: {', '.join(f'`{fp}`' for fp in f.affected_files)}")
            if f.evidence:
                lines += ["- **Evidence**:", "", f"  ```", f"  {f.evidence[:500]}", "  ```"]
            lines.append("")
    else:
        lines.append("*No findings recorded.*")
        lines.append("")

    lines += [
        "## Planned Actions",
        "",
    ]
    if spec.implementation_plan:
        for i, action in enumerate(spec.implementation_plan, 1):
            lines.append(f"### {i}. {action['description']}")
            lines.append(f"- **Type**: `{action['action_type']}`")
            if action.get("command"):
                lines.append(f"- **Command**: `{action['command']}`")
            if action.get("target_files"):
                lines.append(f"- **Files**: {', '.join(f'`{f}`' for f in action['target_files'])}")
            lines.append("")
    else:
        lines.append("*No planned actions recorded.*")
        lines.append("")

    if spec.knowledge_sources:
        lines += [
            "## Knowledge Sources",
            "",
        ]
        for s in spec.knowledge_sources:
            lines.append(f"- {s}")
        lines.append("")

    return "\n".join(lines)


def _render_verification_md(spec: AgentTaskSpec) -> str:
    """verification.md — verification results."""
    v = spec.verification
    lines = [
        "# Verification Results",
        "",
        f"## Final Outcome: {v.outcome.value}",
        "",
        f"- Verification rounds: {v.rounds}",
        f"- Regressions found: {v.regressions_found}",
        f"- Regressions resolved: {v.regressions_resolved}",
        f"- Unresolved regressions: {v.unresolved_regressions}",
        "",
    ]
    if v.summary:
        lines += ["## Summary", "", v.summary, ""]

    lines += ["## Acceptance Criteria", ""]
    for ac in spec.acceptance_criteria:
        status_icon = "✅" if ac.status == "VERIFIED" else ("⚠️" if ac.status == "REQUIRES_HUMAN_REVIEW" else "📋")
        lines.append(f"- {status_icon} **[{ac.status}]** {ac.description}")
    lines.append("")

    if v.human_review_items:
        lines += [
            "## ⚠️ Items Requiring Human Review",
            "",
            "These items were not fully resolved during the rehearsal and require manual inspection:",
            "",
        ]
        for item in v.human_review_items:
            lines.append(f"- {item}")
        lines.append("")

    lines += [
        "---",
        "",
        "*Verification was performed inside a disposable Twin workspace.*",
        "*The original repository was NOT modified.*",
        "",
    ]
    return "\n".join(lines)


def _render_readme(spec: AgentTaskSpec) -> str:
    """README.md for the Agent Pack."""
    return f"""# CodeShift Agent Pack

**Migration**: {spec.task['description']}  
**Rehearsal ID**: `{spec.rehearsal_id}`  
**Outcome**: **{spec.verification.outcome.value}**

## What's in this pack

| File | Description |
|------|-------------|
| `agent_task.json` | Complete machine-readable AgentTaskSpec |
| `implementation-prompt.md` | Ready-to-use implementation prompt for a coding agent |
| `AGENTS.md` | Context file for agentic coding environments |
| `migration-plan.md` | Full migration analysis and planned actions |
| `findings.json` | Migration findings in JSON format |
| `verification.md` | Verification results and acceptance criteria |
| `patch.diff` | Git diff from the rehearsal Twin (apply as reference) |

## Quick Start

1. Read `implementation-prompt.md` for the full task specification.
2. Review `findings.json` for all migration issues found.
3. Use `patch.diff` as a reference for the required changes.
4. Run your test suite and verify against the acceptance criteria in `verification.md`.

## Outcome Details

{spec.verification.summary or 'See verification.md for details.'}

{"## ⚠️ Human Review Required" + chr(10) + chr(10) + "The following items were not resolved during the rehearsal:" + chr(10) + chr(10) + chr(10).join(f"- {item}" for item in spec.verification.human_review_items) if spec.verification.human_review_items else ""}

---

*Generated by [CodeShift](https://github.com) — Repository Migration Rehearsal System*
"""


# ── Pack assembly ─────────────────────────────────────────────────────────────

def generate_agent_pack_zip(spec: AgentTaskSpec) -> bytes:
    """
    Generate the full Agent Pack as an in-memory ZIP archive.

    Returns the raw ZIP bytes.
    """
    prefix = "CodeShift-Agent-Pack/"

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        # agent_task.json
        zf.writestr(
            prefix + "agent_task.json",
            spec.model_dump_json(indent=2),
        )

        # implementation-prompt.md
        zf.writestr(
            prefix + "implementation-prompt.md",
            _render_implementation_prompt(spec),
        )

        # AGENTS.md
        zf.writestr(prefix + "AGENTS.md", _render_agents_md(spec))

        # migration-plan.md
        zf.writestr(prefix + "migration-plan.md", _render_migration_plan_md(spec))

        # findings.json — findings only, compact
        findings_data = [
            json.loads(f.model_dump_json())
            for f in spec.findings
        ]
        zf.writestr(
            prefix + "findings.json",
            json.dumps(findings_data, indent=2),
        )

        # verification.md
        zf.writestr(prefix + "verification.md", _render_verification_md(spec))

        # patch.diff — twin diff when available
        zf.writestr(
            prefix + "patch.diff",
            spec.patch_diff or "# No diff available — migration may have used external tools.\n",
        )

        # README.md
        zf.writestr(prefix + "README.md", _render_readme(spec))

    return buf.getvalue()


### 🤖 Assistant

> 🔧 called: apply_diff

Now update the models `__init__.py` to export `AgentTaskSpec`:

> 🔧 **apply_diff** — backend/app/models/__init__.py

### 🤖 Assistant

> 🔧 called: read_file

Now add the demo mode service and update the migration service to support demo mode. First, let me check the existing migration service for demo handling:

> 🔧 **read_file** — backend/app/services/diagnosis.py

### 🤖 Assistant

> 🔧 called: write_file

Now let me create the demo mode service:

> 🔧 **write_file** — """
Demo Mode service — Session 6.

Provides a fully deterministic React 17 → 18 migration rehearsal that
exercises the complete end-to-end pipeline without requiring:
  - A live repository clone
  - Watsonx credentials
  - Node/npm installed

The demo uses pre-baked artefacts that mirror what the real pipeline
would produce for a React 17 app upgrading to React 18.

Deterministic: same rehearsal_id always produces the same artefacts.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.models.baseline import BaselineResult, CommandResult, StepStatus, TestRunSummary
from app.models.finding import FindingSeverity, FindingStatus, FindingType, MigrationFinding
from app.models.migration_plan import ActionType, MigrationPlan, PlannedAction
from app.models.rehearsal import Rehearsal, RehearsalStage, RehearsalStatus, RepositorySource, TargetUpgrade
from app.models.repository_profile import Ecosystem, PackageManager, RepositoryProfile, ScriptInfo, SourceStructure
from app.models.twin import ChangedFile, MigrationStatus, TwinMethod, TwinResult
from app.models.verification import VerificationContext, VerificationResult
from app.models.verification_run import DiagnosisRecord, RepairRecord, VerificationRun

logger = logging.getLogger(__name__)

# The canonical demo scenario
DEMO_REPO_URL = "https://github.com/example/react17-demo-app"
DEMO_PACKAGE = "react"
DEMO_FROM_VERSION = "17"
DEMO_TO_VERSION = "18"


def build_demo_rehearsal(rehearsal_id: str) -> Rehearsal:
    """Return the demo Rehearsal record."""
    return Rehearsal(
        id=rehearsal_id,
        status=RehearsalStatus.COMPLETE,
        stage=RehearsalStage.COMPLETE,
        repository=RepositorySource(
            url=DEMO_REPO_URL,
            is_demo=True,
            local_path=None,
        ),
        target_upgrade=TargetUpgrade(
            package=DEMO_PACKAGE,
            from_version=DEMO_FROM_VERSION,
            to_version=DEMO_TO_VERSION,
            ecosystem="node",
        ),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
    )


def build_demo_profile(rehearsal_id: str) -> RepositoryProfile:
    """Return a demo RepositoryProfile for a React 17 app."""
    return RepositoryProfile(
        rehearsal_id=rehearsal_id,
        name="react17-demo-app",
        source_url=DEMO_REPO_URL,
        ecosystem=Ecosystem.NODE,
        runtime="node",
        package_manager=PackageManager.NPM,
        framework="react",
        dependencies={
            "react": "^17.0.2",
            "react-dom": "^17.0.2",
            "react-router-dom": "^6.0.0",
        },
        dev_dependencies={
            "@types/react": "^17.0.0",
            "@types/react-dom": "^17.0.0",
            "@testing-library/react": "^12.0.0",
            "typescript": "^4.5.4",
            "jest": "^27.0.0",
        },
        lockfile="package-lock.json",
        build_scripts=[ScriptInfo(name="build", command="npm run build")],
        test_scripts=[ScriptInfo(name="test", command="npm test -- --watchAll=false")],
        lint_scripts=[ScriptInfo(name="lint", command="npm run lint")],
        structure=SourceStructure(
            src_dirs=["src"],
            test_dirs=["src"],
            config_files=["package.json", "tsconfig.json"],
            entry_points=["src/index.tsx"],
        ),
        raw_manifest={
            "name": "react17-demo-app",
            "version": "1.0.0",
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "lint": "eslint src --ext .ts,.tsx",
            },
        },
    )


def build_demo_baseline(rehearsal_id: str) -> BaselineResult:
    """Return a demo baseline showing all tests passing before migration."""
    return BaselineResult(
        rehearsal_id=rehearsal_id,
        install=CommandResult(
            step="install",
            command="npm install",
            exit_code=0,
            stdout="added 1245 packages in 14s",
            stderr="",
            duration_seconds=14.2,
            status=StepStatus.PASSED,
        ),
        build=CommandResult(
            step="build",
            command="npm run build",
            exit_code=0,
            stdout="Compiled successfully.\n\nFile sizes after gzip:\n  82.13 kB  build/static/js/main.chunk.js",
            stderr="",
            duration_seconds=8.7,
            status=StepStatus.PASSED,
        ),
        test=CommandResult(
            step="test",
            command="npm test -- --watchAll=false",
            exit_code=0,
            stdout=(
                "PASS src/App.test.tsx\n"
                "PASS src/components/Header.test.tsx\n"
                "PASS src/components/Button.test.tsx\n"
                "PASS src/hooks/useAuth.test.ts\n"
                "PASS src/pages/Home.test.tsx\n"
                "PASS src/pages/Dashboard.test.tsx\n\n"
                "Tests: 184 passed, 184 total\n"
                "Test Suites: 6 passed, 6 total\n"
                "Time: 4.821 s"
            ),
            stderr="",
            duration_seconds=4.8,
            status=StepStatus.PASSED,
            test_summary=TestRunSummary(passed=184, failed=0, total=184),
        ),
        lint=CommandResult(
            step="lint",
            command="npm run lint",
            exit_code=0,
            stdout="",
            stderr="",
            duration_seconds=2.1,
            status=StepStatus.PASSED,
        ),
        passed=True,
        notes="Baseline established: 184/184 tests passing, build clean, lint clean.",
    )


def build_demo_migration_plan(rehearsal_id: str) -> MigrationPlan:
    """Return a demo MigrationPlan for React 17 → 18."""
    f1 = MigrationFinding(
        type=FindingType.BREAKING_CHANGE,
        severity=FindingSeverity.CRITICAL,
        title="ReactDOM.render is deprecated — use createRoot",
        reason=(
            "React 18 removes ReactDOM.render and ReactDOM.hydrate. "
            "The new root API must be used: createRoot from react-dom/client."
        ),
        evidence="ReactDOM.render(<App />, document.getElementById('root'));",
        required_action=(
            "Replace ReactDOM.render(<App />, container) with "
            "import { createRoot } from 'react-dom/client'; createRoot(container).render(<App />);"
        ),
        affected_files=["src/index.tsx"],
        status=FindingStatus.VERIFIED,
        verification_note="Fixed in Twin — all tests passing after repair.",
    )
    f2 = MigrationFinding(
        type=FindingType.BREAKING_CHANGE,
        severity=FindingSeverity.MEDIUM,
        title="Automatic batching now applies to all updates",
        reason=(
            "In React 18, state updates inside setTimeout, promises, and native event "
            "handlers are batched. Code reading state immediately after async setState "
            "may behave differently."
        ),
        required_action=(
            "Audit async code that reads state immediately after setState. "
            "Wrap any update that must not be batched with ReactDOM.flushSync()."
        ),
        affected_files=[],
        status=FindingStatus.PROPOSED,
    )
    f3 = MigrationFinding(
        type=FindingType.DEPRECATED_API,
        severity=FindingSeverity.CRITICAL,
        title="Update @testing-library/react to v13+",
        reason="@testing-library/react v12 is not compatible with React 18.",
        required_action=(
            "Upgrade @testing-library/react to ^13.0.0 in package.json. "
            "Update @types/react and @types/react-dom to ^18."
        ),
        affected_files=["package.json"],
        status=FindingStatus.VERIFIED,
        verification_note="Updated in Twin — tests pass.",
    )
    f4 = MigrationFinding(
        type=FindingType.BREAKING_CHANGE,
        severity=FindingSeverity.MEDIUM,
        title="StrictMode double-invokes effects in development",
        reason=(
            "React 18 StrictMode mounts, unmounts, and remounts components in development "
            "to surface cleanup issues. Effects must be idempotent."
        ),
        required_action=(
            "Review useEffect hooks for idempotency. "
            "Ensure cleanup functions properly reverse all side effects."
        ),
        affected_files=[],
        status=FindingStatus.REQUIRES_HUMAN_REVIEW,
        verification_note="Requires manual review — cannot be auto-detected.",
    )

    pa1 = PlannedAction(
        action_type=ActionType.VERSION_BUMP,
        description="Bump react, react-dom, @types/react, @types/react-dom to ^18",
        target_files=["package.json"],
        command="npm install react@^18 react-dom@^18 @types/react@^18 @types/react-dom@^18",
    )
    pa2 = PlannedAction(
        action_type=ActionType.CODEMOD,
        description="Replace ReactDOM.render with createRoot in src/index.tsx",
        target_files=["src/index.tsx"],
        command=None,
    )
    pa3 = PlannedAction(
        action_type=ActionType.VERSION_BUMP,
        description="Upgrade @testing-library/react to ^13",
        target_files=["package.json"],
        command="npm install @testing-library/react@^13",
    )

    plan = MigrationPlan(
        rehearsal_id=rehearsal_id,
        package=DEMO_PACKAGE,
        from_version=DEMO_FROM_VERSION,
        to_version=DEMO_TO_VERSION,
        findings=[f1, f2, f3, f4],
        planned_actions=[pa1, pa2, pa3],
        knowledge_sources=["react 17→18"],
        watsonx_model="demo-mode",
        notes=(
            "React 18 migration analysis. Critical items: new root API and "
            "testing-library upgrade. Both resolved in Twin verification."
        ),
    )
    plan.recompute_summary()
    return plan


def build_demo_twin_result(rehearsal_id: str) -> TwinResult:
    """Return a demo TwinResult after migration execution."""
    git_diff = """\
diff --git a/package.json b/package.json
index a1b2c3d..e4f5g6h 100644
--- a/package.json
+++ b/package.json
@@ -5,10 +5,10 @@
   "dependencies": {
-    "react": "^17.0.2",
-    "react-dom": "^17.0.2",
+    "react": "^18.2.0",
+    "react-dom": "^18.2.0",
     "react-router-dom": "^6.0.0"
   },
   "devDependencies": {
-    "@types/react": "^17.0.0",
-    "@types/react-dom": "^17.0.0",
-    "@testing-library/react": "^12.0.0",
+    "@types/react": "^18.0.0",
+    "@types/react-dom": "^18.0.0",
+    "@testing-library/react": "^13.4.0",
     "typescript": "^4.5.4",
     "jest": "^27.0.0"
   }
diff --git a/src/index.tsx b/src/index.tsx
index 1234567..abcdefg 100644
--- a/src/index.tsx
+++ b/src/index.tsx
@@ -1,6 +1,7 @@
-import ReactDOM from 'react-dom';
+import { createRoot } from 'react-dom/client';
 import App from './App';
 
-ReactDOM.render(
-  <React.StrictMode><App /></React.StrictMode>,
-  document.getElementById('root')
-);
+const container = document.getElementById('root')!;
+const root = createRoot(container);
+root.render(<React.StrictMode><App /></React.StrictMode>);
"""

    return TwinResult(
        rehearsal_id=rehearsal_id,
        method=TwinMethod.TEMP_COPY,
        twin_path="/tmp/codeshift-demo-twin",
        starting_revision="abc1234",
        migration_status=MigrationStatus.SUCCESS,
        changed_files=[
            ChangedFile(path="package.json", change_type="modified"),
            ChangedFile(path="src/index.tsx", change_type="modified"),
        ],
        git_diff=git_diff,
        execution_log=[
            "VERSION_BUMP: npm install react@^18 react-dom@^18 @types/react@^18 @types/react-dom@^18 — exit 0",
            "CODEMOD: replaced ReactDOM.render with createRoot in src/index.tsx",
            "VERSION_BUMP: npm install @testing-library/react@^13 — exit 0",
            "Migration complete: 2 files modified",
        ],
        actions_applied=["action-version-bump", "action-codemod-render", "action-testing-library"],
        actions_skipped=[],
        manual_items=[
            "Review useEffect hooks for idempotency (StrictMode double-invoke)"
        ],
    )


def build_demo_verification_run(rehearsal_id: str) -> VerificationRun:
    """
    Return a demo VerificationRun representing:
    Round 1: 176/184 tests (8 regressions due to createRoot)
    Diagnosis: createRoot import pattern, targeted repair applied
    Round 2: 184/184 tests — VERIFIED
    """
    ver1 = VerificationResult(
        rehearsal_id=rehearsal_id,
        context=VerificationContext.POST_MIGRATION,
        round=1,
        install=CommandResult(
            step="install", command="npm install",
            exit_code=0, stdout="updated packages", stderr="",
            duration_seconds=8.2, status=StepStatus.PASSED,
        ),
        build=CommandResult(
            step="build", command="npm run build",
            exit_code=0, stdout="Compiled successfully.", stderr="",
            duration_seconds=9.1, status=StepStatus.PASSED,
        ),
        test=CommandResult(
            step="test", command="npm test -- --watchAll=false",
            exit_code=1,
            stdout=(
                "PASS src/App.test.tsx\n"
                "PASS src/components/Header.test.tsx\n"
                "PASS src/components/Button.test.tsx\n"
                "FAIL src/hooks/useAuth.test.ts\n"
                "FAIL src/pages/Home.test.tsx\n"
                "FAIL src/pages/Dashboard.test.tsx\n\n"
                "Tests: 176 passed, 8 failed, 184 total\n"
                "Test Suites: 3 failed, 3 passed, 6 total"
            ),
            stderr=(
                "Error: ReactDOM.render is not supported in React 18. "
                "Use createRoot instead.\n"
                "  at renderRoot (src/test-utils/render.tsx:12:5)"
            ),
            duration_seconds=5.2, status=StepStatus.FAILED,
            test_summary=TestRunSummary(passed=176, failed=8, total=184),
        ),
        passed=False,
        regression_count=8,
        regression_details=[
            "test: 8 test failures — ReactDOM.render used in test utils"
        ],
        baseline_test_total=184,
        baseline_test_passed=184,
    )

    ver2 = VerificationResult(
        rehearsal_id=rehearsal_id,
        context=VerificationContext.POST_REPAIR,
        round=2,
        install=CommandResult(
            step="install", command="npm install",
            exit_code=0, stdout="", stderr="",
            duration_seconds=3.1, status=StepStatus.PASSED,
        ),
        build=CommandResult(
            step="build", command="npm run build",
            exit_code=0, stdout="Compiled successfully.", stderr="",
            duration_seconds=8.8, status=StepStatus.PASSED,
        ),
        test=CommandResult(
            step="test", command="npm test -- --watchAll=false",
            exit_code=0,
            stdout=(
                "PASS src/App.test.tsx\n"
                "PASS src/components/Header.test.tsx\n"
                "PASS src/components/Button.test.tsx\n"
                "PASS src/hooks/useAuth.test.ts\n"
                "PASS src/pages/Home.test.tsx\n"
                "PASS src/pages/Dashboard.test.tsx\n\n"
                "Tests: 184 passed, 184 total\n"
                "Test Suites: 6 passed, 6 total\n"
                "Time: 4.634 s"
            ),
            stderr="",
            duration_seconds=4.6, status=StepStatus.PASSED,
            test_summary=TestRunSummary(passed=184, failed=0, total=184),
        ),
        passed=True,
        regression_count=0,
        regression_details=[],
        baseline_test_total=184,
        baseline_test_passed=184,
    )

    diagnosis = DiagnosisRecord(
        step="test",
        root_cause=(
            "Test utility file src/test-utils/render.tsx still used ReactDOM.render "
            "from react-dom (legacy API). The migration updated src/index.tsx but missed "
            "the test utility wrapper."
        ),
        migration_relevant=True,
        affected_files=["src/test-utils/render.tsx"],
        requires_human_review=False,
        confidence="HIGH",
        repair_applied=True,
        repair_notes=(
            "Updated src/test-utils/render.tsx: replaced ReactDOM.render with createRoot. "
            "All 184 tests passing after repair."
        ),
    )

    repair = RepairRecord(
        step="test",
        applied=True,
        changed_files=["src/test-utils/render.tsx"],
        notes=(
            "Applied targeted fix to src/test-utils/render.tsx — "
            "replaced legacy ReactDOM.render call with createRoot pattern."
        ),
        requires_human_review=False,
    )

    # Return the final (round 2) verification run with full history
    return VerificationRun(
        rehearsal_id=rehearsal_id,
        round=2,
        verification=ver2,
        diagnoses=[diagnosis],
        repairs=[repair],
        passed=True,
        requires_human_review=False,
        summary=(
            "Round 1: 176/184 tests (8 regressions). "
            "Diagnosis: legacy ReactDOM.render in test utility. "
            "Repair applied to src/test-utils/render.tsx. "
            "Round 2: 184/184 tests — VERIFIED."
        ),
    )


### 🤖 Assistant

> 🔧 called: read_file, read_file

Now let me check if `VerificationResult` and `BaselineResult` have all the fields we're using:

> 🔧 **read_file** — backend/app/models/baseline.py

> 🔧 **read_file** — backend/app/models/verification.py

### 🤖 Assistant

> 🔧 called: apply_diff

Good. `BaselineResult` has `test_summary` but `CommandResult` does not. The `TestRunSummary` is on the `BaselineResult` directly. Let me fix the demo service to match the actual model structure:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:89
-------
    build=CommandResult(
            step="build", command="npm run build",
            exit_code=0, stdout="Compiled successfully.\n\nFile sizes after gzip:\n  82.13 kB  build/static/js/main.chunk.js",
            stderr="",
            duration_seconds=8.7,
            status=StepStatus.PASSED,
        ),
        test=CommandResult(
            step="test",
            command="npm test -- --watchAll=false",
            exit_code=0,
            stdout=(
                "PASS src/App.test.tsx\n"
                "PASS src/components/Header.test.tsx\n"
                "PASS src/components/Button.test.tsx\n"
                "PASS src/hooks/useAuth.test.ts\n"
                "PASS src/pages/Home.test.tsx\n"
                "PASS src/pages/Dashboard.test.tsx\n\n"
                "Tests: 184 passed, 184 total\n"
                "Test Suites: 6 passed, 6 total\n"
                "Time: 4.821 s"
            ),
            stderr="",
            duration_seconds=4.8,
            status=StepStatus.PASSED,
            test_summary=TestRunSummary(passed=184, failed=0, total=184),
        ),
=======
    build=CommandResult(
            step="build", command="npm run build",
            exit_code=0, stdout="Compiled successfully.\n\nFile sizes after gzip:\n  82.13 kB  build/static/js/main.chunk.js",
            stderr="",
            duration_seconds=8.7,
            status=StepStatus.PASSED,
        ),
        test=CommandResult(
            step="test",
            command="npm test -- --watchAll=false",
            exit_code=0,
            stdout=(
                "PASS src/App.test.tsx\n"
                "PASS src/components/Header.test.tsx\n"
                "PASS src/components/Button.test.tsx\n"
                "PASS src/hooks/useAuth.test.ts\n"
                "PASS src/pages/Home.test.tsx\n"
                "PASS src/pages/Dashboard.test.tsx\n\n"
                "Tests: 184 passed, 184 total\n"
                "Test Suites: 6 passed, 6 total\n"
                "Time: 4.821 s"
            ),
            stderr="",
            duration_seconds=4.8,
            status=StepStatus.PASSED,
        ),
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:116
-------
        passed=True,
        notes="Baseline established: 184/184 tests passing, build clean, lint clean.",
    )
=======
        passed=True,
        test_summary=TestRunSummary(passed=184, failed=0, total=184),
        notes="Baseline established: 184/184 tests passing, build clean, lint clean.",
    )
>>>>>>> REPLACE


---

### 👤 User

Reverted changes to 4 files: agent_task_spec.py, agent_pack.py, __init__.py, demo.py