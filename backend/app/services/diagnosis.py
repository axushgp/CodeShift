"""
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
