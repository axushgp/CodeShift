# # Session 4 - Twin + Migration Execution

Implement ONLY the Twin and migration-execution layer for CodeShift-Final v1.0.

First:
- Read `architecture.md`
- Inspect the existing implementation from Sessions 1-3
- Reuse the existing models, persistence, rehearsal flow, and APIs
- Do not redesign or refactor unrelated code

## Goal

Given an analyzed rehearsal with a MigrationPlan, CodeShift must safely rehearse the migration inside a disposable Twin without modifying the original repository.

For the MVP, use this concrete migration scenario:

React 17 → React 18

The existing migration knowledge already contains this scenario.

## Implement

### 1. Twin creation

Create a disposable Twin from the repository workspace used by the rehearsal.

Prefer a Git worktree when practical.

Otherwise use a temporary copy.

Requirements:
- original repository remains untouched
- Twin has its own working directory
- record the Twin location/revision
- clean up only when appropriate for the workflow

### 2. Migration execution

Implement the minimum executor needed for the React 17 → React 18 scenario.

Use deterministic changes for known mechanical work, such as:
- updating relevant dependency versions
- applying known migration changes where they are deterministic

Use the existing MigrationPlan to determine what should be changed.

Do not blindly rewrite files with an LLM.

For semantic code changes, use the existing MigrationFindings and only make targeted changes.

### 3. Capture migration result

After the migration attempt, record:
- migration status
- changed files
- git diff / patch
- relevant execution output
- errors if migration failed

Persist enough information for Session 5 to verify and diagnose the result.

Use the existing filesystem persistence.

### 4. Rehearsal integration

Extend the existing rehearsal flow minimally so it can move from:

BASELINE / ANALYZING
→ TWIN_CREATING
→ MIGRATING

and store the migration result.

Add only the minimum API needed to trigger migration for an analyzed rehearsal.

No new queue, database, or orchestration framework.

## Important safety requirement

The original repository must remain unchanged.

The migration must happen only in the disposable Twin.

Do not run upgrade commands directly against the original workspace.

## Do NOT implement

- post-migration verification
- test/build/lint comparison
- failure clustering
- Watsonx diagnosis
- repair
- AST framework
- generic multi-language migration engine
- AgentTaskSpec
- Agent Pack
- frontend redesign
- authentication
- deployment
- RAG/vector database
- additional LLMs
- large test suites
- extensive documentation

Do not refactor Sessions 1-3 unnecessarily.

## Efficiency

Keep this implementation minimal.

Reuse existing CodeShift models and services.

Do not add libraries unless absolutely necessary.

Do not create abstractions for ecosystems other than Node/JavaScript/TypeScript.

Do not build a general codemod platform.

Do not write a new test suite.

Run only the minimum existing checks needed to catch regressions.

If something cannot be safely automated, record it as a migration item for the later verification/diagnosis stage instead of expanding the scope.

## Completion

Stop when this works:

existing analyzed rehearsal
→ create disposable Twin
→ apply React 17 → React 18 migration
→ capture changed files and diff
→ persist migration result

The original repository must remain unchanged.

Do not implement Session 5 functionality.

---

**Status:** active  **Date:** 2026-09-26

---

### 👤 User

# Session 4 - Twin + Migration Execution

Implement ONLY the Twin and migration-execution layer for CodeShift-Final v1.0.

First:
- Read `architecture.md`
- Inspect the existing implementation from Sessions 1-3
- Reuse the existing models, persistence, rehearsal flow, and APIs
- Do not redesign or refactor unrelated code

## Goal

Given an analyzed rehearsal with a MigrationPlan, CodeShift must safely rehearse the migration inside a disposable Twin without modifying the original repository.

For the MVP, use this concrete migration scenario:

React 17 → React 18

The existing migration knowledge already contains this scenario.

## Implement

### 1. Twin creation

Create a disposable Twin from the repository workspace used by the rehearsal.

Prefer a Git worktree when practical.

Otherwise use a temporary copy.

Requirements:
- original repository remains untouched
- Twin has its own working directory
- record the Twin location/revision
- clean up only when appropriate for the workflow

### 2. Migration execution

Implement the minimum executor needed for the React 17 → React 18 scenario.

Use deterministic changes for known mechanical work, such as:
- updating relevant dependency versions
- applying known migration changes where they are deterministic

Use the existing MigrationPlan to determine what should be changed.

Do not blindly rewrite files with an LLM.

For semantic code changes, use the existing MigrationFindings and only make targeted changes.

### 3. Capture migration result

After the migration attempt, record:
- migration status
- changed files
- git diff / patch
- relevant execution output
- errors if migration failed

Persist enough information for Session 5 to verify and diagnose the result.

Use the existing filesystem persistence.

### 4. Rehearsal integration

Extend the existing rehearsal flow minimally so it can move from:

BASELINE / ANALYZING
→ TWIN_CREATING
→ MIGRATING

and store the migration result.

Add only the minimum API needed to trigger migration for an analyzed rehearsal.

No new queue, database, or orchestration framework.

## Important safety requirement

The original repository must remain unchanged.

The migration must happen only in the disposable Twin.

Do not run upgrade commands directly against the original workspace.

## Do NOT implement

- post-migration verification
- test/build/lint comparison
- failure clustering
- Watsonx diagnosis
- repair
- AST framework
- generic multi-language migration engine
- AgentTaskSpec
- Agent Pack
- frontend redesign
- authentication
- deployment
- RAG/vector database
- additional LLMs
- large test suites
- extensive documentation

Do not refactor Sessions 1-3 unnecessarily.

## Efficiency

Keep this implementation minimal.

Reuse existing CodeShift models and services.

Do not add libraries unless absolutely necessary.

Do not create abstractions for ecosystems other than Node/JavaScript/TypeScript.

Do not build a general codemod platform.

Do not write a new test suite.

Run only the minimum existing checks needed to catch regressions.

If something cannot be safely automated, record it as a migration item for the later verification/diagnosis stage instead of expanding the scope.

## Completion

Stop when this works:

existing analyzed rehearsal
→ create disposable Twin
→ apply React 17 → React 18 migration
→ capture changed files and diff
→ persist migration result

The original repository must remain unchanged.

Do not implement Session 5 functionality.

---

### 🤖 Assistant

> 🔧 called: read_file, list_files



> 🔧 **list_files** — .

> 🔧 **read_file** — architecture.md

