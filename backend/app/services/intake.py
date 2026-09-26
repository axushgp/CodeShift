"""
Repository Intake Service.

Supports:
- Public Git URL  → clone into a temporary workspace
- ZIP file bytes  → extract into a temporary workspace

The original repository is never modified.
Temporary workspaces are cleaned up by the caller after use.
"""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path

logger = logging.getLogger(__name__)

# Basic URL validation — must start with http/https and end with .git or
# be a recognisable hosting URL (github/gitlab/bitbucket).
_GIT_URL_RE = re.compile(
    r"^https?://(github\.com|gitlab\.com|bitbucket\.org|.*)/.*",
    re.IGNORECASE,
)

GIT_CLONE_TIMEOUT = 120  # seconds


class IntakeError(Exception):
    """Raised when repository intake fails."""

    def __init__(self, message: str, detail: str = "") -> None:
        super().__init__(message)
        self.detail = detail


def _validate_git_url(url: str) -> None:
    """Raise IntakeError if the URL looks invalid."""
    url = url.strip()
    if not url:
        raise IntakeError("Repository URL is empty.")
    if not url.startswith(("http://", "https://")):
        raise IntakeError(
            "Invalid repository URL.",
            "Only public http/https Git URLs are supported.",
        )
    if not _GIT_URL_RE.match(url):
        raise IntakeError(
            "Invalid repository URL.",
            "URL does not look like a Git hosting URL.",
        )


def clone_repository(url: str) -> Path:
    """
    Clone a public Git repository into a fresh temporary directory.

    Returns the path to the cloned repository root.
    Raises IntakeError on any failure.
    """
    _validate_git_url(url)

    tmp_dir = Path(tempfile.mkdtemp(prefix="codeshift_git_"))
    logger.info("Cloning %s into %s", url, tmp_dir)

    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", url.strip(), str(tmp_dir)],
            capture_output=True,
            text=True,
            timeout=GIT_CLONE_TIMEOUT,
        )
    except FileNotFoundError:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise IntakeError("git is not installed or not on PATH.")
    except subprocess.TimeoutExpired:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise IntakeError(
            "Git clone timed out.",
            f"Clone did not complete within {GIT_CLONE_TIMEOUT}s.",
        )

    if result.returncode != 0:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        stderr = result.stderr.strip()
        raise IntakeError(
            "Git clone failed.",
            stderr or "Unknown git error.",
        )

    logger.info("Clone successful: %s", tmp_dir)
    return tmp_dir


def extract_zip(zip_bytes: bytes) -> Path:
    """
    Extract a ZIP archive into a fresh temporary directory.

    If the ZIP contains a single top-level directory, returns that directory
    (so callers always get the repo root, not a parent folder).

    Raises IntakeError on any failure.
    """
    if not zip_bytes:
        raise IntakeError("ZIP file is empty.")

    tmp_dir = Path(tempfile.mkdtemp(prefix="codeshift_zip_"))
    logger.info("Extracting ZIP (%d bytes) into %s", len(zip_bytes), tmp_dir)

    try:
        with zipfile.ZipFile(BytesIO(zip_bytes)) as zf:
            zf.extractall(tmp_dir)
    except zipfile.BadZipFile as exc:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise IntakeError("Invalid ZIP file.", str(exc)) from exc
    except Exception as exc:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise IntakeError("ZIP extraction failed.", str(exc)) from exc

    # If the ZIP contained a single top-level directory, descend into it.
    entries = list(tmp_dir.iterdir())
    if len(entries) == 1 and entries[0].is_dir():
        repo_root = entries[0]
    else:
        repo_root = tmp_dir

    logger.info("Extraction successful: %s", repo_root)
    return repo_root


def cleanup_workspace(workspace: Path) -> None:
    """Remove a temporary workspace directory created by intake."""
    try:
        # Walk up to the actual temp dir if we descended into a sub-directory.
        target = workspace
        # If workspace is inside a codeshift_zip_ or codeshift_git_ tmpdir,
        # remove the whole tmpdir.
        parent = workspace.parent
        if parent.name.startswith(("codeshift_zip_", "codeshift_git_")):
            target = parent
        shutil.rmtree(target, ignore_errors=True)
        logger.info("Cleaned up workspace: %s", target)
    except Exception:
        logger.warning("Failed to clean up workspace: %s", workspace, exc_info=True)
