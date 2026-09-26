"""
Twin Workspace Service.

Creates a disposable Twin from the repository workspace used by the rehearsal.

Strategy:
  1. If the workspace is a Git repository, try git worktree (preferred).
  2. Otherwise fall back to a full temporary copy.

The original repository is NEVER modified.
The Twin path is recorded in TwinResult for the migration executor to use.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from app.models.twin import TwinMethod, TwinResult

logger = logging.getLogger(__name__)

# Branch name prefix for worktree branches
_WORKTREE_BRANCH_PREFIX = "codeshift-twin-"


class TwinError(Exception):
    """Raised when Twin creation fails."""


def _is_git_repo(workspace: Path) -> bool:
    """Return True if workspace is inside a Git repository."""
    result = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        cwd=str(workspace),
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _get_head_revision(workspace: Path) -> Optional[str]:
    """Return the current HEAD commit SHA, or None if unavailable."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(workspace),
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def _try_create_worktree(
    workspace: Path,
    rehearsal_id: str,
) -> Optional[TwinResult]:
    """
    Attempt to create a git worktree Twin.

    Returns a TwinResult on success, None if not possible (not a git repo,
    bare repo, shallow clone without history, etc.).
    """
    if not _is_git_repo(workspace):
        logger.debug("Workspace %s is not a git repo; skipping worktree", workspace)
        return None

    # We need a git-dir rooted at workspace (not a parent)
    rev = _get_head_revision(workspace)

    # Determine the top-level git dir
    tl_result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=str(workspace),
        capture_output=True,
        text=True,
    )
    if tl_result.returncode != 0:
        return None
    git_toplevel = Path(tl_result.stdout.strip())

    branch_name = f"{_WORKTREE_BRANCH_PREFIX}{rehearsal_id[:12]}"
    worktree_dir = Path(tempfile.mkdtemp(prefix="codeshift_twin_wt_"))

    # For a shallow clone (--depth 1), we cannot create a new branch easily.
    # Create a worktree on a detached HEAD instead.
    result = subprocess.run(
        ["git", "worktree", "add", "--detach", str(worktree_dir)],
        cwd=str(git_toplevel),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        shutil.rmtree(worktree_dir, ignore_errors=True)
        logger.debug(
            "git worktree add failed (stderr: %s); will fall back to copy",
            result.stderr.strip(),
        )
        return None

    logger.info(
        "Created git worktree Twin at %s (HEAD %s)",
        worktree_dir,
        rev or "unknown",
    )
    return TwinResult(
        rehearsal_id=rehearsal_id,
        method=TwinMethod.GIT_WORKTREE,
        twin_path=str(worktree_dir),
        worktree_branch=None,  # detached HEAD, no branch
        starting_revision=rev,
        execution_log=[
            f"Created git worktree at {worktree_dir} (detached from {rev or 'HEAD'})"
        ],
    )


def _create_copy_twin(workspace: Path, rehearsal_id: str) -> TwinResult:
    """
    Create a Twin by copying the workspace into a fresh temp directory.

    Always succeeds as long as there is disk space.
    """
    twin_dir = Path(tempfile.mkdtemp(prefix="codeshift_twin_cp_"))
    logger.info("Creating copy Twin from %s → %s", workspace, twin_dir)

    try:
        # copytree requires destination to not exist; remove then copy
        shutil.rmtree(twin_dir)
        shutil.copytree(str(workspace), str(twin_dir), symlinks=True)
    except Exception as exc:
        shutil.rmtree(twin_dir, ignore_errors=True)
        raise TwinError(f"Failed to copy workspace to Twin: {exc}") from exc

    # Try to get the revision even in copy mode
    rev = _get_head_revision(twin_dir)

    logger.info("Copy Twin created at %s", twin_dir)
    return TwinResult(
        rehearsal_id=rehearsal_id,
        method=TwinMethod.TEMP_COPY,
        twin_path=str(twin_dir),
        starting_revision=rev,
        execution_log=[f"Created copy Twin at {twin_dir} from {workspace}"],
    )


def create_twin(workspace: Path, rehearsal_id: str) -> TwinResult:
    """
    Create a disposable Twin workspace from the given repository workspace.

    Tries git worktree first; falls back to a full copy.

    The original workspace is NOT modified.

    Returns a TwinResult with twin_path set to the new Twin directory.
    Raises TwinError if even the copy fallback fails.
    """
    twin = _try_create_worktree(workspace, rehearsal_id)
    if twin is not None:
        return twin

    logger.info(
        "Worktree unavailable for rehearsal %s; using temp copy", rehearsal_id
    )
    return _create_copy_twin(workspace, rehearsal_id)


def cleanup_twin(twin: TwinResult) -> None:
    """
    Remove the Twin workspace and, if applicable, the git worktree registration.

    Safe to call even if the Twin path no longer exists.
    """
    twin_path = Path(twin.twin_path)

    if twin.method == TwinMethod.GIT_WORKTREE:
        # Remove the worktree registration from the parent repo.
        # Find the parent git dir by looking at the .git file inside the worktree.
        git_file = twin_path / ".git"
        if git_file.is_file():
            git_content = git_file.read_text(encoding="utf-8").strip()
            # Content: "gitdir: /path/to/parent/.git/worktrees/..."
            if git_content.startswith("gitdir:"):
                # Walk up to find the main git dir
                worktrees_path = Path(git_content.split(":", 1)[1].strip())
                # worktrees_path is .git/worktrees/<name>
                main_git = worktrees_path.parent.parent
                main_repo = main_git.parent
                if main_repo.exists():
                    subprocess.run(
                        ["git", "worktree", "remove", "--force", str(twin_path)],
                        cwd=str(main_repo),
                        capture_output=True,
                    )

    shutil.rmtree(str(twin_path), ignore_errors=True)
    logger.info("Cleaned up Twin at %s", twin_path)