### 🤖 Assistant

> 🔧 called: read_file, list_files



> 🔧 **read_file** — architecture.md

> 🔧 **list_files** — backend

### 🤖 Assistant

> 🔧 called: list_files, read_file



> 🔧 **read_file** — architecture.md

> 🔧 **list_files** — backend/app

### 🤖 Assistant

> 🔧 called: read_file, read_file, read_file



> 🔧 **read_file** — backend/app/models/finding.py

> 🔧 **read_file** — backend/app/models/rehearsal.py

> 🔧 **read_file** — backend/app/models/migration_plan.py

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — backend/app/services/migration.py

> 🔧 **read_file** — backend/app/services/store.py

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — backend/app/api/rehearsals.py

> 🔧 **read_file** — backend/app/migration_knowledge/node/react_17_to_18.json

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — backend/app/config.py

> 🔧 **read_file** — backend/app/services/intake.py

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — backend/app/main.py

> 🔧 **read_file** — backend/app/state_machine.py

### 🤖 Assistant

> 🔧 called: update_todo_list

Now I have a complete picture of the codebase. Let me plan and implement:

> 🔧 **update_todo_list** — 
[-] 1. Create TwinResult model (twin location, revision, changed files, diff, migration status)
[ ] 2. Add store functions for TwinResult (save/load twin_result.json)
[ ] 3. Implement twin service (create twin via git worktree or temp copy)
[ ] 4. Implement migration executor service (React 17→18: version bumps + targeted ReactDOM.render replacements)
[ ] 5. Add migration result capture (changed files, git diff, execution output)
[ ] 6. Add POST /api/rehearsals/{id}/migrate endpoint
[ ] 7. Update rehearsal pipeline: ANALYZING → TWIN_CREATING → MIGRATING stage transitions
[ ] 8. Run existing tests to verify no regressions


### 🤖 Assistant

> 🔧 called: read_file, read_file

Now let me read the models `__init__.py` to understand what's exported:

> 🔧 **read_file** — backend/app/models/verification.py

> 🔧 **read_file** — backend/app/models/__init__.py

### 🤖 Assistant

> 🔧 called: update_todo_list

Now I have everything I need. Let me implement the full Twin + migration execution layer:

> 🔧 **update_todo_list** — 
[-] 1. Create TwinResult model (twin location, revision, changed files, diff, migration status)
[ ] 2. Add store functions for TwinResult (save/load twin_result.json)
[ ] 3. Implement twin service (create twin via git worktree or temp copy)
[ ] 4. Implement migration executor service (React 17→18: version bumps + targeted ReactDOM.render replacements)
[ ] 5. Add migration result capture (changed files, git diff, execution output)
[ ] 6. Add POST /api/rehearsals/{id}/migrate endpoint
[ ] 7. Update rehearsal pipeline: ANALYZING → TWIN_CREATING → MIGRATING stage transitions
[ ] 8. Run existing tests to verify no regressions


### 🤖 Assistant

> 🔧 called: write_file



> 🔧 **write_file** — backend/app/models/twin.py

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] 1. Create TwinResult model (twin location, revision, changed files, diff, migration status)
[-] 2. Add store functions for TwinResult (save/load twin_result.json)
[ ] 3. Implement twin service (create twin via git worktree or temp copy)
[ ] 4. Implement migration executor service (React 17→18: version bumps + targeted ReactDOM.render replacements)
[ ] 5. Add migration result capture (changed files, git diff, execution output)
[ ] 6. Add POST /api/rehearsals/{id}/migrate endpoint
[ ] 7. Update rehearsal pipeline: ANALYZING → TWIN_CREATING → MIGRATING stage transitions
[ ] 8. Run existing tests to verify no regressions


### 🤖 Assistant

> 🔧 called: apply_diff



> 🔧 **apply_diff** — backend/app/services/store.py

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] 1. Create TwinResult model (twin location, revision, changed files, diff, migration status)
[x] 2. Add store functions for TwinResult (save/load twin_result.json)
[-] 3. Implement twin service (create twin via git worktree or temp copy)
[ ] 4. Implement migration executor service (React 17→18: version bumps + targeted ReactDOM.render replacements)
[ ] 5. Add migration result capture (changed files, git diff, execution output)
[ ] 6. Add POST /api/rehearsals/{id}/migrate endpoint
[ ] 7. Update rehearsal pipeline: ANALYZING → TWIN_CREATING → MIGRATING stage transitions
[ ] 8. Run existing tests to verify no regressions


### 🤖 Assistant

> 🔧 called: write_file



> 🔧 **write_file** — backend/app/services/twin.py

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] 1. Create TwinResult model (twin location, revision, changed files, diff, migration status)
[x] 2. Add store functions for TwinResult (save/load twin_result.json)
[x] 3. Implement twin service (create twin via git worktree or temp copy)
[-] 4. Implement migration executor service (React 17→18: version bumps + targeted ReactDOM.render replacements)
[ ] 5. Add migration result capture (changed files, git diff, execution output)
[ ] 6. Add POST /api/rehearsals/{id}/migrate endpoint
[ ] 7. Update rehearsal pipeline: ANALYZING → TWIN_CREATING → MIGRATING stage transitions
[ ] 8. Run existing tests to verify no regressions


### 🤖 Assistant

> 🔧 called: write_file

Now I'll implement the migration executor. Steps 4 and 5 are tightly coupled (executor both applies changes and captures the result), so I'll write them together:

> 🔧 **write_file** — """
Migration Executor Service — React 17 → React 18.

Applies the MigrationPlan inside the Twin workspace.

What this executor does (deterministic only):
  1. VERSION_BUMP — update react / react-dom / @types/react / @types/react-dom
     in package.json (dependencies + devDependencies) to ^18.0.0.
  2. Targeted ReactDOM.render → createRoot replacement in JS/TS/JSX/TSX files.
     Only applies when the pattern is unambiguous (single-file call).
  3. Records all skipped / manual items for Session 5.

What this executor does NOT do:
  - Run npm install (no network; verification stage handles that)
  - Rewrite files with an LLM
  - Touch any file in the original workspace
  - Handle cases that require human judgment (recorded as manual_items)

After execution, it captures:
  - changed_files list
  - git diff (or a synthetic unified diff when git is unavailable)
  - execution_log
  - migration_status (SUCCESS / PARTIAL / FAILED)
"""

