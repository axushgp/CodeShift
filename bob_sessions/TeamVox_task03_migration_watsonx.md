# # Session 3 - Migration Intelligence + Watsonx

Implement ONLY the minimum backend functionality required to turn an existing
CodeShift repository profile + target upgrade into a structured MigrationPlan.

First:
- Read `architecture.md`
- Inspect the existing implementation from Sessions 1 and 2
- Reuse the existing models, config, persistence, rehearsal API, and project structure
- Do not redesign or refactor unrelated code

## Core objective

Make this flow work:

RepositoryProfile
+ Target Upgrade
+ Small Migration Knowledge Set
→ Watsonx
→ validated MigrationPlan
→ stored in the rehearsal

## Implement

### 1. Migration Knowledge

Create a simple local structured file/data source for migration knowledge.

It only needs to support:
- from version
- to version
- breaking changes
- deprecated APIs
- migration actions
- manual considerations

Add only a small example relevant to the supported Node/JavaScript ecosystem.

Do NOT build RAG, embeddings, vector search, crawling, or a large knowledge base.

### 2. Watsonx Client

Create one small isolated Watsonx service.

Use the existing `CODESHIFT_` configuration for:
- API key
- project ID
- base URL
- model ID

Do not hardcode credentials.

Keep the client simple.

### 3. Migration Analysis Service

Create one service that:

1. takes the existing `RepositoryProfile`
2. takes the target upgrade
3. loads applicable migration knowledge
4. builds a compact prompt
5. calls Watsonx
6. parses the result into the existing `MigrationPlan`
7. validates the result
8. returns a clear error on invalid/unusable output

Send ONLY compact structured context to Watsonx.

Do not send the full repository.

Do NOT implement AST analysis yet.

### 4. Rehearsal Integration

Connect this to the existing rehearsal flow with the minimum possible change.

After a rehearsal has completed baseline verification, allow migration analysis to be triggered and store the resulting `MigrationPlan`.

Use the existing filesystem persistence.

Use the existing rehearsal/state structure.

Do not create a new queue, database, orchestration framework, or service architecture.

### 5. Minimal API

Add only the endpoint needed to trigger migration analysis for an existing rehearsal.

Return the resulting MigrationPlan or a useful error.

No new frontend work is required in this session.

## DO NOT IMPLEMENT

- AST analysis
- codemods
- dependency upgrades
- actual migration
- Git worktrees
- Twin
- post-migration verification
- failure clustering
- diagnosis
- repair
- AgentTaskSpec
- Agent Pack
- authentication
- GitHub OAuth
- deployment
- RAG/vector database
- additional LLMs
- frontend changes
- extensive documentation
- new test suites

Do not refactor unrelated Session 1/2 code.

## Efficiency

Keep the implementation as small as possible.

Reuse existing code.

Do not add libraries unless absolutely necessary.

Do not create abstractions for future work unless required now.

Do not write tests or documentation unless something is necessary to keep the implementation working.

Run only the existing checks needed to catch regressions.

If Watsonx credentials are unavailable, implement the real client/configuration path without inventing credentials or pretending a live call succeeded.

## Stop condition

Stop when this backend flow works:

existing rehearsal
→ RepositoryProfile + target upgrade
→ migration knowledge
→ Watsonx
→ validated MigrationPlan
→ persisted result

Do not begin Twin, migration execution, verification, diagnosis, repair, or Agent Pack work.

---

**Status:** active  **Date:** 2026-09-26

---

### 👤 User

# Session 3 - Migration Intelligence + Watsonx

Implement ONLY the minimum backend functionality required to turn an existing
CodeShift repository profile + target upgrade into a structured MigrationPlan.

First:
- Read `architecture.md`
- Inspect the existing implementation from Sessions 1 and 2
- Reuse the existing models, config, persistence, rehearsal API, and project structure
- Do not redesign or refactor unrelated code

## Core objective

Make this flow work:

RepositoryProfile
+ Target Upgrade
+ Small Migration Knowledge Set
→ Watsonx
→ validated MigrationPlan
→ stored in the rehearsal

