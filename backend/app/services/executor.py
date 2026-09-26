"""
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