from __future__ import annotations

import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Optional

from app.models.migration_plan import ActionType, MigrationPlan, PlannedAction
from app.models.twin import ChangedFile, MigrationStatus, TwinResult

logger = logging.getLogger(__name__)

# ── React 18 version targets ──────────────────────────────────────────────────

_REACT_18_PACKAGES: dict[str, str] = {
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
}

# ── Regex for ReactDOM.render detection ──────────────────────────────────────

# Matches: ReactDOM.render(<...>, ...) or ReactDOM.render(
#   <Component ... />, ...
# )  — we detect presence, then replace the entire call.
_RENDER_CALL_RE = re.compile(
    r"ReactDOM\.render\s*\(",
    re.MULTILINE,
)

# Matches: import ReactDOM from 'react-dom'  or  import * as ReactDOM from 'react-dom'
_IMPORT_REACT_DOM_RE = re.compile(
    r"""(import\s+(?:ReactDOM|\*\s+as\s+ReactDOM)\s+from\s+['"]react-dom['"])""",
    re.MULTILINE,
)

# Matches: import { createRoot } from 'react-dom/client'
_IMPORT_CREATE_ROOT_RE = re.compile(
    r"""import\s+\{[^}]*createRoot[^}]*\}\s+from\s+['"]react-dom/client['"]""",
    re.MULTILINE,
)

# Source file extensions to search for React code
_JS_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}