## Implement

### 1. Migration Knowledge

Create a simple local structured file/data source for migration knowledge.

It only needs to support:
- from version
- to version
- breaking changes
- deprecated APIs
- migration actions
- manual considerations

Add only a small example relevant to the supported Node/JavaScript ecosystem.

Do NOT build RAG, embeddings, vector search, crawling, or a large knowledge base.

### 2. Watsonx Client

Create one small isolated Watsonx service.

Use the existing `CODESHIFT_` configuration for:
- API key
- project ID
- base URL
- model ID

Do not hardcode credentials.

Keep the client simple.

### 3. Migration Analysis Service

Create one service that:

1. takes the existing `RepositoryProfile`
2. takes the target upgrade
3. loads applicable migration knowledge
4. builds a compact prompt
5. calls Watsonx
6. parses the result into the existing `MigrationPlan`
7. validates the result
8. returns a clear error on invalid/unusable output

Send ONLY compact structured context to Watsonx.

Do not send the full repository.

Do NOT implement AST analysis yet.

### 4. Rehearsal Integration

Connect this to the existing rehearsal flow with the minimum possible change.

After a rehearsal has completed baseline verification, allow migration analysis to be triggered and store the resulting `MigrationPlan`.

Use the existing filesystem persistence.

Use the existing rehearsal/state structure.

Do not create a new queue, database, orchestration framework, or service architecture.

### 5. Minimal API

Add only the endpoint needed to trigger migration analysis for an existing rehearsal.

Return the resulting MigrationPlan or a useful error.

No new frontend work is required in this session.

## DO NOT IMPLEMENT

- AST analysis
- codemods
- dependency upgrades
- actual migration
- Git worktrees
- Twin
- post-migration verification
- failure clustering
- diagnosis
- repair
- AgentTaskSpec
- Agent Pack
- authentication
- GitHub OAuth
- deployment
- RAG/vector database
- additional LLMs
- frontend changes
- extensive documentation
- new test suites

Do not refactor unrelated Session 1/2 code.

## Efficiency

Keep the implementation as small as possible.

Reuse existing code.

Do not add libraries unless absolutely necessary.

Do not create abstractions for future work unless required now.

Do not write tests or documentation unless something is necessary to keep the implementation working.

Run only the existing checks needed to catch regressions.

If Watsonx credentials are unavailable, implement the real client/configuration path without inventing credentials or pretending a live call succeeded.

## Stop condition

Stop when this backend flow works:

existing rehearsal
→ RepositoryProfile + target upgrade
→ migration knowledge
→ Watsonx
→ validated MigrationPlan
→ persisted result

Do not begin Twin, migration execution, verification, diagnosis, repair, or Agent Pack work.

---

### 🤖 Assistant

> 🔧 called: read_file, list_files



> 🔧 **read_file** — architecture.md

> 🔧 **list_files** — backend

### 🤖 Assistant

> 🔧 called: read_file, list_files



> 🔧 **read_file** — architecture.md

> 🔧 **list_files** — backend/app

### 🤖 Assistant

> 🔧 called: read_file, read_file, read_file



> 🔧 **read_file** — backend/app/config.py

> 🔧 **read_file** — backend/app/models/rehearsal.py

> 🔧 **read_file** — backend/app/models/migration_plan.py

### 🤖 Assistant

> 🔧 called: read_file, read_file, read_file



> 🔧 **read_file** — backend/app/models/finding.py

> 🔧 **read_file** — backend/app/models/repository_profile.py

> 🔧 **read_file** — backend/app/services/store.py

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — backend/app/main.py

> 🔧 **read_file** — backend/app/api/rehearsals.py

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — backend/pyproject.toml

> 🔧 **read_file** — backend/app/services/intake.py

### 🤖 Assistant

> 🔧 called: read_file, read_file

Now I have a thorough understanding. Let me check the existing tests quickly and then plan the implementation.

> 🔧 **read_file** — backend/tests

> 🔧 **read_file** — backend/app/config.py

### 🤖 Assistant

> 🔧 called: update_todo_list

