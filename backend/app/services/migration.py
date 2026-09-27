"""
Migration Analysis Service.

Flow:
    RepositoryProfile + TargetUpgrade
    → load applicable migration knowledge
    → build compact prompt
    → call Watsonx
    → parse JSON response into MigrationPlan
    → validate
    → return MigrationPlan

No AST analysis. No RAG. No vector search.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Optional

from app.config import get_settings
from app.models.finding import FindingSeverity, FindingStatus, FindingType, MigrationFinding
from app.models.migration_plan import ActionType, MigrationPlan, PlannedAction
from app.models.rehearsal import TargetUpgrade
from app.models.repository_profile import RepositoryProfile
from app.services.watsonx_client import WatsonxClient, WatsonxError

logger = logging.getLogger(__name__)

# Where migration knowledge files live (relative to this file's package root)
_KNOWLEDGE_DIR = Path(__file__).parent.parent / "migration_knowledge"

# Severity label → enum
_SEVERITY_MAP: dict[str, FindingSeverity] = {
    "CRITICAL": FindingSeverity.CRITICAL,
    "HIGH": FindingSeverity.HIGH,
    "MEDIUM": FindingSeverity.MEDIUM,
    "LOW": FindingSeverity.LOW,
    "INFO": FindingSeverity.INFO,
}

# Action type label → enum
_ACTION_TYPE_MAP: dict[str, ActionType] = {
    "CODEMOD": ActionType.CODEMOD,
    "AST_TRANSFORM": ActionType.AST_TRANSFORM,
    "VERSION_BUMP": ActionType.VERSION_BUMP,
    "CONFIG_CHANGE": ActionType.CONFIG_CHANGE,
    "MANUAL": ActionType.MANUAL,
    "WATSONX_SEMANTIC": ActionType.WATSONX_SEMANTIC,
}


class MigrationAnalysisError(Exception):
    """Raised when migration analysis cannot produce a usable MigrationPlan."""


# ── Knowledge loading ──────────────────────────────────────────────────────────

def _load_knowledge(package: str, from_version: Optional[str], to_version: str) -> Optional[dict]:
    """
    Return the best-matching migration recipe dict, or None if none found.

    Searches knowledge/recipes/ and knowledge/node/ for recipe JSON files.
    """
    def _strip(v: Optional[str]) -> str:
        if not v:
            return ""
        return re.sub(r"^[^\d]*", "", v).split(".")[0]  # major version only

    from_maj = _strip(from_version)
    to_maj = _strip(to_version)
    pkg = package.lower()

    search_dirs = [_KNOWLEDGE_DIR / "recipes", _KNOWLEDGE_DIR / "node"]
    for sdir in search_dirs:
        if not sdir.exists():
            continue
        for kf in sdir.glob("*.json"):
            stem = kf.stem.lower()
            try:
                data = json.loads(kf.read_text(encoding="utf-8"))
            except Exception:
                continue
            # Exact match: react_17_to_18
            if from_maj and stem == f"{pkg}_{from_maj}_to_{to_maj}":
                return data
            # Version-less match
            if stem.startswith(pkg) and "breaking_changes" in data:
                if to_maj and str(data.get("to_version", "")).startswith(to_maj):
                    return data
                return data

    return None


def _knowledge_sources(knowledge: Optional[dict]) -> list[str]:
    if knowledge is None:
        return []
    return [f"{knowledge.get('package', 'unknown')} {knowledge.get('from_version', '?')}→{knowledge.get('to_version', '?')}"]


# ── Prompt construction ────────────────────────────────────────────────────────

def _build_prompt(
    profile: RepositoryProfile,
    target: TargetUpgrade,
    knowledge: Optional[dict],
) -> str:
    """
    Build a compact, structured prompt for Watsonx.

    The prompt instructs the model to produce a JSON array of findings.
    Only relevant context is included — no full file contents.
    """
    # Compact repo summary
    deps_relevant = {
        k: v
        for k, v in {**profile.dependencies, **profile.dev_dependencies}.items()
        if target.package.lower() in k.lower()
        or k.lower() in ("react", "react-dom", "next", "express", "webpack", "babel",
                          "typescript", "@types/react", "jest", "testing-library",
                          "react-query", "react-router", "react-router-dom")
    }

    repo_ctx = {
        "name": profile.name,
        "ecosystem": profile.ecosystem,
        "framework": profile.framework,
        "runtime": profile.runtime,
        "package_manager": profile.package_manager,
        "relevant_dependencies": deps_relevant,
        "test_scripts": [s.command for s in profile.test_scripts],
        "build_scripts": [s.command for s in profile.build_scripts],
    }

    upgrade_ctx = {
        "package": target.package,
        "from_version": target.from_version,
        "to_version": target.to_version,
    }

    knowledge_ctx: dict[str, Any] = {}
    if knowledge:
        knowledge_ctx = {
            "breaking_changes": [
                {"id": b["id"], "title": b["title"], "severity": b.get("severity", "HIGH"),
                 "affected_apis": b.get("affected_apis", [])}
                for b in knowledge.get("breaking_changes", [])
            ],
            "deprecated_apis": [
                {"api": d["api"], "replacement": d["replacement"], "severity": d.get("severity", "HIGH")}
                for d in knowledge.get("deprecated_apis", [])
            ],
            "manual_considerations": knowledge.get("manual_considerations", []),
        }

    prompt = f"""You are a software migration analyst. Analyze the following repository and produce a JSON migration plan.