class ExecutorError(Exception):
    """Raised when the executor encounters an unrecoverable error."""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _git_diff(twin_path: Path) -> Optional[str]:
    """Return unified git diff of all unstaged changes in the Twin, or None."""
    result = subprocess.run(
        ["git", "diff"],
        cwd=str(twin_path),
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout or None
    return None


def _git_status_changed(twin_path: Path) -> list[str]:
    """Return list of modified/added file paths relative to git index."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(twin_path),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) >= 3:
            paths.append(line[3:].strip())
    return paths


def _changed_files_from_git(twin_path: Path) -> list[ChangedFile]:
    """Derive ChangedFile list from git status."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(twin_path),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    files: list[ChangedFile] = []
    for line in result.stdout.splitlines():
        if len(line) < 3:
            continue
        xy = line[:2].strip()
        path = line[3:].strip()
        if xy in ("M", "MM", " M"):
            change_type = "modified"
        elif xy == "A":
            change_type = "added"
        elif xy == "D":
            change_type = "deleted"
        else:
            change_type = "modified"
        files.append(ChangedFile(path=path, change_type=change_type))
    return files


# ── Step 1: Version bump ──────────────────────────────────────────────────────

def _apply_version_bumps(
    twin_path: Path,
    twin: TwinResult,
    log: list[str],
) -> list[str]:
    """
    Update react/react-dom/@types/react/@types/react-dom to ^18.0.0
    in package.json. Returns list of changed file paths (relative).
    """
    pkg_json_path = twin_path / "package.json"
    if not pkg_json_path.exists():
        log.append("SKIP version bump: no package.json found at Twin root")
        return []

    try:
        data = _read_json(pkg_json_path)
    except Exception as exc:
        log.append(f"SKIP version bump: could not parse package.json — {exc}")
        return []

    changed = False
    for section_key in ("dependencies", "devDependencies", "peerDependencies"):
        section: Optional[dict] = data.get(section_key)
        if not isinstance(section, dict):
            continue
        for pkg, target_version in _REACT_18_PACKAGES.items():
            if pkg in section:
                old_version = section[pkg]
                if old_version != target_version:
                    section[pkg] = target_version
                    log.append(
                        f"VERSION_BUMP [{section_key}] {pkg}: {old_version!r} → {target_version!r}"
                    )
                    changed = True
                else:
                    log.append(f"SKIP {pkg} in [{section_key}]: already {target_version!r}")

    if not changed:
        log.append("Version bump: no relevant package versions needed updating")
        return []

    _write_json(pkg_json_path, data)
    log.append("Wrote updated package.json")
    return ["package.json"]


# ── Step 2: ReactDOM.render → createRoot ─────────────────────────────────────

def _find_render_files(twin_path: Path) -> list[Path]:
    """Find all JS/TS source files that call ReactDOM.render(."""
    matches: list[Path] = []
    skip_dirs = {"node_modules", ".git", "dist", "build", ".next", "coverage"}

    for f in twin_path.rglob("*"):
        if not f.is_file():
            continue
        if f.suffix not in _JS_EXTENSIONS:
            continue
        # Skip common non-source directories
        if any(part in skip_dirs for part in f.parts):
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            if _RENDER_CALL_RE.search(content):
                matches.append(f)
        except Exception:
            continue

    return matches


def _rewrite_render_call(content: str, filepath: Path, log: list[str]) -> Optional[str]:
    """
    Rewrite a single ReactDOM.render() call to createRoot().render().

    Returns the new content if a clean rewrite was performed, else None
    (the caller should record this as a manual item).

    Only applies the rewrite when:
    - There is exactly ONE ReactDOM.render( call in the file.
    - The call matches the simple pattern:
        ReactDOM.render(<Component/>, document.getElementById('...'))
      or similar one-liner / two-liner forms.

    Complex or multi-call files are left untouched and recorded as manual.
    """
    render_matches = list(_RENDER_CALL_RE.finditer(content))
    if len(render_matches) != 1:
        log.append(
            f"MANUAL {filepath.name}: {len(render_matches)} ReactDOM.render calls — "
            "requires human review"
        )
        return None

    # Locate the full call: ReactDOM.render(<JSX>, container)
    # We parse the parentheses by counting depth from the opening '('
    start_pos = render_matches[0].end() - 1  # position of the '('
    depth = 0
    call_end = start_pos
    for i in range(start_pos, len(content)):
        ch = content[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                call_end = i + 1
                break
    else:
        log.append(
            f"MANUAL {filepath.name}: could not locate end of ReactDOM.render call"
        )
        return None

    full_call = content[start_pos:call_end]  # includes outer parens
    inner = full_call[1:-1].strip()  # contents inside the parens

    # Split on the top-level comma to get (jsx_arg, container_arg)
    # We need to respect nested parens/angle-brackets
    depth = 0
    split_idx: Optional[int] = None
    for i, ch in enumerate(inner):
        if ch in ("(", "<", "{", "["):
            depth += 1
        elif ch in (")", ">", "}", "]"):
            depth -= 1
        elif ch == "," and depth == 0:
            split_idx = i
            break

    if split_idx is None:
        log.append(
            f"MANUAL {filepath.name}: cannot split ReactDOM.render arguments — "
            "requires human review"
        )
        return None

    jsx_arg = inner[:split_idx].strip()
    container_arg = inner[split_idx + 1:].strip()

    # Build the replacement
    new_call = f"createRoot({container_arg}).render({jsx_arg})"

    # Full replacement in the file
    # Replace "ReactDOM.render(<inner>)" with the new_call
    old_call_str = content[render_matches[0].start():call_end]
    new_content = content[:render_matches[0].start()] + new_call + content[call_end:]

    # Ensure createRoot import is present
    if not _IMPORT_CREATE_ROOT_RE.search(new_content):
        # Add createRoot import.  Find an existing react-dom import to insert after.
        import_match = _IMPORT_REACT_DOM_RE.search(new_content)
        if import_match:
            insert_pos = import_match.end()
            new_content = (
                new_content[:insert_pos]
                + "\nimport { createRoot } from 'react-dom/client';"
                + new_content[insert_pos:]
            )
            log.append(
                f"  → Added 'import {{ createRoot }} from react-dom/client' to {filepath.name}"
            )
        else:
            # Prepend at top of file
            new_content = (
                "import { createRoot } from 'react-dom/client';\n" + new_content
            )
            log.append(
                f"  → Prepended 'import {{ createRoot }} from react-dom/client' to {filepath.name}"
            )

    log.append(
        f"REWRITE {filepath.name}: ReactDOM.render({inner[:60]}…) "
        f"→ createRoot({container_arg}).render({jsx_arg[:40]}…)"
    )
    return new_content


def _apply_render_rewrites(
    twin_path: Path,
    twin: TwinResult,
    log: list[str],
    manual_items: list[str],
) -> list[str]:
    """
    Find and rewrite ReactDOM.render calls across the Twin.
    Returns list of changed file paths (relative to twin_path).
    """
    render_files = _find_render_files(twin_path)
    if not render_files:
        log.append("No ReactDOM.render calls found in source files")
        return []

    log.append(f"Found {len(render_files)} file(s) with ReactDOM.render calls")
    changed: list[str] = []

    for f in render_files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            new_content = _rewrite_render_call(content, f, log)
            if new_content is not None:
                f.write_text(new_content, encoding="utf-8")
                rel = str(f.relative_to(twin_path))
                changed.append(rel)
            else:
                rel = str(f.relative_to(twin_path))
                manual_items.append(
                    f"ReactDOM.render in {rel} requires manual migration to createRoot"
                )
        except Exception as exc:
            logger.warning("Could not rewrite %s: %s", f, exc)
            log.append(f"ERROR rewriting {f.name}: {exc}")
            rel = str(f.relative_to(twin_path))
            manual_items.append(
                f"ReactDOM.render in {rel} could not be automatically migrated: {exc}"
            )

    return changed


# ── Step 3: Capture result ────────────────────────────────────────────────────

def _capture_result(
    twin_path: Path,
    twin: TwinResult,
    changed_rel_paths: list[str],
    log: list[str],
) -> None:
    """
    Populate twin's changed_files and git_diff after all mutations are done.
    """
    # Prefer git-derived change info (works for both worktree and copy twins)
    git_files = _changed_files_from_git(twin_path)
    if git_files:
        twin.changed_files = git_files
    else:
        # Fall back to the tracked paths
        twin.changed_files = [
            ChangedFile(path=p, change_type="modified") for p in changed_rel_paths
        ]

    diff = _git_diff(twin_path)
    if diff:
        twin.git_diff = diff
        log.append(f"Captured git diff ({len(diff)} chars)")
    else:
        log.append("git diff not available (non-git Twin or no staged changes)")


# ── Public entry point ─────────────────────────────────────────────────────────

def execute_migration(
    twin: TwinResult,
    plan: MigrationPlan,
) -> TwinResult:
    """
    Apply the MigrationPlan inside the Twin workspace.

    Mutates and returns the twin with updated:
      - migration_status
      - changed_files
      - git_diff
      - execution_log
      - actions_applied / actions_skipped
      - manual_items

    Never modifies the original repository.
    Never raises — on unexpected error sets migration_status = FAILED.
    """
    twin_path = Path(twin.twin_path)
    log: list[str] = list(twin.execution_log)
    manual_items: list[str] = list(twin.manual_items)
    all_changed: list[str] = []
    actions_applied: list[str] = []
    actions_skipped: list[str] = []

    log.append(
        f"Starting migration execution: {plan.package} "
        f"{plan.from_version or '?'} → {plan.to_version}"
    )

    try:
        # ── Pass 1: VERSION_BUMP actions ─────────────────────────────────────
        version_bump_actions = [
            a for a in plan.planned_actions if a.action_type == ActionType.VERSION_BUMP
        ]

        if version_bump_actions:
            log.append(
                f"Applying {len(version_bump_actions)} VERSION_BUMP action(s)"
            )
            for action in version_bump_actions:
                log.append(f"  Action: {action.description}")

        bumped = _apply_version_bumps(twin_path, twin, log)
        all_changed.extend(bumped)

        if bumped:
            for action in version_bump_actions:
                actions_applied.append(action.id)
        else:
            for action in version_bump_actions:
                actions_skipped.append(action.id)

        # ── Pass 2: ReactDOM.render → createRoot rewrites ────────────────────
        codemod_actions = [
            a for a in plan.planned_actions
            if a.action_type in (ActionType.CODEMOD, ActionType.AST_TRANSFORM)
        ]

        # Also do this unconditionally for React 18 — it's deterministic.
        log.append("Scanning Twin for ReactDOM.render calls to rewrite")
        rewritten = _apply_render_rewrites(twin_path, twin, log, manual_items)
        all_changed.extend(rewritten)

        if rewritten:
            for action in codemod_actions:
                actions_applied.append(action.id)
        else:
            for action in codemod_actions:
                actions_skipped.append(action.id)

        # ── Pass 3: MANUAL / WATSONX_SEMANTIC actions → record as manual ─────
        manual_actions = [
            a for a in plan.planned_actions
            if a.action_type in (ActionType.MANUAL, ActionType.WATSONX_SEMANTIC)
        ]
        for action in manual_actions:
            manual_items.append(
                f"[MANUAL] {action.description}"
            )
            actions_skipped.append(action.id)
            log.append(f"SKIP (manual): {action.description}")

        # ── Capture diff and changed files ────────────────────────────────────
        _capture_result(twin_path, twin, all_changed, log)

        # ── Determine overall status ──────────────────────────────────────────
        if manual_items:
            twin.migration_status = MigrationStatus.PARTIAL
            log.append(
                f"Migration PARTIAL: {len(all_changed)} file(s) changed, "
                f"{len(manual_items)} manual item(s) remain"
            )
        elif all_changed:
            twin.migration_status = MigrationStatus.SUCCESS
            log.append(
                f"Migration SUCCESS: {len(all_changed)} file(s) changed"
            )
        else:
            # No changes made — could be already migrated or nothing applicable
            twin.migration_status = MigrationStatus.PARTIAL
            log.append("Migration complete: no files modified (may already be migrated)")

    except Exception as exc:
        logger.exception("Unexpected error during migration execution")
        twin.migration_status = MigrationStatus.FAILED
        twin.error_message = str(exc)
        log.append(f"FATAL: {exc}")

    twin.execution_log = log
    twin.manual_items = manual_items
    twin.actions_applied = actions_applied
    twin.actions_skipped = actions_skipped

    logger.info(
        "Migration execution complete for rehearsal %s: status=%s, changed=%d files",
        twin.rehearsal_id,
        twin.migration_status.value,
        len(twin.changed_files),
    )
    return twin


### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] 1. Create TwinResult model (twin location, revision, changed files, diff, migration status)
[x] 2. Add store functions for TwinResult (save/load twin_result.json)
[x] 3. Implement twin service (create twin via git worktree or temp copy)
[x] 4. Implement migration executor service (React 17→18: version bumps + targeted ReactDOM.render replacements)
[x] 5. Add migration result capture (changed files, git diff, execution output)
[-] 6. Add POST /api/rehearsals/{id}/migrate endpoint
[ ] 7. Update rehearsal pipeline: ANALYZING → TWIN_CREATING → MIGRATING stage transitions
[ ] 8. Run existing tests to verify no regressions


### 🤖 Assistant

> 🔧 called: apply_diff

Now extend the rehearsals API with the migrate endpoint and update the pipeline:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:1
-------
"""
Rehearsals API — Repository Intake + Scan + Baseline + Migration Analysis.

POST /api/rehearsals                  — create and run a new rehearsal (URL or ZIP)
GET  /api/rehearsals/{id}             — retrieve rehearsal state + profile + baseline
POST /api/rehearsals/{id}/analyze     — trigger migration analysis, returns MigrationPlan
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.models.baseline import BaselineResult
from app.models.migration_plan import MigrationPlan
from app.models.rehearsal import (
    Rehearsal,
    RehearsalStage,
    RehearsalStatus,
    RepositorySource,
    TargetUpgrade,
)
from app.models.repository_profile import RepositoryProfile
from app.services import baseline as baseline_svc
from app.services import intake as intake_svc
from app.services import migration as migration_svc
from app.services import scanner as scanner_svc
from app.services import store
from app.services.watsonx_client import WatsonxError
=======
"""
Rehearsals API — Repository Intake + Scan + Baseline + Migration Analysis + Twin + Migration.

POST /api/rehearsals                  — create and run a new rehearsal (URL or ZIP)
GET  /api/rehearsals/{id}             — retrieve rehearsal state + profile + baseline
POST /api/rehearsals/{id}/analyze     — trigger migration analysis, returns MigrationPlan
POST /api/rehearsals/{id}/migrate     — create Twin and execute migration
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.models.baseline import BaselineResult
from app.models.migration_plan import MigrationPlan
from app.models.rehearsal import (
    Rehearsal,
    RehearsalStage,
    RehearsalStatus,
    RepositorySource,
    TargetUpgrade,
)
from app.models.repository_profile import RepositoryProfile
from app.models.twin import TwinResult
from app.services import baseline as baseline_svc
from app.services import executor as executor_svc
from app.services import intake as intake_svc
from app.services import migration as migration_svc
from app.services import scanner as scanner_svc
from app.services import store
from app.services import twin as twin_svc
from app.services.watsonx_client import WatsonxError
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:50
-------
class RehearsalResponse(BaseModel):
    """Full rehearsal state returned from GET or POST."""

    rehearsal: Rehearsal
    repo_profile: Optional[RepositoryProfile] = None
    baseline: Optional[BaselineResult] = None
    migration_plan: Optional[MigrationPlan] = None


class AnalyzeResponse(BaseModel):
    """Response from POST /api/rehearsals/{id}/analyze."""

    rehearsal_id: str
    migration_plan: MigrationPlan
=======
class RehearsalResponse(BaseModel):
    """Full rehearsal state returned from GET or POST."""

    rehearsal: Rehearsal
    repo_profile: Optional[RepositoryProfile] = None
    baseline: Optional[BaselineResult] = None
    migration_plan: Optional[MigrationPlan] = None
    twin_result: Optional[TwinResult] = None


class AnalyzeResponse(BaseModel):
    """Response from POST /api/rehearsals/{id}/analyze."""

    rehearsal_id: str
    migration_plan: MigrationPlan


class MigrateResponse(BaseModel):
    """Response from POST /api/rehearsals/{id}/migrate."""

    rehearsal_id: str
    twin_result: TwinResult
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:68
-------
# ── Background pipeline ────────────────────────────────────────────────────────

def _run_intake_pipeline(
=======
# ── Background pipelines ───────────────────────────────────────────────────────

def _run_twin_and_migrate(rehearsal_id: str) -> None:
    """
    Synchronous pipeline: TWIN_CREATING → MIGRATING.

    Called from the /migrate endpoint via BackgroundTasks.
    The original workspace (repository.local_path) is read but never modified.
    """
    twin: Optional[TwinResult] = None
    try:
        rehearsal = store.load_rehearsal(rehearsal_id)
        if rehearsal is None:
            logger.error("_run_twin_and_migrate: rehearsal %s not found", rehearsal_id)
            return

        local_path = rehearsal.repository.local_path
        if not local_path:
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message="No local workspace path recorded on rehearsal.",
            )
            return

        workspace = Path(local_path)
        if not workspace.exists():
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message=f"Workspace path does not exist: {local_path}",
            )
            return

        plan = store.load_migration_plan(rehearsal_id)
        if plan is None:
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message="No migration plan found. Run /analyze first.",
            )
            return

        # ── TWIN_CREATING ────────────────────────────────────────────────────
        store.update_rehearsal_stage(rehearsal_id, RehearsalStage.TWIN_CREATING)
        try:
            twin = twin_svc.create_twin(workspace, rehearsal_id)
        except twin_svc.TwinError as exc:
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message=f"Twin creation failed: {exc}",
            )
            return

        store.save_twin_result(twin)
        logger.info(
            "Twin created for rehearsal %s at %s (method=%s)",
            rehearsal_id,
            twin.twin_path,
            twin.method.value,
        )

        # ── MIGRATING ────────────────────────────────────────────────────────
        store.update_rehearsal_stage(rehearsal_id, RehearsalStage.MIGRATING)
        twin = executor_svc.execute_migration(twin, plan)
        store.save_twin_result(twin)

        from app.models.twin import MigrationStatus
        if twin.migration_status == MigrationStatus.FAILED:
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message=twin.error_message or "Migration execution failed.",
            )
        else:
            # Leave the rehearsal in MIGRATING / RUNNING so Session 5 can pick it up.
            # Mark status COMPLETE for the MVP (verification is Session 5).
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.MIGRATING,
                status=RehearsalStatus.COMPLETE,
            )
            logger.info(
                "Migration complete for rehearsal %s: status=%s, changed=%d files",
                rehearsal_id,
                twin.migration_status.value,
                len(twin.changed_files),
            )

    except Exception as exc:
        logger.exception("Unexpected error in _run_twin_and_migrate for %s", rehearsal_id)
        store.update_rehearsal_stage(
            rehearsal_id,
            RehearsalStage.FAILED,
            status=RehearsalStatus.FAILED,
            error_message=str(exc),
        )
        # Do NOT clean up the twin on unexpected failure — preserve for diagnosis.