Now I have a complete picture. Let me set up the todo list and implement everything.

> 🔧 **update_todo_list** — 
[-] Add watsonx_model_id to Settings config
[ ] Create migration knowledge data file (node/react ecosystem YAML/JSON)
[ ] Create Watsonx client service (backend/app/services/watsonx_client.py)
[ ] Create migration analysis service (backend/app/services/migration.py)
[ ] Add save/load_migration_plan to store.py
[ ] Add POST /api/rehearsals/{id}/analyze endpoint to rehearsals.py
[ ] Register new endpoint in rehearsals router (already in router)
[ ] Update RehearsalResponse to include migration_plan
[ ] Run existing tests to verify no regressions


### 🤖 Assistant

> 🔧 called: apply_diff



> 🔧 **apply_diff** — backend/app/config.py

### 🤖 Assistant

> 🔧 called: update_todo_list

Now create the migration knowledge data file:

> 🔧 **update_todo_list** — 
[x] Add watsonx_model_id to Settings config
[-] Create migration knowledge data file (node/react ecosystem YAML/JSON)
[ ] Create Watsonx client service (backend/app/services/watsonx_client.py)
[ ] Create migration analysis service (backend/app/services/migration.py)
[ ] Add save/load_migration_plan to store.py
[ ] Add POST /api/rehearsals/{id}/analyze endpoint to rehearsals.py
[ ] Update RehearsalResponse to include migration_plan
[ ] Run existing tests to verify no regressions


### 🤖 Assistant

> 🔧 called: write_file



> 🔧 **write_file** — backend/app/migration_knowledge/node/react_17_to_18.json

### 🤖 Assistant

> 🔧 called: update_todo_list

Now create the Watsonx client service:

> 🔧 **update_todo_list** — 
[x] Add watsonx_model_id to Settings config
[x] Create migration knowledge data file (node/react ecosystem YAML/JSON)
[-] Create Watsonx client service (backend/app/services/watsonx_client.py)
[ ] Create migration analysis service (backend/app/services/migration.py)
[ ] Add save/load_migration_plan to store.py
[ ] Add POST /api/rehearsals/{id}/analyze endpoint to rehearsals.py
[ ] Update RehearsalResponse to include migration_plan
[ ] Run existing tests to verify no regressions


### 🤖 Assistant

> 🔧 called: write_file



> 🔧 **write_file** — """
Watsonx client — thin wrapper around the watsonx.ai text generation REST API.

Uses CODESHIFT_ settings for all credentials and endpoints.
No credentials are hardcoded.

Raises WatsonxError on any call failure.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

# Watsonx.ai text generation endpoint path
_GENERATION_PATH = "/ml/v1/text/generation"


class WatsonxError(Exception):
    """Raised when a Watsonx API call fails."""


class WatsonxClient:
    """
    Minimal synchronous Watsonx text generation client.

    Obtains an IAM token on first use and reuses it for the session lifetime.
    For the MVP, token refresh is not implemented — restart the server to
    refresh an expired token.
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._iam_token: str | None = None

    # ── IAM authentication ─────────────────────────────────────────────────────

    def _fetch_iam_token(self) -> str:
        """Exchange the API key for an IAM bearer token."""
        api_key = self._settings.watsonx_api_key
        if not api_key:
            raise WatsonxError(
                "CODESHIFT_WATSONX_API_KEY is not set. "
                "Set it in .env or as an environment variable."
            )

        resp = httpx.post(
            "https://iam.cloud.ibm.com/identity/token",
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": api_key,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        if resp.status_code != 200:
            raise WatsonxError(
                f"IAM token fetch failed: HTTP {resp.status_code} — {resp.text[:200]}"
            )
        token = resp.json().get("access_token")
        if not token:
            raise WatsonxError("IAM response did not contain access_token.")
        return token

    def _get_token(self) -> str:
        if self._iam_token is None:
            self._iam_token = self._fetch_iam_token()
        return self._iam_token

    # ── Text generation ────────────────────────────────────────────────────────

    def generate(self, prompt: str, max_new_tokens: int = 1500) -> str:
        """
        Send a prompt to watsonx.ai and return the generated text.

        Raises WatsonxError on any failure.
        """
        settings = self._settings
        if not settings.watsonx_project_id:
            raise WatsonxError(
                "CODESHIFT_WATSONX_PROJECT_ID is not set. "
                "Set it in .env or as an environment variable."
            )

        url = settings.watsonx_url.rstrip("/") + _GENERATION_PATH
        payload: dict[str, Any] = {
            "model_id": settings.watsonx_model_id,
            "project_id": settings.watsonx_project_id,
            "input": prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": max_new_tokens,
                "repetition_penalty": 1.1,
            },
        }

        token = self._get_token()
        try:
            resp = httpx.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                params={"version": "2023-05-29"},
                timeout=60,
            )
        except httpx.TimeoutException as exc:
            raise WatsonxError("Watsonx request timed out.") from exc
        except httpx.RequestError as exc:
            raise WatsonxError(f"Watsonx request failed: {exc}") from exc

        if resp.status_code != 200:
            raise WatsonxError(
                f"Watsonx generation failed: HTTP {resp.status_code} — {resp.text[:300]}"
            )

        try:
            data = resp.json()
            text: str = data["results"][0]["generated_text"]
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            raise WatsonxError(
                f"Unexpected Watsonx response shape: {resp.text[:300]}"
            ) from exc

        logger.debug("Watsonx generated %d chars", len(text))
        return text


