# # Session 5 - Verification + Recovery

Implement ONLY the verification and migration-recovery layer for CodeShift-Final v1.0.

First:
- Read `architecture.md`
- Inspect the existing implementation from Sessions 1-4
- Reuse the existing models, TwinResult, persistence, rehearsal flow, and APIs
- Do not redesign or refactor unrelated code

## Goal

After Session 4 has created a Twin and applied the migration, CodeShift must determine whether the migration actually works.

Required flow:

Twin
→ install/build/test/lint
→ compare with baseline
→ identify migration failures
→ diagnose relevant failures with Watsonx
→ apply targeted repair where safe
→ verify again

## Implement

### 1. Verification

Run the applicable repository checks inside the Twin:

- install
- build
- test
- lint

Reuse the existing baseline command structure where possible.

Capture:
- command
- exit code
- pass/fail
- relevant output
- duration

Compare the result with the stored baseline.

Do NOT modify the original repository.

### 2. Failure extraction

From failed commands, extract the useful failure information.

Keep this deterministic and simple.

Group obviously related failures into small failure clusters.

Each cluster should retain enough information to understand:
- what failed
- relevant error/output
- affected file(s) when detectable
- associated migration finding when possible

Do not build a sophisticated static-analysis or observability system.

### 3. Watsonx diagnosis

For migration-caused or potentially migration-caused failures, send compact context to Watsonx:

- migration findings
- failure clusters
- relevant diff
- relevant source snippets
- baseline comparison

Do NOT send the entire repository or huge raw logs.

Ask Watsonx for a structured diagnosis containing:
- likely root cause
- migration relevance
- affected files
- recommended targeted fix
- whether human review is required

Reuse the existing Watsonx client.

### 4. Targeted repair

For fixes that are clear and safe:

- apply the targeted change inside the Twin
- never modify the original repository

For ambiguous or unsafe fixes:

- do not guess
- mark the finding `REQUIRES_HUMAN_REVIEW`

After a repair, run verification again.

### 5. Final status

The rehearsal should be able to reach:

VERIFIED

when the migrated Twin passes the applicable checks,

or:

REQUIRES_HUMAN_REVIEW

when unresolved migration issues remain.

Persist the final verification/recovery information using the existing filesystem approach.

Update the existing rehearsal flow minimally.

## DO NOT IMPLEMENT

- AgentTaskSpec
- Agent Pack
- frontend redesign
- new dashboard
- AST framework
- generic repair engine
- multi-language support
- RAG
- vector database
- additional LLMs
- authentication
- deployment
- large test suites
- extensive documentation

Do not refactor unrelated Sessions 1-4 code.

## Efficiency

Keep this implementation minimal.

Reuse existing models, services, persistence, and Watsonx client.

Do not add libraries unless absolutely necessary.

Do not create a new testing framework or extensive tests.

Run only the minimum existing checks needed to catch regressions.

Do not invent credentials.

Do not add speculative abstractions.

Prefer deterministic parsing and decision logic wherever possible.

Use Watsonx only for semantic diagnosis where deterministic logic is insufficient.

## Completion

Stop when this flow works:

existing migrated Twin
→ verification
→ failure extraction
→ Watsonx diagnosis where needed
→ targeted repair or human-review status
→ verification again
→ final VERIFIED / REQUIRES_HUMAN_REVIEW result

Do not start AgentTaskSpec or Agent Pack work.

---

**Status:** active  **Date:** 2026-09-26

---

### 👤 User

# Session 5 - Verification + Recovery

Implement ONLY the verification and migration-recovery layer for CodeShift-Final v1.0.

First:
- Read `architecture.md`
- Inspect the existing implementation from Sessions 1-4
- Reuse the existing models, TwinResult, persistence, rehearsal flow, and APIs
- Do not redesign or refactor unrelated code

## Goal

After Session 4 has created a Twin and applied the migration, CodeShift must determine whether the migration actually works.

Required flow:

Twin
→ install/build/test/lint
→ compare with baseline
→ identify migration failures
→ diagnose relevant failures with Watsonx
→ apply targeted repair where safe
→ verify again

## Implement

### 1. Verification

Run the applicable repository checks inside the Twin:

- install
- build
- test
- lint

Reuse the existing baseline command structure where possible.

Capture:
- command
- exit code
- pass/fail
- relevant output
- duration

Compare the result with the stored baseline.

Do NOT modify the original repository.

### 2. Failure extraction

From failed commands, extract the useful failure information.

Keep this deterministic and simple.

Group obviously related failures into small failure clusters.

Each cluster should retain enough information to understand:
- what failed
- relevant error/output
- affected file(s) when detectable
- associated migration finding when possible

Do not build a sophisticated static-analysis or observability system.

### 3. Watsonx diagnosis

For migration-caused or potentially migration-caused failures, send compact context to Watsonx:

- migration findings
- failure clusters
- relevant diff
- relevant source snippets
- baseline comparison

Do NOT send the entire repository or huge raw logs.

Ask Watsonx for a structured diagnosis containing:
- likely root cause
- migration relevance
- affected files
- recommended targeted fix
- whether human review is required

Reuse the existing Watsonx client.

### 4. Targeted repair

For fixes that are clear and safe:

- apply the targeted change inside the Twin
- never modify the original repository

For ambiguous or unsafe fixes:

- do not guess
- mark the finding `REQUIRES_HUMAN_REVIEW`

After a repair, run verification again.

### 5. Final status

The rehearsal should be able to reach:

VERIFIED

when the migrated Twin passes the applicable checks,

or:

REQUIRES_HUMAN_REVIEW

when unresolved migration issues remain.

Persist the final verification/recovery information using the existing filesystem approach.

Update the existing rehearsal flow minimally.

## DO NOT IMPLEMENT

- AgentTaskSpec
- Agent Pack
- frontend redesign
- new dashboard
- AST framework
- generic repair engine
- multi-language support
- RAG
- vector database
- additional LLMs
- authentication
- deployment
- large test suites
- extensive documentation

Do not refactor unrelated Sessions 1-4 code.

## Efficiency

Keep this implementation minimal.

Reuse existing models, services, persistence, and Watsonx client.

Do not add libraries unless absolutely necessary.

Do not create a new testing framework or extensive tests.

Run only the minimum existing checks needed to catch regressions.

Do not invent credentials.

Do not add speculative abstractions.

Prefer deterministic parsing and decision logic wherever possible.

Use Watsonx only for semantic diagnosis where deterministic logic is insufficient.

## Completion

Stop when this flow works:

existing migrated Twin
→ verification
→ failure extraction
→ Watsonx diagnosis where needed
→ targeted repair or human-review status
→ verification again
→ final VERIFIED / REQUIRES_HUMAN_REVIEW result

Do not start AgentTaskSpec or Agent Pack work.

---

### 🤖 Assistant

> 🔧 called: read_file, list_files



> 🔧 **read_file** — architecture.md

> 🔧 **list_files** — backend/app

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — architecture.md

> 🔧 **read_file** — backend/app/models/verification.py

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — architecture.md

> 🔧 **read_file** — backend/app/models/rehearsal.py

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — backend/app/models/baseline.py

> 🔧 **read_file** — backend/app/models/finding.py

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — backend/app/services/twin.py

> 🔧 **read_file** — backend/app/services/baseline.py

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — backend/app/services/migration.py

> 🔧 **read_file** — backend/app/services/watsonx_client.py

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — backend/app/services/store.py

> 🔧 **read_file** — backend/app/api/rehearsals.py

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — backend/app/models/twin.py

> 🔧 **read_file** — backend/app/services/executor.py

### 🤖 Assistant

> 🔧 called: update_todo_list

Now I have a thorough understanding of the codebase. Let me plan what needs to be built for Session 5:

> 🔧 **update_todo_list** — [-] Read and understand existing codebase (Sessions 1-4)
[ ] Create verification service (run install/build/test/lint inside Twin, compare with baseline)
[ ] Create failure clustering service (parse logs, group failures, map to files/findings)
[ ] Create Watsonx diagnosis service (compact prompt, structured diagnosis response)
[ ] Create repair service (apply targeted fixes inside Twin, mark ambiguous as REQUIRES_HUMAN_REVIEW)
[ ] Add persistence for verification results and repair records to store.py
[ ] Wire up the verify/diagnose/repair pipeline in a new background task
[ ] Add API endpoint POST /api/rehearsals/{id}/verify to the rehearsals router
[ ] Update RehearsalResponse to include verification result
[ ] Minimal regression check


### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — backend/app/models/__init__.py

> 🔧 **read_file** — backend/app/models/migration_plan.py

### 🤖 Assistant

> 🔧 called: update_todo_list

Now I have a complete picture. Let me implement all the Session 5 components.

> 🔧 **update_todo_list** — [x] Read and understand existing codebase (Sessions 1-4)
[-] Create verification service (run install/build/test/lint inside Twin, compare with baseline)
[ ] Create failure clustering service (parse logs, group failures, map to files/findings)
[ ] Create Watsonx diagnosis service (compact prompt, structured diagnosis response)
[ ] Create repair service (apply targeted fixes inside Twin, mark ambiguous as REQUIRES_HUMAN_REVIEW)
[ ] Add persistence for verification results and repair records to store.py
[ ] Wire up the verify/diagnose/repair pipeline in a new background task
[ ] Add API endpoint POST /api/rehearsals/{id}/verify to the rehearsals router
[ ] Update RehearsalResponse to include verification result
[ ] Minimal regression check


### 🤖 Assistant

> 🔧 called: write_file

Now let me create all the services. I'll start with the verification service, failure clustering, Watsonx diagnosis, and repair service:

> 🔧 **write_file** — backend/app/services/verification.py

### 🤖 Assistant

> 🔧 called: write_file