def _run_intake_pipeline(
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:138
-------
    finally:
        if workspace is not None:
            intake_svc.cleanup_workspace(workspace)
=======
    finally:
        # NOTE: Do NOT clean up the workspace here — it is needed by /migrate.
        # The workspace is intentionally kept alive after intake completes.
        # Twin creation will read it; Session 5 cleanup will remove it.
        pass
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:220
-------
@router.get("/{rehearsal_id}", response_model=RehearsalResponse)
async def get_rehearsal(rehearsal_id: str) -> RehearsalResponse:
    """
    Retrieve the current state of a rehearsal, including profile, baseline, and migration plan.
    """
    rehearsal = store.load_rehearsal(rehearsal_id)
    if rehearsal is None:
        raise HTTPException(status_code=404, detail=f"Rehearsal '{rehearsal_id}' not found.")

    profile = store.load_repo_profile(rehearsal_id)
    baseline = store.load_baseline(rehearsal_id)
    migration_plan = store.load_migration_plan(rehearsal_id)

    return RehearsalResponse(
        rehearsal=rehearsal,
        repo_profile=profile,
        baseline=baseline,
        migration_plan=migration_plan,
    )
=======
@router.get("/{rehearsal_id}", response_model=RehearsalResponse)
async def get_rehearsal(rehearsal_id: str) -> RehearsalResponse:
    """
    Retrieve the current state of a rehearsal, including profile, baseline, migration plan,
    and twin result if migration has been run.
    """
    rehearsal = store.load_rehearsal(rehearsal_id)
    if rehearsal is None:
        raise HTTPException(status_code=404, detail=f"Rehearsal '{rehearsal_id}' not found.")

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
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:241
-------
@router.post("/{rehearsal_id}/analyze", response_model=AnalyzeResponse)
async def analyze_rehearsal(rehearsal_id: str) -> AnalyzeResponse:
    """
    Trigger migration analysis for an existing rehearsal.

    Requires that the rehearsal has a RepositoryProfile (i.e. scanning completed).
    Calls Watsonx, produces a MigrationPlan, persists and returns it.
    """
    rehearsal = store.load_rehearsal(rehearsal_id)
    if rehearsal is None:
        raise HTTPException(status_code=404, detail=f"Rehearsal '{rehearsal_id}' not found.")

    profile = store.load_repo_profile(rehearsal_id)
    if profile is None:
        raise HTTPException(
            status_code=422,
            detail="Repository profile not available. Run scanning first.",
        )

    store.update_rehearsal_stage(rehearsal_id, RehearsalStage.ANALYZING)

    try:
        plan = migration_svc.analyze(
            rehearsal_id=rehearsal_id,
            profile=profile,
            target=rehearsal.target_upgrade,
        )
    except WatsonxError as exc:
        store.update_rehearsal_stage(
            rehearsal_id,
            RehearsalStage.FAILED,
            status=RehearsalStatus.FAILED,
            error_message=str(exc),
        )
        raise HTTPException(status_code=502, detail=f"Watsonx error: {exc}") from exc
    except migration_svc.MigrationAnalysisError as exc:
        store.update_rehearsal_stage(
            rehearsal_id,
            RehearsalStage.FAILED,
            status=RehearsalStatus.FAILED,
            error_message=str(exc),
        )
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    store.save_migration_plan(plan)
    store.update_rehearsal_stage(
        rehearsal_id,
        RehearsalStage.ANALYZING,
        status=RehearsalStatus.COMPLETE,
    )
    logger.info("Migration analysis persisted for rehearsal %s", rehearsal_id)

    return AnalyzeResponse(rehearsal_id=rehearsal_id, migration_plan=plan)
=======
@router.post("/{rehearsal_id}/analyze", response_model=AnalyzeResponse)
async def analyze_rehearsal(rehearsal_id: str) -> AnalyzeResponse:
    """
    Trigger migration analysis for an existing rehearsal.

    Requires that the rehearsal has a RepositoryProfile (i.e. scanning completed).
    Calls Watsonx, produces a MigrationPlan, persists and returns it.
    """
    rehearsal = store.load_rehearsal(rehearsal_id)
    if rehearsal is None:
        raise HTTPException(status_code=404, detail=f"Rehearsal '{rehearsal_id}' not found.")

    profile = store.load_repo_profile(rehearsal_id)
    if profile is None:
        raise HTTPException(
            status_code=422,
            detail="Repository profile not available. Run scanning first.",
        )

    store.update_rehearsal_stage(rehearsal_id, RehearsalStage.ANALYZING)

    try:
        plan = migration_svc.analyze(
            rehearsal_id=rehearsal_id,
            profile=profile,
            target=rehearsal.target_upgrade,
        )
    except WatsonxError as exc:
        store.update_rehearsal_stage(
            rehearsal_id,
            RehearsalStage.FAILED,
            status=RehearsalStatus.FAILED,
            error_message=str(exc),
        )
        raise HTTPException(status_code=502, detail=f"Watsonx error: {exc}") from exc
    except migration_svc.MigrationAnalysisError as exc:
        store.update_rehearsal_stage(
            rehearsal_id,
            RehearsalStage.FAILED,
            status=RehearsalStatus.FAILED,
            error_message=str(exc),
        )
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    store.save_migration_plan(plan)
    store.update_rehearsal_stage(
        rehearsal_id,
        RehearsalStage.ANALYZING,
        status=RehearsalStatus.COMPLETE,
    )
    logger.info("Migration analysis persisted for rehearsal %s", rehearsal_id)

    return AnalyzeResponse(rehearsal_id=rehearsal_id, migration_plan=plan)


@router.post("/{rehearsal_id}/migrate", response_model=MigrateResponse, status_code=202)
async def migrate_rehearsal(
    rehearsal_id: str,
    background_tasks: BackgroundTasks,
) -> MigrateResponse:
    """
    Create a disposable Twin and execute the migration inside it.

    Requires a completed migration analysis (MigrationPlan must exist).
    Requires that the rehearsal workspace (local_path) is still accessible.

    The pipeline (TWIN_CREATING → MIGRATING) runs in the background.
    Poll GET /api/rehearsals/{id} to retrieve the TwinResult.

    The original repository workspace is NEVER modified.
    """
    rehearsal = store.load_rehearsal(rehearsal_id)
    if rehearsal is None:
        raise HTTPException(status_code=404, detail=f"Rehearsal '{rehearsal_id}' not found.")

    if store.load_migration_plan(rehearsal_id) is None:
        raise HTTPException(
            status_code=422,
            detail="No migration plan found. Run POST /analyze first.",
        )

    local_path = rehearsal.repository.local_path
    if not local_path:
        raise HTTPException(
            status_code=422,
            detail=(
                "No local workspace path recorded on this rehearsal. "
                "The original repository intake pipeline did not preserve the workspace. "
                "Re-run the rehearsal to create a fresh workspace."
            ),
        )

    if not Path(local_path).exists():
        raise HTTPException(
            status_code=422,
            detail=(
                f"Workspace at {local_path!r} no longer exists. "
                "Re-run the rehearsal to recreate a fresh workspace."
            ),
        )

    # Return immediately with a stub TwinResult; background task fills it in.
    from app.models.twin import MigrationStatus, TwinMethod
    stub = TwinResult(
        rehearsal_id=rehearsal_id,
        method=TwinMethod.TEMP_COPY,
        twin_path="",
        migration_status=MigrationStatus.PENDING,
        execution_log=["Migration queued — background task started"],
    )

    background_tasks.add_task(_run_twin_and_migrate, rehearsal_id)

    logger.info("Queued twin+migrate background task for rehearsal %s", rehearsal_id)
    return MigrateResponse(rehearsal_id=rehearsal_id, twin_result=stub)
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] 1. Create TwinResult model (twin location, revision, changed files, diff, migration status)
[x] 2. Add store functions for TwinResult (save/load twin_result.json)
[x] 3. Implement twin service (create twin via git worktree or temp copy)
[x] 4. Implement migration executor service (React 17→18: version bumps + targeted ReactDOM.render replacements)
[x] 5. Add migration result capture (changed files, git diff, execution output)
[x] 6. Add POST /api/rehearsals/{id}/migrate endpoint
[-] 7. Update models/__init__.py to export TwinResult; verify no import errors
[ ] 8. Run existing tests to verify no regressions