### 🤖 Assistant

> 🔧 called: update_todo_list

Now create the migration analysis service:

> 🔧 **update_todo_list** — 
[x] Add watsonx_model_id to Settings config
[x] Create migration knowledge data file (node/react ecosystem YAML/JSON)
[x] Create Watsonx client service (backend/app/services/watsonx_client.py)
[-] Create migration analysis service (backend/app/services/migration.py)
[ ] Add save/load_migration_plan to store.py
[ ] Add POST /api/rehearsals/{id}/analyze endpoint to rehearsals.py
[ ] Update RehearsalResponse to include migration_plan
[ ] Run existing tests to verify no regressions


### 🤖 Assistant

> 🔧 called: write_file



> 🔧 **write_file** — """
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
    Return the best-matching migration knowledge dict, or None if none found.

    Searches knowledge/<ecosystem>/  for JSON files matching
    {package}_{from}_to_{to}.json, then falls back to any file for that package.
    """
    # Normalise version strings: strip leading non-digit chars (^, ~, >=, etc.)
    def _strip(v: Optional[str]) -> str:
        if not v:
            return ""
        return re.sub(r"^[^\d]*", "", v).split(".")[0]  # major version only

    from_maj = _strip(from_version)
    to_maj = _strip(to_version)
    pkg = package.lower()

    candidates: list[Path] = []
    for ecosystem_dir in _KNOWLEDGE_DIR.iterdir():
        if not ecosystem_dir.is_dir():
            continue
        for kf in ecosystem_dir.glob("*.json"):
            stem = kf.stem.lower()
            # Exact match: react_17_to_18
            if from_maj and stem == f"{pkg}_{from_maj}_to_{to_maj}":
                return json.loads(kf.read_text(encoding="utf-8"))
            # Version-less match: file name starts with package name
            if stem.startswith(pkg):
                candidates.append(kf)

    # Use first candidate (alphabetically stable)
    if candidates:
        candidates.sort()
        data = json.loads(candidates[0].read_text(encoding="utf-8"))
        # Verify it targets the right to_version if possible
        if to_maj and str(data.get("to_version", "")).startswith(to_maj):
            return data
        # Still return it — partial knowledge is better than none
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

    plan = MigrationPlan(
        rehearsal_id=rehearsal_id,
        package=target.package,
        from_version=target.from_version,
        to_version=target.to_version,
        findings=findings,
        planned_actions=planned_actions,
        knowledge_sources=_knowledge_sources(knowledge),
        watsonx_model=model_id,
        notes=raw.get("notes"),
    )
    plan.recompute_summary()
    return plan