> 🔧 **write_file** — """
Failure Clustering — Session 5.

Deterministic log parsing: extracts structured failure information from
failed VerificationResult steps and groups related failures into clusters.

No LLM involved here — this is pure text parsing.
Clusters become the structured input for Watsonx diagnosis.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from app.models.baseline import CommandResult, StepStatus
from app.models.finding import MigrationFinding
from app.models.verification import VerificationResult


# ── Data models ───────────────────────────────────────────────────────────────

@dataclass
class FailureCluster:
    """
    A group of related failures from one verification step.

    Kept small so it can be sent compactly to Watsonx.
    """
    step: str                        # "install" | "build" | "test" | "lint"
    summary: str                     # short one-liner describing the cluster
    errors: list[str]                # individual error lines / messages
    affected_files: list[str]        # file paths mentioned in the output
    related_finding_ids: list[str]   # MigrationFinding IDs that may be related
    raw_output_snippet: str          # ≤ 2 KB of the most relevant output


# ── Pattern library ───────────────────────────────────────────────────────────

# File path patterns in error output
_FILE_REF_RE = re.compile(
    r"(?:^|\s)"                       # word boundary
    r"((?:\./|\.\.\/|[A-Za-z]:[\\/])?[\w./\\-]+\."  # path start
    r"(?:ts|tsx|js|jsx|mjs|cjs|json|css|scss))"       # extension
    r"(?::\d+)?",                     # optional line number
    re.MULTILINE,
)

# TypeScript error lines: src/Foo.tsx(12,5): error TS2345: ...
_TS_ERROR_RE = re.compile(
    r"([\w./\\-]+\.tsx?)\((\d+),(\d+)\):\s+(error|warning)\s+(TS\d+):\s+(.+)"
)

# Jest/Vitest failed test block header
_JEST_FAIL_RE = re.compile(
    r"(?:●|FAIL|✗|×)\s+(.+)"
)

# ESLint error line:  /path/to/file.ts
#   12:5  error  'foo' is not defined  no-undef
_ESLINT_RE = re.compile(
    r"^\s+(\d+):(\d+)\s+(error|warning)\s+(.+?)\s+([\w/-]+)\s*$",
    re.MULTILINE,
)

# npm install errors: npm ERR! ...
_NPM_ERR_RE = re.compile(r"^npm ERR! (.+)$", re.MULTILINE)

# General "Error: ..." lines
_GENERIC_ERR_RE = re.compile(
    r"(?:^|\s)(?:Error|TypeError|SyntaxError|ReferenceError):\s+(.+)",
    re.MULTILINE,
)

_MAX_SNIPPET = 2000  # characters sent to Watsonx per cluster


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_files(text: str) -> list[str]:
    """Return de-duplicated file paths found in error output."""
    found: list[str] = []
    seen: set[str] = set()
    for m in _FILE_REF_RE.finditer(text):
        p = m.group(1).strip()
        if p and p not in seen and len(p) > 3:
            seen.add(p)
            found.append(p)
    return found


def _tail(text: str, max_chars: int = _MAX_SNIPPET) -> str:
    """Return the last *max_chars* characters of *text*, trimmed."""
    if not text:
        return ""
    return text[-max_chars:].strip()


def _most_relevant_output(result: CommandResult) -> str:
    """
    Pick the most relevant portion of a failed command's output.

    Prefers stderr when it has content, falls back to stdout tail.
    """
    stderr = (result.stderr or "").strip()
    stdout = (result.stdout or "").strip()

    if stderr:
        return _tail(stderr)
    return _tail(stdout)


# ── Step-specific parsers ─────────────────────────────────────────────────────

def _cluster_build(result: CommandResult) -> FailureCluster:
    """Parse TypeScript / bundler build failures."""
    text = (result.stdout or "") + "\n" + (result.stderr or "")
    errors: list[str] = []
    files: list[str] = []

    for m in _TS_ERROR_RE.finditer(text):
        path, line, col, kind, code, msg = m.groups()
        errors.append(f"{path}:{line}:{col} {code}: {msg}")
        if path not in files:
            files.append(path)

    # Generic error lines as fallback
    if not errors:
        for m in _GENERIC_ERR_RE.finditer(text):
            err = m.group(1).strip()
            if err and err not in errors:
                errors.append(err)
        files.extend(_extract_files(text))

    summary = (
        f"Build failed with {len(errors)} error(s)"
        if errors
        else "Build failed (exit code {})".format(result.exit_code)
    )
    return FailureCluster(
        step="build",
        summary=summary,
        errors=errors[:20],  # cap
        affected_files=list(dict.fromkeys(files))[:10],
        related_finding_ids=[],
        raw_output_snippet=_most_relevant_output(result),
    )


def _cluster_test(result: CommandResult) -> FailureCluster:
    """Parse Jest / Vitest test failures."""
    text = (result.stdout or "") + "\n" + (result.stderr or "")
    errors: list[str] = []
    files: list[str] = []

    for m in _JEST_FAIL_RE.finditer(text):
        msg = m.group(1).strip()
        if msg and msg not in errors:
            errors.append(msg)

    files.extend(_extract_files(text))

    # Extract "expected ... received ..." snippets
    expect_re = re.compile(r"Expected:(.+?)(?=\n)", re.IGNORECASE)
    for m in expect_re.finditer(text):
        snippet = m.group(1).strip()
        if snippet:
            errors.append(f"Expected: {snippet}")

    summary = (
        f"{len(errors)} test failure(s) detected"
        if errors
        else "Test suite failed (exit code {})".format(result.exit_code)
    )
    return FailureCluster(
        step="test",
        summary=summary,
        errors=errors[:20],
        affected_files=list(dict.fromkeys(files))[:10],
        related_finding_ids=[],
        raw_output_snippet=_most_relevant_output(result),
    )


def _cluster_lint(result: CommandResult) -> FailureCluster:
    """Parse ESLint / tsc lint failures."""
    text = (result.stdout or "") + "\n" + (result.stderr or "")
    errors: list[str] = []
    files: list[str] = []

    # ESLint format
    for m in _ESLINT_RE.finditer(text):
        line, col, kind, msg, rule = m.groups()
        if kind == "error":
            errors.append(f"{line}:{col} {msg} ({rule})")

    files.extend(_extract_files(text))

    # TS errors as fallback
    if not errors:
        for m in _TS_ERROR_RE.finditer(text):
            path, line, col, kind, code, msg = m.groups()
            errors.append(f"{path}:{line} {code}: {msg}")
            if path not in files:
                files.append(path)

    summary = (
        f"Lint failed with {len(errors)} error(s)"
        if errors
        else "Lint failed (exit code {})".format(result.exit_code)
    )
    return FailureCluster(
        step="lint",
        summary=summary,
        errors=errors[:20],
        affected_files=list(dict.fromkeys(files))[:10],
        related_finding_ids=[],
        raw_output_snippet=_most_relevant_output(result),
    )


def _cluster_install(result: CommandResult) -> FailureCluster:
    """Parse npm/yarn install failures."""
    text = (result.stdout or "") + "\n" + (result.stderr or "")
    errors: list[str] = []

    for m in _NPM_ERR_RE.finditer(text):
        err = m.group(1).strip()
        if err and err not in errors:
            errors.append(err)

    if not errors:
        for m in _GENERIC_ERR_RE.finditer(text):
            err = m.group(1).strip()
            if err and err not in errors:
                errors.append(err)

    summary = (
        f"Install failed: {errors[0][:120]}"
        if errors
        else "Install failed (exit code {})".format(result.exit_code)
    )
    return FailureCluster(
        step="install",
        summary=summary,
        errors=errors[:10],
        affected_files=[],
        related_finding_ids=[],
        raw_output_snippet=_most_relevant_output(result),
    )


# ── Finding association ───────────────────────────────────────────────────────

def _associate_findings(
    clusters: list[FailureCluster],
    findings: list[MigrationFinding],
) -> None:
    """
    Associate migration findings with clusters by matching affected files
    and keyword overlap.  Mutates cluster.related_finding_ids in place.
    """
    for cluster in clusters:
        related: list[str] = []
        cluster_text = " ".join(cluster.errors + cluster.affected_files).lower()
        for finding in findings:
            # File overlap
            for af in finding.affected_files:
                af_norm = af.replace("\\", "/").lower()
                if any(af_norm in cf.replace("\\", "/").lower() for cf in cluster.affected_files):
                    if finding.id not in related:
                        related.append(finding.id)
                    break
            # Keyword overlap — check finding title/reason words in cluster output
            if finding.id not in related:
                title_words = set(re.findall(r"\w{4,}", finding.title.lower()))
                if title_words & set(re.findall(r"\w{4,}", cluster_text)):
                    related.append(finding.id)
        cluster.related_finding_ids = related


# ── Public entry point ────────────────────────────────────────────────────────

def extract_failure_clusters(
    verification: VerificationResult,
    findings: list[MigrationFinding],
) -> list[FailureCluster]:
    """
    Parse failed steps in *verification* and return structured FailureClusters.

    Only processes steps that actually failed (exit_code != 0 and not SKIPPED).
    Associates each cluster with relevant MigrationFindings where possible.
    """
    clusters: list[FailureCluster] = []

    step_parsers = {
        "install": _cluster_install,
        "build": _cluster_build,
        "test": _cluster_test,
        "lint": _cluster_lint,
    }

    for step_name, parser in step_parsers.items():
        result: Optional[CommandResult] = getattr(verification, step_name)
        if result is None:
            continue
        if result.status in (StepStatus.PASSED, StepStatus.SKIPPED, StepStatus.NOT_RUN):
            continue
        cluster = parser(result)
        clusters.append(cluster)

    _associate_findings(clusters, findings)
    return clusters


### 🤖 Assistant

> 🔧 called: write_file



> 🔧 **write_file** — """
Watsonx Failure Diagnosis — Session 5.

Sends compact failure context to Watsonx and parses a structured diagnosis.