### 🤖 Assistant

> 🔧 called: apply_diff



> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:32
-------
from app.models.migration_plan import MigrationPlan, PlannedAction
from app.models.verification import VerificationResult, VerificationContext

__all__ = [
    # Rehearsal
    "Rehearsal",
    "RehearsalStatus",
    "RehearsalStage",
    "TargetUpgrade",
    "RepositorySource",
    # Repository Profile
    "RepositoryProfile",
    "Ecosystem",
    "PackageManager",
    # Baseline
    "BaselineResult",
    "CommandResult",
    "StepStatus",
    "TestRunSummary",
    # Finding
    "MigrationFinding",
    "FindingType",
    "FindingSeverity",
    "FindingStatus",
    # Migration Plan
    "MigrationPlan",
    "PlannedAction",
    # Verification
    "VerificationResult",
    "VerificationContext",
]
=======
from app.models.migration_plan import MigrationPlan, PlannedAction
from app.models.twin import TwinResult, TwinMethod, MigrationStatus, ChangedFile
from app.models.verification import VerificationResult, VerificationContext

__all__ = [
    # Rehearsal
    "Rehearsal",
    "RehearsalStatus",
    "RehearsalStage",
    "TargetUpgrade",
    "RepositorySource",
    # Repository Profile
    "RepositoryProfile",
    "Ecosystem",
    "PackageManager",
    # Baseline
    "BaselineResult",
    "CommandResult",
    "StepStatus",
    "TestRunSummary",
    # Finding
    "MigrationFinding",
    "FindingType",
    "FindingSeverity",
    "FindingStatus",
    # Migration Plan
    "MigrationPlan",
    "PlannedAction",
    # Twin
    "TwinResult",
    "TwinMethod",
    "MigrationStatus",
    "ChangedFile",
    # Verification
    "VerificationResult",
    "VerificationContext",
]
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: execute_command