# ── Public entry point ─────────────────────────────────────────────────────────

def analyze(
    rehearsal_id: str,
    profile: RepositoryProfile,
    target: TargetUpgrade,
) -> MigrationPlan:
    """
    Run migration analysis for a rehearsal.

    1. Load applicable migration knowledge.
    2. Build compact prompt.
    3. Call Watsonx.
    4. Parse and validate result into a MigrationPlan.

    Raises MigrationAnalysisError on unrecoverable failure.
    Raises WatsonxError (subclass of Exception) on Watsonx credential/network issues.
    """
    settings = get_settings()

    knowledge = _load_knowledge(target.package, target.from_version, target.to_version)
    if knowledge:
        logger.info(
            "Loaded migration knowledge: %s %s→%s",
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
    try:
        raw_text = client.generate(prompt, max_new_tokens=1500)
    except WatsonxError:
        raise  # Caller decides how to surface credential / network errors

    try:
        raw_dict = _extract_json(raw_text)
    except (json.JSONDecodeError, MigrationAnalysisError) as exc:
        raise MigrationAnalysisError(
            f"Watsonx output could not be parsed as a MigrationPlan: {exc}. "
            f"Raw output (first 400 chars): {raw_text[:400]}"
        ) from exc

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


### 🤖 Assistant

> 🔧 called: update_todo_list

Now add `save_migration_plan` / `load_migration_plan` to the store:

> 🔧 **update_todo_list** — 
[x] Add watsonx_model_id to Settings config
[x] Create migration knowledge data file (node/react ecosystem YAML/JSON)
[x] Create Watsonx client service (backend/app/services/watsonx_client.py)
[x] Create migration analysis service (backend/app/services/migration.py)
[-] Add save/load_migration_plan to store.py
[ ] Add POST /api/rehearsals/{id}/analyze endpoint to rehearsals.py
[ ] Update RehearsalResponse to include migration_plan
[ ] Run existing tests to verify no regressions


### 🤖 Assistant

> 🔧 called: apply_diff



> 🔧 **apply_diff** — backend/app/services/store.py

### 🤖 Assistant

> 🔧 called: update_todo_list

Now add the analyze endpoint and update the response model:

> 🔧 **update_todo_list** — 
[x] Add watsonx_model_id to Settings config
[x] Create migration knowledge data file (node/react ecosystem YAML/JSON)
[x] Create Watsonx client service (backend/app/services/watsonx_client.py)
[x] Create migration analysis service (backend/app/services/migration.py)
[x] Add save/load_migration_plan to store.py
[-] Add POST /api/rehearsals/{id}/analyze endpoint and update RehearsalResponse
[ ] Run existing tests to verify no regressions


### 🤖 Assistant

> 🔧 called: apply_diff



> 🔧 **apply_diff** — backend/app/api/rehearsals.py

### 🤖 Assistant

> 🔧 called: update_todo_list

Now run the existing tests to verify no regressions:

> 🔧 **update_todo_list** — 
[x] Add watsonx_model_id to Settings config
[x] Create migration knowledge data file (node/react ecosystem YAML/JSON)
[x] Create Watsonx client service (backend/app/services/watsonx_client.py)
[x] Create migration analysis service (backend/app/services/migration.py)
[x] Add save/load_migration_plan to store.py
[x] Add POST /api/rehearsals/{id}/analyze endpoint and update RehearsalResponse
[-] Run existing tests to verify no regressions


### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — cd backend; .venv\Scripts\python.exe -m pytest tests/ -x -q 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — .\backend\.venv\Scripts\python.exe -m pytest backend/tests/ -x -q 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — & "backend\.venv\Scripts\python.exe" -m pytest backend/tests/ -x -q 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python -m pytest tests/ -x -q 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — Get-ChildItem backend\tests -Recurse -Filter "*.py" | Select-Object FullName

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — Get-Location

### 🤖 Assistant

> 🔧 called: execute_command

The shell's working directory is a different location than the workspace. Let me use the absolute path:

> 🔧 **execute_command** — python -m pytest tests/ -x -q 2>&1

### 🤖 Assistant

> 🔧 called: glob



> 🔧 **glob** — backend/tests/**/*.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — backend/tests

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — backend/tests/conftest.py

### 🤖 Assistant

> 🔧 called: list_files, list_files



> 🔧 **list_files** — backend/tests/integration

> 🔧 **list_files** — backend/tests/unit

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python -m pytest tests/unit/ tests/integration/ -x -q 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — Get-Location; Get-ChildItem

### 🤖 Assistant

> 🔧 called: execute_command

The `cwd` parameter isn't being respected — the shell is stuck elsewhere. Let me try a different approach using explicit paths:

> 🔧 **execute_command** — Set-Location "c:\Users\Ayush\Desktop\thezap\00-NEW-FRESH\CodeShift\backend"; python -m pytest tests/ -x -q 2>&1

### 🤖 Assistant

> 🔧 called: update_todo_list

All 46 tests pass. Let me mark the final task complete:

> 🔧 **update_todo_list** — 
[x] Add watsonx_model_id to Settings config
[x] Create migration knowledge data file (node/react ecosystem YAML/JSON)
[x] Create Watsonx client service (backend/app/services/watsonx_client.py)
[x] Create migration analysis service (backend/app/services/migration.py)
[x] Add save/load_migration_plan to store.py
[x] Add POST /api/rehearsals/{id}/analyze endpoint and update RehearsalResponse
[x] Run existing tests to verify no regressions


### 🤖 Assistant

All 46 tests pass. Here's a summary of everything implemented for Session 3:

---

## Session 3 — What was built

### 1. Migration Knowledge ([`backend/app/migration_knowledge/node/react_17_to_18.json`](backend/app/migration_knowledge/node/react_17_to_18.json))
A structured local JSON file covering React 17→18 migration: 4 breaking changes, 3 deprecated APIs, 3 migration actions, and 4 manual considerations. The knowledge loader in the migration service searches this directory tree and matches files by package + major version, with a graceful fallback to any file for the same package.

### 2. Watsonx Client ([`backend/app/services/watsonx_client.py`](backend/app/services/watsonx_client.py))
Thin `httpx`-based synchronous wrapper around the watsonx.ai text generation REST API. Uses all four `CODESHIFT_WATSONX_*` settings (api_key, project_id, url, model_id). Performs IAM token exchange on first call and reuses it. Raises `WatsonxError` — not credential-inventing, not mocked — so missing credentials produce a clear actionable error surfaced to the API caller.

Added `watsonx_model_id: str = "ibm/granite-13b-instruct-v2"` to [`backend/app/config.py`](backend/app/config.py).

### 3. Migration Analysis Service ([`backend/app/services/migration.py`](backend/app/services/migration.py))
`analyze(rehearsal_id, profile, target) → MigrationPlan`:
1. Loads matching knowledge from the local file tree
2. Builds a compact structured prompt (only relevant deps, scripts, knowledge — no full repo)
3. Calls `WatsonxClient.generate()`
4. Extracts the JSON object from the response (handles markdown fences, finds `{…}` by bracket depth)
5. Parses findings and planned actions into typed Pydantic models, skipping malformed items with a warning
6. Returns a fully validated `MigrationPlan` with `recompute_summary()` called
7. Raises `MigrationAnalysisError` on unparseable output

### 4. Persistence ([`backend/app/services/store.py`](backend/app/services/store.py))
Added `save_migration_plan(plan)` and `load_migration_plan(rehearsal_id)` — persists as `data/rehearsals/{id}/migration_plan.json`, consistent with the existing store pattern.

### 5. API endpoint ([`backend/app/api/rehearsals.py`](backend/app/api/rehearsals.py))
- **`POST /api/rehearsals/{id}/analyze`** — triggers migration analysis, advances stage to `ANALYZING`, persists the plan, returns `AnalyzeResponse`. Returns HTTP 502 on Watsonx errors, 422 on parse failures.
- **`GET /api/rehearsals/{id}`** — now also returns `migration_plan` if one exists.
- `RehearsalResponse` gains an optional `migration_plan` field.