Input:  FailureCluster list + MigrationPlan + git diff + baseline comparison
Output: DiagnosisResult per cluster (root cause, repair recommendation, status)

Reuses the existing WatsonxClient.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from app.models.finding import FindingStatus
from app.models.migration_plan import MigrationPlan
from app.models.verification import VerificationResult
from app.services.failure_clustering import FailureCluster
from app.services.watsonx_client import WatsonxClient, WatsonxError

logger = logging.getLogger(__name__)

# Cap on diff snippet sent to Watsonx (characters)
_MAX_DIFF_CHARS = 3000
# Cap on source snippet per file (characters)
_MAX_SNIPPET_CHARS = 800


# ── Output model ──────────────────────────────────────────────────────────────

@dataclass
class RepairSuggestion:
    """A targeted repair recommended by Watsonx for one cluster."""

    file: str                         # file to modify (relative path)
    description: str                  # what change to make
    patch_hint: str                   # brief code or pattern to apply


@dataclass
class DiagnosisResult:
    """Structured Watsonx diagnosis for one failure cluster."""

    step: str
    root_cause: str
    migration_relevant: bool
    affected_files: list[str]
    repair_suggestions: list[RepairSuggestion]
    requires_human_review: bool
    confidence: str                   # "HIGH" | "MEDIUM" | "LOW"
    raw_response: str = ""            # kept for traceability


# ── Prompt construction ───────────────────────────────────────────────────────

def _compact_findings(plan: MigrationPlan) -> list[dict]:
    """Return a compact list of finding dicts for the prompt."""
    return [
        {
            "id": f.id,
            "type": f.type.value,
            "severity": f.severity.value,
            "title": f.title,
            "required_action": f.required_action,
            "affected_files": f.affected_files[:3],
        }
        for f in plan.findings
    ]


def _compact_cluster(cluster: FailureCluster) -> dict:
    """Convert a FailureCluster to a compact dict for the prompt."""
    return {
        "step": cluster.step,
        "summary": cluster.summary,
        "errors": cluster.errors[:10],
        "affected_files": cluster.affected_files[:5],
        "related_finding_ids": cluster.related_finding_ids[:5],
        "output_snippet": cluster.raw_output_snippet[:_MAX_SNIPPET_CHARS],
    }


def _diff_snippet(git_diff: Optional[str]) -> str:
    if not git_diff:
        return "(no diff available)"
    return git_diff[:_MAX_DIFF_CHARS]


def _baseline_summary(verification: VerificationResult) -> dict:
    return {
        "baseline_test_total": verification.baseline_test_total,
        "baseline_test_passed": verification.baseline_test_passed,
        "current_regressions": verification.regression_count,
        "regression_details": verification.regression_details[:5],
    }


def _build_diagnosis_prompt(
    cluster: FailureCluster,
    plan: MigrationPlan,
    verification: VerificationResult,
    git_diff: Optional[str],
) -> str:
    ctx = {
        "migration": {
            "package": plan.package,
            "from_version": plan.from_version,
            "to_version": plan.to_version,
            "findings": _compact_findings(plan),
        },
        "failure_cluster": _compact_cluster(cluster),
        "baseline_comparison": _baseline_summary(verification),
        "git_diff_snippet": _diff_snippet(git_diff),
    }

    return f"""You are a software migration diagnostician analyzing a failed verification step after a {plan.package} migration.

## Context
{json.dumps(ctx, indent=2)}

## Instructions
Diagnose this failure and respond with ONLY a JSON object:
{{
  "root_cause": "<concise root cause, 1-2 sentences>",
  "migration_relevant": true | false,
  "affected_files": ["<relative file path>"],
  "repair_suggestions": [
    {{
      "file": "<relative file path>",
      "description": "<what to change>",
      "patch_hint": "<code snippet or pattern>"
    }}
  ],
  "requires_human_review": true | false,
  "confidence": "HIGH" | "MEDIUM" | "LOW"
}}

Rules:
- If the failure is NOT related to the migration, set migration_relevant=false and requires_human_review=true.
- Only suggest repairs that are targeted and safe — single-file, low-risk changes.
- If the fix requires understanding complex business logic, set requires_human_review=true.
- Limit repair_suggestions to at most 3 items.
- Output ONLY the JSON object. No markdown, no explanation outside the JSON.
"""


# ── Response parsing ──────────────────────────────────────────────────────────

def _extract_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?\s*", "", text).replace("```", "").strip()
    start = text.find("{")
    if start == -1:
        raise ValueError(f"No JSON found in Watsonx output: {text[:200]}")
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start: i + 1])
    raise ValueError(f"Incomplete JSON in Watsonx output: {text[:200]}")


def _parse_diagnosis(raw: dict, cluster: FailureCluster) -> DiagnosisResult:
    suggestions: list[RepairSuggestion] = []
    for s in raw.get("repair_suggestions", []):
        if isinstance(s, dict):
            suggestions.append(
                RepairSuggestion(
                    file=str(s.get("file", "")),
                    description=str(s.get("description", "")),
                    patch_hint=str(s.get("patch_hint", "")),
                )
            )

    return DiagnosisResult(
        step=cluster.step,
        root_cause=str(raw.get("root_cause", "Unknown root cause")),
        migration_relevant=bool(raw.get("migration_relevant", False)),
        affected_files=raw.get("affected_files", cluster.affected_files)[:10],
        repair_suggestions=suggestions[:3],
        requires_human_review=bool(raw.get("requires_human_review", True)),
        confidence=str(raw.get("confidence", "LOW")).upper(),
    )


# ── Public entry point ────────────────────────────────────────────────────────

def diagnose_failures(
    clusters: list[FailureCluster],
    plan: MigrationPlan,
    verification: VerificationResult,
    git_diff: Optional[str],
) -> list[DiagnosisResult]:
    """
    For each migration-relevant failure cluster, call Watsonx for a diagnosis.

    Clusters that look like pre-existing failures (no related findings, not
    regression-listed) are given a cheap default diagnosis without calling
    Watsonx, to conserve tokens.

    Returns one DiagnosisResult per cluster.
    """
    if not clusters:
        return []

    client = WatsonxClient()
    results: list[DiagnosisResult] = []

    for cluster in clusters:
        # Only call Watsonx for clusters with related findings OR regressions
        is_regression = any(
            cluster.step in detail
            for detail in verification.regression_details
        )
        has_finding_link = bool(cluster.related_finding_ids)

        if not (is_regression or has_finding_link):
            # Return a cheap deterministic diagnosis
            logger.info(
                "Cluster step=%s has no migration link — skipping Watsonx call",
                cluster.step,
            )
            results.append(
                DiagnosisResult(
                    step=cluster.step,
                    root_cause=(
                        f"{cluster.step} failure does not appear related to the migration. "
                        "May be a pre-existing issue."
                    ),
                    migration_relevant=False,
                    affected_files=cluster.affected_files,
                    repair_suggestions=[],
                    requires_human_review=True,
                    confidence="LOW",
                )
            )
            continue

        prompt = _build_diagnosis_prompt(cluster, plan, verification, git_diff)
        logger.info("Calling Watsonx to diagnose %s failure", cluster.step)

        try:
            raw_text = client.generate(prompt, max_new_tokens=800)
            raw_dict = _extract_json(raw_text)
            diagnosis = _parse_diagnosis(raw_dict, cluster)
            diagnosis.raw_response = raw_text[:500]
            results.append(diagnosis)
            logger.info(
                "Diagnosis for %s: migration_relevant=%s requires_human_review=%s confidence=%s",
                cluster.step,
                diagnosis.migration_relevant,
                diagnosis.requires_human_review,
                diagnosis.confidence,
            )
        except WatsonxError as exc:
            logger.warning("Watsonx call failed for cluster %s: %s", cluster.step, exc)
            results.append(
                DiagnosisResult(
                    step=cluster.step,
                    root_cause=f"Watsonx diagnosis unavailable: {exc}",
                    migration_relevant=True,
                    affected_files=cluster.affected_files,
                    repair_suggestions=[],
                    requires_human_review=True,
                    confidence="LOW",
                )
            )
        except (ValueError, json.JSONDecodeError) as exc:
            logger.warning("Could not parse Watsonx diagnosis for cluster %s: %s", cluster.step, exc)
            results.append(
                DiagnosisResult(
                    step=cluster.step,
                    root_cause=f"Diagnosis parse error: {exc}",
                    migration_relevant=True,
                    affected_files=cluster.affected_files,
                    repair_suggestions=[],
                    requires_human_review=True,
                    confidence="LOW",
                )
            )

    return results


### 🤖 Assistant

> 🔧 called: write_file

Now create the repair service:

> 🔧 **write_file** — """
Targeted Repair Service — Session 5.

Applies safe, targeted fixes inside the Twin workspace based on DiagnosisResults.

Rules:
- Only modifies the Twin workspace.  Never touches the original repository.
- Only applies repairs that are:
    * Targeting a single, clearly-identified file
    * A simple search-and-replace patch (patch_hint contains old→new text or a clear instruction)
    * Non-destructive (the file exists and is readable)
- All other diagnoses are marked REQUIRES_HUMAN_REVIEW without attempting repair.

After each repair attempt the caller is expected to re-run verification.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.models.finding import FindingStatus
from app.models.migration_plan import MigrationPlan
from app.services.diagnosis import DiagnosisResult, RepairSuggestion

logger = logging.getLogger(__name__)

# Patch hint patterns we recognise as safe to apply automatically
# Format: "OLD_TEXT → NEW_TEXT" or "replace OLD with NEW"
_ARROW_RE = re.compile(r"^(.+?)\s*(?:→|->|=>)\s*(.+)$", re.DOTALL)
_REPLACE_RE = re.compile(
    r"replace\s+['\"`]?(.+?)['\"`]?\s+with\s+['\"`]?(.+?)['\"`]?\s*$",
    re.IGNORECASE | re.DOTALL,
)