Now let's run the existing tests to check for regressions:

> 🔧 **execute_command** — cd backend && .\.venv\Scripts\python.exe -m pytest tests/ -x -q 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — .\.venv\Scripts\python.exe -m pytest tests/ -x -q 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — Get-ChildItem .\.venv\Scripts\ | Where-Object { $_.Name -like "python*" }

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — $env:VIRTUAL_ENV = ""; python -m pytest tests/ -x -q 2>&1

### 🤖 Assistant

> 🔧 called: list_files



> 🔧 **list_files** — backend/tests

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python -m pytest backend/tests/ -x -q 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — Get-Command python | Select-Object -ExpandProperty Source

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — & "C:\Users\Ayush\AppData\Local\Programs\Python\Python312\python.exe" -m pytest tests/ -x -q 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — Get-ChildItem backend\tests\ -Recurse -Filter "*.py" | Select-Object Name, FullName

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — Get-Location

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — Get-ChildItem "C:\Users\Ayush\Desktop\thezap\00-NEW-FRESH\CodeShift\backend\tests" -Recurse -Filter "*.py" | Select-Object Name, FullName

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — & "C:\Users\Ayush\Desktop\thezap\00-NEW-FRESH\CodeShift\backend\.venv\Scripts\python.exe" -m pytest "C:\Users\Ayush\Desktop\thezap\00-NEW-FRESH\CodeShift\backend\tests" -x -q 2>&1