## Repository
{json.dumps(repo_ctx, indent=2)}

## Target Upgrade
{json.dumps(upgrade_ctx, indent=2)}

## Known Migration Issues
{json.dumps(knowledge_ctx, indent=2) if knowledge_ctx else "No structured knowledge available for this upgrade."}

## Instructions
Produce a JSON object with this exact structure:
{{
  "findings": [
    {{
      "type": "<BREAKING_CHANGE|DEPRECATED_API|CONFIGURATION_CHANGE|MANUAL_MIGRATION_REQUIRED|INFORMATIONAL>",
      "severity": "<CRITICAL|HIGH|MEDIUM|LOW|INFO>",
      "title": "<short title>",
      "reason": "<why this is an issue>",
      "required_action": "<what must be done>",
      "affected_files": []
    }}
  ],
  "planned_actions": [
    {{
      "action_type": "<VERSION_BUMP|MANUAL|CONFIG_CHANGE|CODEMOD|WATSONX_SEMANTIC>",
      "description": "<what will change>",
      "target_files": []
    }}
  ],
  "notes": "<optional summary>"
}}

Rules:
- Only include findings relevant to the actual dependencies found in the repository.
- Keep findings concise and actionable.
- Do not include findings for packages not present in the repository.
- Output ONLY the JSON object. No markdown, no explanation outside the JSON.
"""
    return prompt


# ── Response parsing ───────────────────────────────────────────────────────────

def _extract_json(text: str) -> dict:
    """Extract the first JSON object from model output."""
    # Strip markdown fences if present
    text = re.sub(r"```(?:json)?\s*", "", text).strip()
    text = text.replace("```", "").strip()

    # Find the outermost { ... }
    start = text.find("{")
    if start == -1:
        raise MigrationAnalysisError(f"No JSON object found in Watsonx output: {text[:200]}")

    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start : i + 1]
                return json.loads(candidate)

    raise MigrationAnalysisError(f"Could not locate complete JSON object in output: {text[:200]}")


def _parse_plan(
    raw: dict,
    rehearsal_id: str,
    target: TargetUpgrade,
    profile: RepositoryProfile,
    knowledge: Optional[dict],
    model_id: str,
) -> MigrationPlan:
    """Convert the raw parsed dict into a validated MigrationPlan."""
    findings: list[MigrationFinding] = []
    for item in raw.get("findings", []):
        try:
            finding = MigrationFinding(
                type=FindingType(item.get("type", "INFORMATIONAL")),
                severity=_SEVERITY_MAP.get(
                    str(item.get("severity", "INFO")).upper(), FindingSeverity.INFO
                ),
                title=str(item.get("title", "Untitled finding")),
                reason=str(item.get("reason", "")),
                required_action=str(item.get("required_action", "")),
                evidence=item.get("evidence"),
                affected_files=item.get("affected_files", []),
                status=FindingStatus.PROPOSED,
            )
            findings.append(finding)
        except Exception as exc:
            logger.warning("Skipping malformed finding: %s — %s", item, exc)

    planned_actions: list[PlannedAction] = []
    for item in raw.get("planned_actions", []):
        try:
            action = PlannedAction(
                action_type=_ACTION_TYPE_MAP.get(
                    str(item.get("action_type", "MANUAL")).upper(), ActionType.MANUAL
                ),
                description=str(item.get("description", "")),
                target_files=item.get("target_files", []),
                command=item.get("command"),
            )
            planned_actions.append(action)
        except Exception as exc:
            logger.warning("Skipping malformed planned action: %s — %s", item, exc)

    fw_name = profile.framework.capitalize() if profile.framework else target.package.capitalize()
    migration_path_str = f"{fw_name} {target.from_version or '?'} -> {target.to_version}"
    recipe_id = knowledge.get("id") or knowledge.get("recipe") if knowledge else None

    plan = MigrationPlan(
        rehearsal_id=rehearsal_id,
        package=target.package,
        from_version=target.from_version,
        to_version=target.to_version,
        framework=fw_name,
        migration_path=migration_path_str,
        recipe_id=recipe_id,
        findings=findings,
        planned_actions=planned_actions,
        knowledge_sources=_knowledge_sources(knowledge),
        watsonx_model=model_id,
        notes=raw.get("notes"),
    )
    plan.recompute_summary()
    return plan


# ── Public entry point ─────────────────────────────────────────────────────────

def _knowledge_to_raw_plan(
    knowledge: dict,
    profile: RepositoryProfile,
    target: TargetUpgrade,
) -> dict:
    findings = []
    for b in knowledge.get("breaking_changes", []):
        findings.append({
            "type": "BREAKING_CHANGE",
            "severity": b.get("severity", "HIGH"),
            "title": b.get("title", ""),
            "reason": b.get("description", ""),
            "required_action": b.get("replacement", ""),
            "affected_files": [],
        })
    for d in knowledge.get("deprecated_apis", []):
        findings.append({
            "type": "DEPRECATED_API",
            "severity": d.get("severity", "HIGH"),
            "title": f"Deprecated API: {d.get('api')}",
            "reason": f"API {d.get('api')} is deprecated in {target.package} {target.to_version}.",
            "required_action": f"Replace with {d.get('replacement')}",
            "affected_files": [],
        })
    planned_actions = []
    for a in knowledge.get("migration_actions", []):
        planned_actions.append({
            "action_type": a.get("action_type", "MANUAL"),
            "description": a.get("description", ""),
            "target_files": ["package.json"] if a.get("action_type") == "VERSION_BUMP" else [],
            "command": a.get("codemod_hint"),
        })
    return {
        "findings": findings,
        "planned_actions": planned_actions,
        "notes": f"Deterministic plan derived from {knowledge.get('package')} {knowledge.get('to_version')} knowledge base.",
    }


def analyze(
    rehearsal_id: str,
    profile: RepositoryProfile,
    target: TargetUpgrade,
    is_demo: bool = False,
) -> MigrationPlan:
    """
    Run migration analysis for a rehearsal.

    1. Load applicable migration knowledge.
    2. Build compact prompt.
    3. Call Watsonx (or fall back to curated knowledge only in explicit demo mode).
    4. Parse and validate result into a MigrationPlan.
    """
    settings = get_settings()

    knowledge = _load_knowledge(target.package, target.from_version, target.to_version)
    if knowledge:
        logger.info(
            "Loaded migration knowledge: %s %s->%s",
            knowledge.get("package"),
            knowledge.get("from_version"),
            knowledge.get("to_version"),
        )
    else:
        logger.info(
            "No structured knowledge found for %s %s→%s; proceeding with profile only",
            target.package,
            target.from_version,
            target.to_version,
        )

    prompt = _build_prompt(profile, target, knowledge)
    logger.debug("Migration prompt (%d chars):\n%s", len(prompt), prompt[:500])

    client = WatsonxClient()
    raw_dict = None
    try:
        raw_text = client.generate(prompt, max_new_tokens=1500)
        try:
            raw_dict = _extract_json(raw_text)
        except (json.JSONDecodeError, MigrationAnalysisError) as exc:
            if is_demo and knowledge:
                logger.warning("Could not parse Watsonx output in demo mode; using knowledge base: %s", exc)
                raw_dict = _knowledge_to_raw_plan(knowledge, profile, target)
            else:
                raise MigrationAnalysisError(
                    f"Watsonx output could not be parsed as a MigrationPlan: {exc}. "
                    f"Raw output (first 400 chars): {raw_text[:400]}"
                ) from exc
    except WatsonxError as exc:
        if is_demo and knowledge:
            logger.info("Watsonx unavailable in demo mode (%s); using curated demo knowledge base", exc)
            raw_dict = _knowledge_to_raw_plan(knowledge, profile, target)
        else:
            raise

    plan = _parse_plan(
        raw_dict,
        rehearsal_id=rehearsal_id,
        target=target,
        profile=profile,
        knowledge=knowledge,
        model_id=settings.watsonx_model_id,
    )

    logger.info(
        "Migration analysis complete for rehearsal %s: %d findings, %d actions",
        rehearsal_id,
        plan.total_findings,
        len(plan.planned_actions),
    )
    return plan