# ── Result model ──────────────────────────────────────────────────────────────

@dataclass
class RepairOutcome:
    """Result of attempting a repair for one DiagnosisResult."""

    step: str
    applied: bool
    changed_files: list[str]
    notes: str
    requires_human_review: bool


# ── Helpers ───────────────────────────────────────────────────────────────────

def _resolve_file(twin_path: Path, file_hint: str) -> Optional[Path]:
    """
    Try to resolve a file path relative to the Twin root.
    Handles both forward and back slashes, and normalises ./prefixes.
    """
    if not file_hint:
        return None
    # Normalise separators
    normalised = file_hint.replace("\\", "/").lstrip("./")
    candidate = twin_path / normalised
    if candidate.is_file():
        return candidate

    # Try a glob search for the filename
    fname = Path(normalised).name
    if fname:
        skip_dirs = {"node_modules", ".git", "dist", "build", ".next", "coverage"}
        for found in twin_path.rglob(fname):
            if not any(p in skip_dirs for p in found.parts):
                return found
    return None


def _apply_patch_hint(content: str, patch_hint: str) -> Optional[str]:
    """
    Attempt to apply a patch hint to *content*.

    Recognises:
    - "old → new" (arrow notation)
    - "replace 'old' with 'new'"

    Returns the new content on success, None if the pattern could not be applied.
    """
    patch_hint = patch_hint.strip()

    # Arrow notation
    m = _ARROW_RE.match(patch_hint)
    if m:
        old, new = m.group(1).strip(), m.group(2).strip()
        # Strip surrounding quotes
        old = old.strip("'\"` ")
        new = new.strip("'\"` ")
        if old and old in content:
            return content.replace(old, new, 1)
        return None

    # "replace X with Y"
    m = _REPLACE_RE.match(patch_hint)
    if m:
        old, new = m.group(1).strip(), m.group(2).strip()
        if old and old in content:
            return content.replace(old, new, 1)
        return None

    return None


def _is_safe_suggestion(suggestion: RepairSuggestion) -> bool:
    """
    Return True only when the suggestion is concrete enough to apply safely:
    - Has a file path
    - Has a non-empty patch_hint that encodes an old→new substitution
    """
    if not suggestion.file or not suggestion.patch_hint:
        return False
    ph = suggestion.patch_hint.strip()
    # Must contain an arrow or "replace ... with ..." pattern
    if _ARROW_RE.match(ph) or _REPLACE_RE.match(ph):
        return True
    return False


# ── Public entry point ────────────────────────────────────────────────────────

def apply_repairs(
    twin_path: Path,
    diagnoses: list[DiagnosisResult],
) -> list[RepairOutcome]:
    """
    Attempt to apply targeted repairs inside the Twin for each diagnosis.

    For diagnoses with clear, safe repair suggestions: apply them.
    For all others: record as REQUIRES_HUMAN_REVIEW without guessing.

    Returns one RepairOutcome per DiagnosisResult.
    Never raises — errors are captured in RepairOutcome.notes.
    """
    outcomes: list[RepairOutcome] = []

    for diagnosis in diagnoses:
        # Don't attempt repair if Watsonx said human review is needed
        if diagnosis.requires_human_review:
            outcomes.append(
                RepairOutcome(
                    step=diagnosis.step,
                    applied=False,
                    changed_files=[],
                    notes=f"Marked REQUIRES_HUMAN_REVIEW: {diagnosis.root_cause}",
                    requires_human_review=True,
                )
            )
            continue

        # No suggestions → human review
        if not diagnosis.repair_suggestions:
            outcomes.append(
                RepairOutcome(
                    step=diagnosis.step,
                    applied=False,
                    changed_files=[],
                    notes="No repair suggestions provided by diagnosis.",
                    requires_human_review=True,
                )
            )
            continue

        # Attempt each safe suggestion
        changed_files: list[str] = []
        repair_notes: list[str] = []
        any_human_review = False

        for suggestion in diagnosis.repair_suggestions:
            if not _is_safe_suggestion(suggestion):
                repair_notes.append(
                    f"Skipped unsafe suggestion for {suggestion.file!r}: "
                    f"patch_hint not in recognised format"
                )
                any_human_review = True
                continue

            target = _resolve_file(twin_path, suggestion.file)
            if target is None:
                repair_notes.append(
                    f"File not found in Twin: {suggestion.file!r}"
                )
                any_human_review = True
                continue

            try:
                content = target.read_text(encoding="utf-8", errors="ignore")
                new_content = _apply_patch_hint(content, suggestion.patch_hint)
                if new_content is None:
                    repair_notes.append(
                        f"Patch pattern not found in {suggestion.file!r}: "
                        f"{suggestion.patch_hint[:80]}"
                    )
                    any_human_review = True
                    continue

                target.write_text(new_content, encoding="utf-8")
                rel = str(target.relative_to(twin_path))
                changed_files.append(rel)
                repair_notes.append(
                    f"Applied repair to {rel}: {suggestion.description}"
                )
                logger.info("Repair applied: %s — %s", rel, suggestion.description)

            except Exception as exc:
                repair_notes.append(
                    f"Error applying repair to {suggestion.file!r}: {exc}"
                )
                any_human_review = True
                logger.warning("Repair error for %s: %s", suggestion.file, exc)

        outcomes.append(
            RepairOutcome(
                step=diagnosis.step,
                applied=bool(changed_files),
                changed_files=changed_files,
                notes="; ".join(repair_notes) or "No repairs applied.",
                requires_human_review=any_human_review and not changed_files,
            )
        )

    return outcomes


### 🤖 Assistant

> 🔧 called: update_todo_list

Now add models for the repair/diagnosis records and update the store:

> 🔧 **update_todo_list** — [x] Read and understand existing codebase (Sessions 1-4)
[x] Create verification service (run install/build/test/lint inside Twin, compare with baseline)
[x] Create failure clustering service (parse logs, group failures, map to files/findings)
[x] Create Watsonx diagnosis service (compact prompt, structured diagnosis response)
[x] Create repair service (apply targeted fixes inside Twin, mark ambiguous as REQUIRES_HUMAN_REVIEW)
[-] Add persistence for verification results and repair records to store.py
[ ] Wire up the verify/diagnose/repair pipeline in a new background task
[ ] Add API endpoint POST /api/rehearsals/{id}/verify to the rehearsals router
[ ] Update RehearsalResponse to include verification result
[ ] Minimal regression check


### 🤖 Assistant

> 🔧 called: write_file

Now I need a persisted model for the diagnosis+repair run, then update store.py:

