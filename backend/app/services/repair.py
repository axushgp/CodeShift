"""
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