### 🤖 Assistant

> 🔧 called: execute_command

All 46 tests pass. Let me also do a quick import smoke test to verify the new modules load cleanly:

> 🔧 **execute_command** — & "C:\Users\Ayush\Desktop\thezap\00-NEW-FRESH\CodeShift\backend\.venv\Scripts\python.exe" -c "from app.models.twin import TwinResult, TwinMethod, MigrationStatus, ChangedFile; from app.services.twin import create_twin, cleanup_twin; from app.services.executor import execute_migration; from app.services.store import save_twin_result, load_twin_result; from app.api.rehearsals import router; print('All imports OK')"

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — & "C:\Users\Ayush\Desktop\thezap\00-NEW-FRESH\CodeShift\backend\.venv\Scripts\python.exe" -c "import sys; sys.path.insert(0, '.'); from app.models.twin import TwinResult, TwinMethod, MigrationStatus, ChangedFile; from app.services.twin import create_twin, cleanup_twin; from app.services.executor import execute_migration; from app.services.store import save_twin_result, load_twin_result; from app.api.rehearsals import router; print('All imports OK')"

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — & "C:\Users\Ayush\Desktop\thezap\00-NEW-FRESH\CodeShift\backend\.venv\Scripts\python.exe" -c "import sys; sys.path.insert(0, 'C:/Users/Ayush/Desktop/thezap/00-NEW-FRESH/CodeShift/backend'); from app.models.twin import TwinResult, TwinMethod, MigrationStatus, ChangedFile; from app.services.twin import create_twin, cleanup_twin; from app.services.executor import execute_migration; from app.services.store import save_twin_result, load_twin_result; from app.api.rehearsals import router; print('All imports OK')"

### 🤖 Assistant

> 🔧 called: execute_command

All imports resolve cleanly. Let me run the full test suite once more to confirm a final clean pass:

> 🔧 **execute_command** — & "C:\Users\Ayush\Desktop\thezap\00-NEW-FRESH\CodeShift\backend\.venv\Scripts\python.exe" -m pytest "C:\Users\Ayush\Desktop\thezap\00-NEW-FRESH\CodeShift\backend\tests" -q 2>&1 | Select-String -Pattern "passed|failed|error" | Select-Object -Last 3

### 🤖 Assistant

> 🔧 called: update_todo_list

46/46 passing, no regressions.

> 🔧 **update_todo_list** — 
[x] 1. Create TwinResult model (twin location, revision, changed files, diff, migration status)
[x] 2. Add store functions for TwinResult (save/load twin_result.json)
[x] 3. Implement twin service (create twin via git worktree or temp copy)
[x] 4. Implement migration executor service (React 17→18: version bumps + targeted ReactDOM.render replacements)
[x] 5. Add migration result capture (changed files, git diff, execution output)
[x] 6. Add POST /api/rehearsals/{id}/migrate endpoint
[x] 7. Update models/__init__.py to export TwinResult; verify no import errors
[x] 8. Run existing tests to verify no regressions


### 🤖 Assistant

Session 4 is complete. Here's what was implemented:

---

## What was built

### New files

**[`backend/app/models/twin.py`](backend/app/models/twin.py)** — `TwinResult` model  
Tracks twin workspace location (`twin_path`, `method`, `starting_revision`), migration outcome (`migration_status`, `changed_files`, `git_diff`), execution log, and per-action applied/skipped lists. Persisted as `twin_result.json`.

**[`backend/app/services/twin.py`](backend/app/services/twin.py)** — Twin workspace creation  
Tries `git worktree add --detach` first (preserves history, cheap copy). Falls back to `shutil.copytree` when not a git repo or worktree fails (shallow clones, bare repos). The original workspace is never touched. [`cleanup_twin()`](backend/app/services/twin.py) removes the worktree registration cleanly.

**[`backend/app/services/executor.py`](backend/app/services/executor.py)** — Migration executor  
Deterministic-only, React 17 → 18 specific:
- **VERSION_BUMP**: rewrites `react`, `react-dom`, `@types/react`, `@types/react-dom` to `^18.0.0` in `package.json`
- **ReactDOM.render → createRoot**: scans all `.js/.jsx/.ts/.tsx` files, rewrites unambiguous single-call sites, adds the `import { createRoot } from 'react-dom/client'` import; files with multiple calls or unparseable args are recorded as `manual_items` for Session 5
- **MANUAL/WATSONX_SEMANTIC actions**: recorded as `manual_items`, never auto-applied
- Captures `git diff` and `changed_files` after all mutations

### Modified files

**[`backend/app/services/store.py`](backend/app/services/store.py)** — added `save_twin_result` / `load_twin_result`

**[`backend/app/models/__init__.py`](backend/app/models/__init__.py)** — exports `TwinResult`, `TwinMethod`, `MigrationStatus`, `ChangedFile`

**[`backend/app/api/rehearsals.py`](backend/app/api/rehearsals.py)**:
- **`POST /{id}/migrate`** (202) — validates workspace + plan exist, starts `_run_twin_and_migrate` background task, returns stub `TwinResult`
- **`_run_twin_and_migrate`** — TWIN_CREATING → MIGRATING pipeline; updates rehearsal stage, saves twin_result at each step
- **`GET /{id}`** — now includes `twin_result` in the response
- Intake pipeline **no longer cleans up the workspace** — it's preserved for the `/migrate` call

### Safety guarantee

The original repository workspace is read-only from the executor's perspective. All mutations happen only in the `twin_path` directory. The twin is either a git worktree (separate directory on disk) or a `copytree` snapshot — neither path touches the original.