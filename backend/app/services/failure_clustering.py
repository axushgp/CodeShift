"""
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
        if result.status in (
            StepStatus.PASSED,
            StepStatus.SKIPPED,
            StepStatus.SKIPPED_NOT_APPLICABLE,
            StepStatus.NOT_RUN,
        ):
            continue
        cluster = parser(result)
        clusters.append(cluster)

    _associate_findings(clusters, findings)
    return clusters