> 🔧 **write_file** — """
VerificationRun model — Session 5.

A VerificationRun persists the complete result of one verify → diagnose → repair
cycle.  Multiple runs can exist per rehearsal (round 1 = post-migration,
round 2 = post-repair).

Persisted as verification_run_{round}.json under the rehearsal directory.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.models.verification import VerificationResult


class RepairRecord(BaseModel):
    """Persisted record of a single repair attempt."""

    step: str
    applied: bool
    changed_files: list[str] = Field(default_factory=list)
    notes: str = ""
    requires_human_review: bool = False


class DiagnosisRecord(BaseModel):
    """Persisted diagnosis for one failure cluster."""

    step: str
    root_cause: str
    migration_relevant: bool = False
    affected_files: list[str] = Field(default_factory=list)
    requires_human_review: bool = True
    confidence: str = "LOW"
    repair_applied: bool = False
    repair_notes: str = ""


class VerificationRun(BaseModel):
    """
    One complete verify → diagnose → repair cycle.

    round=1  post-migration verification
    round=2  post-repair verification
    """

    rehearsal_id: str
    round: int = Field(default=1)

    verification: VerificationResult
    diagnoses: list[DiagnosisRecord] = Field(default_factory=list)
    repairs: list[RepairRecord] = Field(default_factory=list)

    # Final outcome for this round
    passed: bool = Field(default=False)
    requires_human_review: bool = Field(default=False)
    summary: Optional[str] = None


### 🤖 Assistant

> 🔧 called: apply_diff

Now extend store.py with VerificationRun persistence:

> 🔧 **apply_diff** — backend/app/services/store.py

### 🤖 Assistant

> 🔧 called: insert_content



> 🔧 **insert_content** — backend/app/services/store.py

### 🤖 Assistant

> 🔧 called: update_todo_list

Now wire up the full pipeline and add the `/verify` endpoint to the rehearsals API:

> 🔧 **update_todo_list** — [x] Read and understand existing codebase (Sessions 1-4)
[x] Create verification service (run install/build/test/lint inside Twin, compare with baseline)
[x] Create failure clustering service (parse logs, group failures, map to files/findings)
[x] Create Watsonx diagnosis service (compact prompt, structured diagnosis response)
[x] Create repair service (apply targeted fixes inside Twin, mark ambiguous as REQUIRES_HUMAN_REVIEW)
[x] Add persistence for verification results and repair records to store.py
[-] Wire up the verify/diagnose/repair pipeline in a new background task
[ ] Add API endpoint POST /api/rehearsals/{id}/verify to the rehearsals router
[ ] Update RehearsalResponse to include verification result
[ ] Minimal regression check


### 🤖 Assistant

> 🔧 called: apply_diff

Now add the pipeline and endpoint to `rehearsals.py`:

> 🔧 **apply_diff** — backend/app/api/rehearsals.py

### 🤖 Assistant

> 🔧 called: read_file

Now add the VerifyResponse model and the pipeline function + endpoint. Let me read the current state of the file to know the exact line numbers:

> 🔧 **read_file** — backend/app/api/rehearsals.py

### 🤖 Assistant

> 🔧 called: apply_diff



> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:79
-------
class MigrateResponse(BaseModel):
    """Response from POST /api/rehearsals/{id}/migrate."""

    rehearsal_id: str
    twin_result: TwinResult


# ── Background pipelines ───────────────────────────────────────────────────────
=======
class MigrateResponse(BaseModel):
    """Response from POST /api/rehearsals/{id}/migrate."""

    rehearsal_id: str
    twin_result: TwinResult


class VerifyResponse(BaseModel):
    """Response from POST /api/rehearsals/{id}/verify."""

    rehearsal_id: str
    verification_run: VerificationRun


# ── Background pipelines ───────────────────────────────────────────────────────
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: read_file

Now add the verify pipeline function. Let me find the exact location to insert it:

> 🔧 **read_file** — backend/app/api/rehearsals.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — backend/app/api/rehearsals.py

### 🤖 Assistant

> 🔧 called: apply_diff



> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:196
-------
        # Do NOT clean up the twin on unexpected failure — preserve for diagnosis.


def _run_intake_pipeline(
=======
        # Do NOT clean up the twin on unexpected failure — preserve for diagnosis.


def _run_verify_pipeline(rehearsal_id: str) -> None:
    """
    Synchronous pipeline: VERIFYING → DIAGNOSING → REPAIRING → VERIFYING → FINALIZING.

    Flow:
      1. Run verification (install/build/test/lint) inside the existing Twin.
      2. Extract failure clusters from failed steps.
      3. For migration-relevant failures: call Watsonx diagnosis.
      4. Apply safe targeted repairs inside the Twin.
      5. Re-run verification (round 2).
      6. Set final rehearsal status: VERIFIED or REQUIRES_HUMAN_REVIEW.

    The original workspace is never modified.
    """
    try:
        rehearsal = store.load_rehearsal(rehearsal_id)
        if rehearsal is None:
            logger.error("_run_verify_pipeline: rehearsal %s not found", rehearsal_id)
            return

        twin = store.load_twin_result(rehearsal_id)
        if twin is None:
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message="No twin result found. Run /migrate first.",
            )
            return

        baseline = store.load_baseline(rehearsal_id)
        if baseline is None:
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message="No baseline found. Re-run the full rehearsal.",
            )
            return

        profile = store.load_repo_profile(rehearsal_id)
        if profile is None:
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message="No repository profile found.",
            )
            return

        plan = store.load_migration_plan(rehearsal_id)
        twin_path = Path(twin.twin_path)
        if not twin_path.exists():
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message=f"Twin path no longer exists: {twin.twin_path}",
            )
            return

        from app.models.verification import VerificationContext

        # ── Round 1: VERIFYING ───────────────────────────────────────────────
        store.update_rehearsal_stage(rehearsal_id, RehearsalStage.VERIFYING)
        ver1 = verification_svc.run_verification(
            twin_path=twin_path,
            profile=profile,
            rehearsal_id=rehearsal_id,
            baseline=baseline,
            context=VerificationContext.POST_MIGRATION,
            round_num=1,
        )

        run1 = VerificationRun(
            rehearsal_id=rehearsal_id,
            round=1,
            verification=ver1,
        )

        if ver1.passed and ver1.regression_count == 0:
            # Migration passed cleanly — no diagnosis needed
            run1.passed = True
            run1.summary = "All checks passed after migration. No regressions detected."
            store.save_verification_run(run1)
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.COMPLETE,
                status=RehearsalStatus.COMPLETE,
            )
            logger.info("Rehearsal %s: VERIFIED after round 1", rehearsal_id)
            return

        # ── DIAGNOSING ────────────────────────────────────────────────────────
        store.update_rehearsal_stage(rehearsal_id, RehearsalStage.DIAGNOSING)

        findings = plan.findings if plan else []
        clusters = clustering_svc.extract_failure_clusters(ver1, findings)
        logger.info(
            "Rehearsal %s: %d failure cluster(s) extracted", rehearsal_id, len(clusters)
        )

        diagnoses_raw = diagnosis_svc.diagnose_failures(
            clusters=clusters,
            plan=plan or _empty_plan(rehearsal_id),
            verification=ver1,
            git_diff=twin.git_diff,
        )

        # Convert to persisted records
        diagnosis_records: list[DiagnosisRecord] = [
            DiagnosisRecord(
                step=d.step,
                root_cause=d.root_cause,
                migration_relevant=d.migration_relevant,
                affected_files=d.affected_files,
                requires_human_review=d.requires_human_review,
                confidence=d.confidence,
            )
            for d in diagnoses_raw
        ]
        run1.diagnoses = diagnosis_records

        # ── REPAIRING ─────────────────────────────────────────────────────────
        repairable = [d for d in diagnoses_raw if not d.requires_human_review and d.migration_relevant]

        repair_records: list[RepairRecord] = []

        if repairable:
            store.update_rehearsal_stage(rehearsal_id, RehearsalStage.REPAIRING)
            outcomes = repair_svc.apply_repairs(twin_path, repairable)
            for outcome in outcomes:
                repair_records.append(
                    RepairRecord(
                        step=outcome.step,
                        applied=outcome.applied,
                        changed_files=outcome.changed_files,
                        notes=outcome.notes,
                        requires_human_review=outcome.requires_human_review,
                    )
                )
                if outcome.applied:
                    # Update diagnosis record with repair result
                    for dr in run1.diagnoses:
                        if dr.step == outcome.step:
                            dr.repair_applied = True
                            dr.repair_notes = outcome.notes
        else:
            logger.info("Rehearsal %s: no repairable diagnoses", rehearsal_id)

        run1.repairs = repair_records
        store.save_verification_run(run1)

        any_repair_applied = any(r.applied for r in repair_records)

        if not any_repair_applied:
            # Nothing was repaired — determine final status from diagnoses
            all_human_review = all(d.requires_human_review for d in diagnoses_raw)
            run1.requires_human_review = True
            run1.passed = False
            run1.summary = (
                f"{ver1.regression_count} regression(s). "
                "No safe targeted repairs available — human review required."
            )
            store.save_verification_run(run1)
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.REQUIRES_HUMAN_REVIEW,
                status=RehearsalStatus.REQUIRES_HUMAN_REVIEW,
            )
            logger.info("Rehearsal %s: REQUIRES_HUMAN_REVIEW (no repairs applied)", rehearsal_id)
            return

        # ── Round 2: VERIFYING (post-repair) ─────────────────────────────────
        store.update_rehearsal_stage(rehearsal_id, RehearsalStage.VERIFYING)
        ver2 = verification_svc.run_verification(
            twin_path=twin_path,
            profile=profile,
            rehearsal_id=rehearsal_id,
            baseline=baseline,
            context=VerificationContext.POST_REPAIR,
            round_num=2,
        )

        run2 = VerificationRun(
            rehearsal_id=rehearsal_id,
            round=2,
            verification=ver2,
            diagnoses=run1.diagnoses,
            repairs=run1.repairs,
        )

        if ver2.passed and ver2.regression_count == 0:
            run2.passed = True
            run2.summary = "All checks passed after targeted repair."
            store.save_verification_run(run2)
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.COMPLETE,
                status=RehearsalStatus.COMPLETE,
            )
            logger.info("Rehearsal %s: VERIFIED after repair (round 2)", rehearsal_id)
        else:
            run2.requires_human_review = True
            remaining = ver2.regression_count
            run2.summary = (
                f"{remaining} regression(s) remain after repair attempt. "
                "Human review required."
            )
            store.save_verification_run(run2)
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.REQUIRES_HUMAN_REVIEW,
                status=RehearsalStatus.REQUIRES_HUMAN_REVIEW,
            )
            logger.info(
                "Rehearsal %s: REQUIRES_HUMAN_REVIEW after repair (%d regressions remain)",
                rehearsal_id,
                remaining,
            )

    except Exception as exc:
        logger.exception("Unexpected error in _run_verify_pipeline for %s", rehearsal_id)
        store.update_rehearsal_stage(
            rehearsal_id,
            RehearsalStage.FAILED,
            status=RehearsalStatus.FAILED,
            error_message=str(exc),
        )


def _empty_plan(rehearsal_id: str):
    """Return a minimal MigrationPlan stub when none exists."""
    from app.models.migration_plan import MigrationPlan
    return MigrationPlan(rehearsal_id=rehearsal_id, package="unknown", to_version="unknown")


def _run_intake_pipeline(
=======
        # Do NOT clean up the twin on unexpected failure — preserve for diagnosis.


def _run_verify_pipeline(rehearsal_id: str) -> None:
    """
    Synchronous pipeline: VERIFYING → DIAGNOSING → REPAIRING → VERIFYING → FINALIZING.

    Flow:
      1. Run verification (install/build/test/lint) inside the existing Twin.
      2. Extract failure clusters from failed steps.
      3. For migration-relevant failures: call Watsonx diagnosis.
      4. Apply safe targeted repairs inside the Twin.
      5. Re-run verification (round 2).
      6. Set final rehearsal status: VERIFIED or REQUIRES_HUMAN_REVIEW.

    The original workspace is never modified.
    """
    try:
        rehearsal = store.load_rehearsal(rehearsal_id)
        if rehearsal is None:
            logger.error("_run_verify_pipeline: rehearsal %s not found", rehearsal_id)
            return

        twin = store.load_twin_result(rehearsal_id)
        if twin is None:
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message="No twin result found. Run /migrate first.",
            )
            return

        baseline = store.load_baseline(rehearsal_id)
        if baseline is None:
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message="No baseline found. Re-run the full rehearsal.",
            )
            return

        profile = store.load_repo_profile(rehearsal_id)
        if profile is None:
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message="No repository profile found.",
            )
            return

        plan = store.load_migration_plan(rehearsal_id)
        twin_path = Path(twin.twin_path)
        if not twin_path.exists():
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message=f"Twin path no longer exists: {twin.twin_path}",
            )
            return

        from app.models.verification import VerificationContext

        # ── Round 1: VERIFYING ───────────────────────────────────────────────
        store.update_rehearsal_stage(rehearsal_id, RehearsalStage.VERIFYING)
        ver1 = verification_svc.run_verification(
            twin_path=twin_path,
            profile=profile,
            rehearsal_id=rehearsal_id,
            baseline=baseline,
            context=VerificationContext.POST_MIGRATION,
            round_num=1,
        )

        run1 = VerificationRun(
            rehearsal_id=rehearsal_id,
            round=1,
            verification=ver1,
        )

        if ver1.passed and ver1.regression_count == 0:
            # Migration passed cleanly — no diagnosis needed
            run1.passed = True
            run1.summary = "All checks passed after migration. No regressions detected."
            store.save_verification_run(run1)
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.COMPLETE,
                status=RehearsalStatus.COMPLETE,
            )
            logger.info("Rehearsal %s: VERIFIED after round 1", rehearsal_id)
            return

        # ── DIAGNOSING ────────────────────────────────────────────────────────
        store.update_rehearsal_stage(rehearsal_id, RehearsalStage.DIAGNOSING)

        findings = plan.findings if plan else []
        clusters = clustering_svc.extract_failure_clusters(ver1, findings)
        logger.info(
            "Rehearsal %s: %d failure cluster(s) extracted", rehearsal_id, len(clusters)
        )

        diagnoses_raw = diagnosis_svc.diagnose_failures(
            clusters=clusters,
            plan=plan if plan else _empty_plan(rehearsal_id),
            verification=ver1,
            git_diff=twin.git_diff,
        )

        # Convert to persisted records
        diagnosis_records: list[DiagnosisRecord] = [
            DiagnosisRecord(
                step=d.step,
                root_cause=d.root_cause,
                migration_relevant=d.migration_relevant,
                affected_files=d.affected_files,
                requires_human_review=d.requires_human_review,
                confidence=d.confidence,
            )
            for d in diagnoses_raw
        ]
        run1.diagnoses = diagnosis_records

        # ── REPAIRING ─────────────────────────────────────────────────────────
        repairable = [d for d in diagnoses_raw if not d.requires_human_review and d.migration_relevant]

        repair_records: list[RepairRecord] = []

        if repairable:
            store.update_rehearsal_stage(rehearsal_id, RehearsalStage.REPAIRING)
            outcomes = repair_svc.apply_repairs(twin_path, repairable)
            for outcome in outcomes:
                repair_records.append(
                    RepairRecord(
                        step=outcome.step,
                        applied=outcome.applied,
                        changed_files=outcome.changed_files,
                        notes=outcome.notes,
                        requires_human_review=outcome.requires_human_review,
                    )
                )
                if outcome.applied:
                    for dr in run1.diagnoses:
                        if dr.step == outcome.step:
                            dr.repair_applied = True
                            dr.repair_notes = outcome.notes
        else:
            logger.info("Rehearsal %s: no repairable diagnoses", rehearsal_id)

        run1.repairs = repair_records
        store.save_verification_run(run1)

        any_repair_applied = any(r.applied for r in repair_records)

        if not any_repair_applied:
            run1.requires_human_review = True
            run1.passed = False
            run1.summary = (
                f"{ver1.regression_count} regression(s). "
                "No safe targeted repairs available — human review required."
            )
            store.save_verification_run(run1)
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.REQUIRES_HUMAN_REVIEW,
                status=RehearsalStatus.REQUIRES_HUMAN_REVIEW,
            )
            logger.info("Rehearsal %s: REQUIRES_HUMAN_REVIEW (no repairs applied)", rehearsal_id)
            return

        # ── Round 2: VERIFYING (post-repair) ─────────────────────────────────
        store.update_rehearsal_stage(rehearsal_id, RehearsalStage.VERIFYING)
        ver2 = verification_svc.run_verification(
            twin_path=twin_path,
            profile=profile,
            rehearsal_id=rehearsal_id,
            baseline=baseline,
            context=VerificationContext.POST_REPAIR,
            round_num=2,
        )

        run2 = VerificationRun(
            rehearsal_id=rehearsal_id,
            round=2,
            verification=ver2,
            diagnoses=run1.diagnoses,
            repairs=run1.repairs,
        )

        if ver2.passed and ver2.regression_count == 0:
            run2.passed = True
            run2.summary = "All checks passed after targeted repair."
            store.save_verification_run(run2)
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.COMPLETE,
                status=RehearsalStatus.COMPLETE,
            )
            logger.info("Rehearsal %s: VERIFIED after repair (round 2)", rehearsal_id)
        else:
            run2.requires_human_review = True
            remaining = ver2.regression_count
            run2.summary = (
                f"{remaining} regression(s) remain after repair attempt. "
                "Human review required."
            )
            store.save_verification_run(run2)
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.REQUIRES_HUMAN_REVIEW,
                status=RehearsalStatus.REQUIRES_HUMAN_REVIEW,
            )
            logger.info(
                "Rehearsal %s: REQUIRES_HUMAN_REVIEW after repair (%d regressions remain)",
                rehearsal_id,
                remaining,
            )

    except Exception as exc:
        logger.exception("Unexpected error in _run_verify_pipeline for %s", rehearsal_id)
        store.update_rehearsal_stage(
            rehearsal_id,
            RehearsalStage.FAILED,
            status=RehearsalStatus.FAILED,
            error_message=str(exc),
        )


def _empty_plan(rehearsal_id: str):
    """Return a minimal MigrationPlan stub when none exists."""
    from app.models.migration_plan import MigrationPlan
    return MigrationPlan(rehearsal_id=rehearsal_id, package="unknown", to_version="unknown")


def _run_intake_pipeline(
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — backend/app/api/rehearsals.py

### 🤖 Assistant

> 🔧 called: insert_content

I'll use `insert_content` to add the pipeline function between lines 197 and 198:

> 🔧 **insert_content** — backend/app/api/rehearsals.py

### 🤖 Assistant

> 🔧 called: read_file

Now add the `/verify` endpoint and update the `get_rehearsal` handler to include verification_run. Let me find the end of the file:

> 🔧 **read_file** — backend/app/api/rehearsals.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — backend/app/api/rehearsals.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — backend/app/api/rehearsals.py

### 🤖 Assistant

> 🔧 called: apply_diff

Now I'll update the `get_rehearsal` handler to include verification_run, and append the `/verify` endpoint:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:598
-------
    profile = store.load_repo_profile(rehearsal_id)
    baseline = store.load_baseline(rehearsal_id)
    migration_plan = store.load_migration_plan(rehearsal_id)
    twin_result = store.load_twin_result(rehearsal_id)

    return RehearsalResponse(
        rehearsal=rehearsal,
        repo_profile=profile,
        baseline=baseline,
        migration_plan=migration_plan,
        twin_result=twin_result,
    )
=======
    profile = store.load_repo_profile(rehearsal_id)
    baseline = store.load_baseline(rehearsal_id)
    migration_plan = store.load_migration_plan(rehearsal_id)
    twin_result = store.load_twin_result(rehearsal_id)
    verification_run = store.load_latest_verification_run(rehearsal_id)

    return RehearsalResponse(
        rehearsal=rehearsal,
        repo_profile=profile,
        baseline=baseline,
        migration_plan=migration_plan,
        twin_result=twin_result,
        verification_run=verification_run,
    )
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:725
-------
    logger.info("Queued twin+migrate background task for rehearsal %s", rehearsal_id)
    return MigrateResponse(rehearsal_id=rehearsal_id, twin_result=stub)
=======
    logger.info("Queued twin+migrate background task for rehearsal %s", rehearsal_id)
    return MigrateResponse(rehearsal_id=rehearsal_id, twin_result=stub)


@router.post("/{rehearsal_id}/verify", response_model=VerifyResponse, status_code=202)
async def verify_rehearsal(
    rehearsal_id: str,
    background_tasks: BackgroundTasks,
) -> VerifyResponse:
    """
    Run verification → diagnosis → repair inside the existing Twin.

    Requires a migrated Twin (POST /migrate must have completed successfully).

    The pipeline runs in the background:
      VERIFYING → DIAGNOSING → REPAIRING → VERIFYING → COMPLETE / REQUIRES_HUMAN_REVIEW

    Poll GET /api/rehearsals/{id} for results (check rehearsal.stage / status
    and verification_run in the response).

    The original repository is NEVER modified.
    """
    rehearsal = store.load_rehearsal(rehearsal_id)
    if rehearsal is None:
        raise HTTPException(status_code=404, detail=f"Rehearsal '{rehearsal_id}' not found.")

    twin = store.load_twin_result(rehearsal_id)
    if twin is None:
        raise HTTPException(
            status_code=422,
            detail="No twin result found. Run POST /migrate first.",
        )

    if not twin.twin_path:
        raise HTTPException(
            status_code=422,
            detail="Twin path is empty — migration may still be running. Try again shortly.",
        )

    if not Path(twin.twin_path).exists():
        raise HTTPException(
            status_code=422,
            detail=(
                f"Twin workspace at {twin.twin_path!r} no longer exists. "
                "Re-run /migrate to create a fresh Twin."
            ),
        )

    if store.load_baseline(rehearsal_id) is None:
        raise HTTPException(
            status_code=422,
            detail="No baseline found. The rehearsal baseline may not have completed.",
        )

    background_tasks.add_task(_run_verify_pipeline, rehearsal_id)

    logger.info("Queued verify pipeline for rehearsal %s", rehearsal_id)

    # Return a stub VerificationRun immediately; the real result appears after polling.
    from app.models.verification import VerificationContext, VerificationResult
    stub_run = VerificationRun(
        rehearsal_id=rehearsal_id,
        round=0,
        verification=VerificationResult(
            rehearsal_id=rehearsal_id,
            context=VerificationContext.POST_MIGRATION,
            round=0,
        ),
        summary="Verification queued — background task started.",
    )
    return VerifyResponse(rehearsal_id=rehearsal_id, verification_run=stub_run)
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: apply_diff

Now update the models `__init__.py` to export the new types:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:34
-------
from app.models.twin import TwinResult, TwinMethod, MigrationStatus, ChangedFile
from app.models.verification import VerificationResult, VerificationContext
=======
from app.models.twin import TwinResult, TwinMethod, MigrationStatus, ChangedFile
from app.models.verification import VerificationResult, VerificationContext
from app.models.verification_run import VerificationRun, DiagnosisRecord, RepairRecord
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:64
-------
    # Verification
    "VerificationResult",
    "VerificationContext",
]
=======
    # Verification
    "VerificationResult",
    "VerificationContext",
    # Verification Run (Session 5)
    "VerificationRun",
    "DiagnosisRecord",
    "RepairRecord",
]
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: execute_command

Now let's run validation to make sure everything imports cleanly:

> 🔧 **execute_command** — cd backend; python -c "from app.api.rehearsals import router; print('rehearsals OK')" 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python -c "from app.api.rehearsals import router; print('rehearsals OK')"

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python -c "
from app.services.verification import run_verification
from app.services.failure_clustering import extract_failure_clusters
from app.services.diagnosis import diagnose_failures
from app.services.repair import apply_repairs
from app.models.verification_run import VerificationRun, DiagnosisRecord, RepairRecord
from app.services.store import save_verification_run, load_verification_run, load_latest_verification_run
print('All Session 5 imports OK')
"

### 🤖 Assistant

> 🔧 called: execute_command

All imports clean. Let's now run a broader import check across the whole app:

> 🔧 **execute_command** — python -c "
import app.models
import app.services.store
import app.services.verification
import app.services.failure_clustering
import app.services.diagnosis
import app.services.repair
import app.api.rehearsals
print('Full app import OK')
"

### 🤖 Assistant

> 🔧 called: execute_command

Let's also verify that the FastAPI app itself starts without errors:

> 🔧 **execute_command** — python -c "
from app.main import app
print('FastAPI app OK, routes:')
for route in app.routes:
    if hasattr(route, 'path'):
        methods = getattr(route, 'methods', set())
        print(f'  {list(methods)} {route.path}')
"

### 🤖 Assistant

> 🔧 called: execute_command

All 6 rehearsal endpoints are registered including the new `/verify`. Now let me run a quick unit-level smoke test on the failure clustering and repair logic (no network/Watsonx needed):

> 🔧 **execute_command** — python -c "
from app.models.baseline import CommandResult, StepStatus
from app.models.verification import VerificationResult, VerificationContext
from app.models.finding import MigrationFinding, FindingType, FindingSeverity, FindingStatus
from app.services.failure_clustering import extract_failure_clusters

# Build a synthetic failed verification result
ver = VerificationResult(
    rehearsal_id='test-123',
    context=VerificationContext.POST_MIGRATION,
    round=1,
)
ver.build = CommandResult(
    step='build',
    command='npm run build',
    exit_code=1,
    stdout='',
    stderr='src/index.tsx(5,3): error TS2345: Argument of type Element is not assignable',
    status=StepStatus.FAILED,
)
ver.test = CommandResult(
    step='test',
    command='npm run test',
    exit_code=1,
    stdout='● App renders correctly\n\n  TypeError: createRoot is not a function\n\nTests: 0 passed, 1 failed, 1 total',
    stderr='',
    status=StepStatus.FAILED,
)
ver.install = CommandResult(step='install', command='npm install', exit_code=0, status=StepStatus.PASSED)
ver.lint = CommandResult(step='lint', command='npm run lint', exit_code=0, status=StepStatus.SKIPPED)
ver.regression_count = 2
ver.regression_details = ['build: regression (was PASSED, now FAILED)', 'test: 1 new failure(s)']

finding = MigrationFinding(
    type=FindingType.BREAKING_CHANGE,
    severity=FindingSeverity.HIGH,
    title='ReactDOM.render removed',
    reason='React 18 removed ReactDOM.render',
    required_action='Use createRoot',
    affected_files=['src/index.tsx'],
    status=FindingStatus.PROPOSED,
)

clusters = extract_failure_clusters(ver, [finding])
print(f'Clusters: {len(clusters)}')
for c in clusters:
    print(f'  step={c.step} summary={c.summary!r}')
    print(f'  errors={c.errors[:2]}')
    print(f'  affected_files={c.affected_files}')
    print(f'  related_finding_ids={c.related_finding_ids}')
print('Failure clustering smoke test PASSED')
"

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python -c "
from app.services.repair import apply_repairs, _apply_patch_hint, _is_safe_suggestion, RepairSuggestion
from app.services.diagnosis import DiagnosisResult

# Test patch hint parsing
cases = [
    ('ReactDOM.render -> createRoot', 'old -> new format'),
    ('replace ReactDOM.render with createRoot', 'replace ... with format'),
    ('something vague without arrow', 'should be rejected'),
]
for hint, desc in cases:
    s = RepairSuggestion(file='src/index.tsx', description=desc, patch_hint=hint)
    safe = _is_safe_suggestion(s)
    print(f'  safe={safe}  hint={hint!r}')

# Test actual patch application
content = 'import ReactDOM from \"react-dom\";\nReactDOM.render(<App />, document.getElementById(\"root\"));\n'
new = _apply_patch_hint(content, 'ReactDOM.render -> createRoot')
if new is None:
    # Arrow pointing at token not literally in file — expected, regex only matches literal strings
    print('Patch hint arrow: None (ok — literal not found)')
else:
    print(f'Patch applied: {repr(new[:60])}')

# Direct string replacement
new2 = _apply_patch_hint('foo bar baz', 'foo -> qux')
print(f'Simple replace: {repr(new2)}')
print('Repair smoke test PASSED')
"

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python -c "
from app.services.repair import _apply_patch_hint, _is_safe_suggestion, RepairSuggestion

# Test safe suggestion detection
s1 = RepairSuggestion(file='src/index.tsx', description='fix', patch_hint='foo -> bar')
s2 = RepairSuggestion(file='src/index.tsx', description='fix', patch_hint='replace foo with bar')
s3 = RepairSuggestion(file='src/index.tsx', description='fix', patch_hint='rewrite the whole module')
print('arrow safe:', _is_safe_suggestion(s1))
print('replace safe:', _is_safe_suggestion(s2))
print('vague unsafe:', _is_safe_suggestion(s3))

# Test patch application
result = _apply_patch_hint('hello world foo', 'foo -> baz')
print('arrow patch result:', repr(result))

result2 = _apply_patch_hint('hello world foo', 'replace foo with qux')
print('replace patch result:', repr(result2))

result3 = _apply_patch_hint('hello world', 'notfound -> baz')
print('missing pattern:', result3)

print('Repair logic smoke test PASSED')
"

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python -c "
# Test the verification service test-summary parser
from app.services.verification import _parse_test_summary
from app.models.baseline import CommandResult, StepStatus

# Jest style
r1 = CommandResult(step='test', command='npm run test', exit_code=1,
    stdout='Tests: 176 passed, 8 failed, 184 total\nTest Suites: 2 failed, 10 passed',
    status=StepStatus.FAILED)
s1 = _parse_test_summary(r1)
print(f'Jest parser: passed={s1.passed} failed={s1.failed} total={s1.total}')

# Vitest style
r2 = CommandResult(step='test', command='npm run test', exit_code=1,
    stdout='10 passed | 2 failed',
    status=StepStatus.FAILED)
s2 = _parse_test_summary(r2)
print(f'Vitest parser: passed={s2.passed} failed={s2.failed} total={s2.total}')

# Nothing parseable
r3 = CommandResult(step='test', command='npm run test', exit_code=1,
    stdout='some random output',
    status=StepStatus.FAILED)
s3 = _parse_test_summary(r3)
print(f'Unparseable: {s3}')
print('Verification summary parser PASSED')
"

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python -c "
# Test the regression computation
from app.models.baseline import BaselineResult, CommandResult, StepStatus, TestRunSummary
from app.models.verification import VerificationResult, VerificationContext
from app.services.verification import _compute_regressions

baseline = BaselineResult(rehearsal_id='test')
baseline.test = CommandResult(step='test', command='npm run test', exit_code=0, status=StepStatus.PASSED)
baseline.test_summary = TestRunSummary(total=184, passed=184, failed=0)
baseline.build = CommandResult(step='build', command='npm run build', exit_code=0, status=StepStatus.PASSED)

ver = VerificationResult(rehearsal_id='test', context=VerificationContext.POST_MIGRATION, round=1)
ver.build = CommandResult(step='build', command='npm run build', exit_code=1, status=StepStatus.FAILED)
ver.test = CommandResult(step='test', command='npm run test', exit_code=1, status=StepStatus.FAILED)
ver.test_summary = TestRunSummary(total=184, passed=176, failed=8)

_compute_regressions(ver, baseline)
print(f'regression_count={ver.regression_count}')
print(f'regression_details={ver.regression_details}')
print(f'baseline_test_total={ver.baseline_test_total}')
assert ver.regression_count == 2, f'Expected 2, got {ver.regression_count}'
print('Regression computation PASSED')
"

### 🤖 Assistant

> 🔧 called: read_file

The regression detection found 3 — it's double-counting "test failed" once for the step status and once for the test count delta. Let me fix this to avoid double-reporting a test step failure and test count delta for the same step:

> 🔧 **read_file** — backend/app/services/verification.py

### 🤖 Assistant

> 🔧 called: apply_diff

The issue: when the test step went from PASSED to FAILED and we also have a test count delta, we're reporting both. The step-level regression is more informative than the count when the whole step failed. Fix: only report count delta when the test step itself didn't already count as a regression:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:87
-------
    regressions: list[str] = []

    for step_name in ("install", "build", "test", "lint"):
        ver_step: Optional[CommandResult] = getattr(ver, step_name)
        base_step: Optional[CommandResult] = getattr(baseline, step_name)

        if ver_step is None or ver_step.status == StepStatus.SKIPPED:
            continue
        if base_step is None or base_step.status == StepStatus.SKIPPED:
            # No baseline for this step — treat as a new failure
            if ver_step.status == StepStatus.FAILED:
                regressions.append(f"{step_name}: FAILED (no baseline)")
            continue

        # Both were run — compare
        if base_step.status == StepStatus.PASSED and ver_step.status == StepStatus.FAILED:
            regressions.append(f"{step_name}: regression (was PASSED, now FAILED)")

    # Test count regression
    if ver.test_summary and baseline.test_summary:
        b = baseline.test_summary
        v = ver.test_summary
        if v.failed > b.failed:
            delta = v.failed - b.failed
            regressions.append(
                f"test: {delta} new failure(s) "
                f"({v.passed}/{v.total} passing vs baseline {b.passed}/{b.total})"
            )
=======
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
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: execute_command

Wait — the test step did fail (test_step_already_regressed=True), so the count delta entry is suppressed. But the count detail is still useful information when the step passed but individual tests failed (partial failure scenario). The fix is correct: when the whole step regressed, no need to also show count delta. But when the step *passed* but some tests failed (which can happen with Vitest sometimes returning exit 0), we want the count delta. Let me verify the fix works correctly:

> 🔧 **execute_command** — python -c "
from app.models.baseline import BaselineResult, CommandResult, StepStatus, TestRunSummary
from app.models.verification import VerificationResult, VerificationContext
from app.services.verification import _compute_regressions

# Case 1: test step fully fails (was PASS now FAIL) + count delta — should give 2 regressions
baseline = BaselineResult(rehearsal_id='test')
baseline.test = CommandResult(step='test', command='npm run test', exit_code=0, status=StepStatus.PASSED)
baseline.test_summary = TestRunSummary(total=184, passed=184, failed=0)
baseline.build = CommandResult(step='build', command='npm run build', exit_code=0, status=StepStatus.PASSED)

ver = VerificationResult(rehearsal_id='test', context=VerificationContext.POST_MIGRATION, round=1)
ver.build = CommandResult(step='build', command='npm run build', exit_code=1, status=StepStatus.FAILED)
ver.test = CommandResult(step='test', command='npm run test', exit_code=1, status=StepStatus.FAILED)
ver.test_summary = TestRunSummary(total=184, passed=176, failed=8)

_compute_regressions(ver, baseline)
print(f'Case 1: count={ver.regression_count} details={ver.regression_details}')
assert ver.regression_count == 2, f'Expected 2, got {ver.regression_count}'

# Case 2: test step passes (exit 0) but 3 fewer passing tests — should give 1 regression (count delta)
ver2 = VerificationResult(rehearsal_id='test', context=VerificationContext.POST_MIGRATION, round=1)
ver2.build = CommandResult(step='build', command='npm run build', exit_code=0, status=StepStatus.PASSED)
ver2.test = CommandResult(step='test', command='npm run test', exit_code=0, status=StepStatus.PASSED)
ver2.test_summary = TestRunSummary(total=184, passed=181, failed=3)
_compute_regressions(ver2, baseline)
print(f'Case 2: count={ver2.regression_count} details={ver2.regression_details}')
assert ver2.regression_count == 1

# Case 3: everything passes cleanly
ver3 = VerificationResult(rehearsal_id='test', context=VerificationContext.POST_MIGRATION, round=1)
ver3.build = CommandResult(step='build', command='npm run build', exit_code=0, status=StepStatus.PASSED)
ver3.test = CommandResult(step='test', command='npm run test', exit_code=0, status=StepStatus.PASSED)
ver3.test_summary = TestRunSummary(total=184, passed=184, failed=0)
_compute_regressions(ver3, baseline)
print(f'Case 3: count={ver3.regression_count} details={ver3.regression_details}')
assert ver3.regression_count == 0
print('All regression cases PASSED')
"

### 🤖 Assistant

> 🔧 called: execute_command

All regression detection cases are correct. Let's do a final comprehensive check:

> 🔧 **execute_command** — python -c "
# Full end-to-end model + service smoke test (no external calls)
import pathlib, tempfile

# Test VerificationRun round-trip persistence
from app.models.baseline import BaselineResult, CommandResult, StepStatus, TestRunSummary
from app.models.verification import VerificationResult, VerificationContext
from app.models.verification_run import VerificationRun, DiagnosisRecord, RepairRecord

ver = VerificationResult(
    rehearsal_id='r1',
    context=VerificationContext.POST_MIGRATION,
    round=1,
    passed=False,
    regression_count=1,
    regression_details=['build: regression'],
)

diag = DiagnosisRecord(
    step='build',
    root_cause='React 18 API change',
    migration_relevant=True,
    affected_files=['src/index.tsx'],
    requires_human_review=False,
    confidence='HIGH',
)

rep = RepairRecord(
    step='build',
    applied=True,
    changed_files=['src/index.tsx'],
    notes='Applied createRoot migration',
    requires_human_review=False,
)

run = VerificationRun(
    rehearsal_id='r1',
    round=1,
    verification=ver,
    diagnoses=[diag],
    repairs=[rep],
    passed=False,
    requires_human_review=False,
    summary='Test summary',
)

# Round-trip through JSON
json_str = run.model_dump_json()
run2 = VerificationRun.model_validate_json(json_str)
assert run2.rehearsal_id == 'r1'
assert run2.round == 1
assert len(run2.diagnoses) == 1
assert run2.diagnoses[0].root_cause == 'React 18 API change'
assert run2.repairs[0].applied is True
print('VerificationRun round-trip PASSED')

# Test store persistence
import os, tempfile
from unittest.mock import patch

with tempfile.TemporaryDirectory() as tmpdir:
    with patch('app.services.store.get_settings') as mock_settings:
        mock_settings.return_value.data_dir = tmpdir
        from app.services import store
        store.save_verification_run(run)
        loaded = store.load_verification_run('r1', 1)
        assert loaded is not None
        assert loaded.round == 1
        latest = store.load_latest_verification_run('r1')
        assert latest is not None
        print('Store persistence PASSED')

print('All smoke tests PASSED')
"

### 🤖 Assistant

> 🔧 called: update_todo_list

All tests pass. Let me update the todo list and do a final check on the full file to make sure everything is clean:

> 🔧 **update_todo_list** — [x] Read and understand existing codebase (Sessions 1-4)
[x] Create verification service (run install/build/test/lint inside Twin, compare with baseline)
[x] Create failure clustering service (parse logs, group failures, map to files/findings)
[x] Create Watsonx diagnosis service (compact prompt, structured diagnosis response)
[x] Create repair service (apply targeted fixes inside Twin, mark ambiguous as REQUIRES_HUMAN_REVIEW)
[x] Add persistence for verification results and repair records to store.py
[x] Wire up the verify/diagnose/repair pipeline in a new background task
[x] Add API endpoint POST /api/rehearsals/{id}/verify to the rehearsals router
[x] Update RehearsalResponse to include verification result
[x] Minimal regression check


### 🤖 Assistant

Session 5 is fully implemented. Here's a summary of everything built:

---

## Session 5 — Verification + Recovery: What Was Built

### New files

**[`backend/app/services/verification.py`](backend/app/services/verification.py)**
Runs install/build/test/lint inside the Twin using the existing `_run`/`_has_script`/`_pm_bin` helpers from [`baseline.py`](backend/app/services/baseline.py). Parses Jest/Vitest test summaries. Computes regressions against the stored baseline without double-counting step-level vs. count-level failures.

**[`backend/app/services/failure_clustering.py`](backend/app/services/failure_clustering.py)**
Deterministic log parsing — no LLM. Step-specific parsers for TypeScript errors, Jest failures, ESLint errors, npm install errors. Associates clusters with existing `MigrationFinding` objects via file-path overlap and keyword matching.

**[`backend/app/services/diagnosis.py`](backend/app/services/diagnosis.py)**
Calls Watsonx only for migration-relevant failure clusters (those with related findings or confirmed regressions). Skips clusters with no migration link to conserve tokens. Returns structured `DiagnosisResult` objects with root cause, affected files, repair suggestions, and `requires_human_review`.

**[`backend/app/services/repair.py`](backend/app/services/repair.py)**
Applies only safe, targeted single-file patches. Recognises `old → new` and `replace X with Y` patch hints from Watsonx. Marks everything else `REQUIRES_HUMAN_REVIEW` without guessing.

**[`backend/app/models/verification_run.py`](backend/app/models/verification_run.py)**
`VerificationRun` persists one complete verify → diagnose → repair cycle (supports multiple rounds). Contains `DiagnosisRecord` and `RepairRecord`.

### Modified files

**[`backend/app/services/store.py`](backend/app/services/store.py)** — Added `save_verification_run`, `load_verification_run`, `load_latest_verification_run`.

**[`backend/app/api/rehearsals.py`](backend/app/api/rehearsals.py)** — Added `_run_verify_pipeline` background task (the full flow), `_empty_plan` helper, `VerifyResponse` model, `POST /{id}/verify` endpoint, and `verification_run` field on `GET /{id}` response.

**[`backend/app/models/__init__.py`](backend/app/models/__init__.py)** — Exported new types.

### Flow implemented

```
migrated Twin
  → verification round 1 (install/build/test/lint vs baseline)
  → if PASSED: → COMPLETE (VERIFIED)
  → failure clustering (deterministic parsing)
  → Watsonx diagnosis (only for migration-relevant clusters)
  → repair (safe patch hints only; ambiguous → REQUIRES_HUMAN_REVIEW)
  → if repairs applied: verification round 2
      → if PASSED: → COMPLETE (VERIFIED)
      → if still failing: → REQUIRES_HUMAN_REVIEW
  → if no repairs: → REQUIRES_HUMAN_REVIEW
```