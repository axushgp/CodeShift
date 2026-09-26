"""
RepositoryProfile model.

Represents the deterministic scan result for a repository.
Produced by the Repository Scanner (Session 2+).
Persisted as repo_profile.json inside the rehearsal data directory.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Ecosystem(str, Enum):
    """Supported ecosystems. Extensible for future sessions."""

    NODE = "node"
    PYTHON = "python"
    UNKNOWN = "unknown"


class PackageManager(str, Enum):
    """Known package managers."""

    NPM = "npm"
    YARN = "yarn"
    PNPM = "pnpm"
    BUN = "bun"
    PIP = "pip"
    POETRY = "poetry"
    UV = "uv"
    UNKNOWN = "unknown"


class ScriptInfo(BaseModel):
    """Represents a named script detected in the repository."""

    name: str
    command: str


class SourceStructure(BaseModel):
    """Detected important directories and files."""

    src_dirs: list[str] = Field(default_factory=list)
    test_dirs: list[str] = Field(default_factory=list)
    config_files: list[str] = Field(default_factory=list)
    entry_points: list[str] = Field(default_factory=list)


class RepositoryProfile(BaseModel):
    """
    Deterministic repository scan result.

    Contains everything the later stages need to know about the repository
    without any LLM inference. Produced by the Repository Scanner.
    """

    rehearsal_id: str = Field(description="Parent rehearsal identifier")

    # Identity
    name: Optional[str] = Field(default=None, description="Repository name")
    source_url: Optional[str] = Field(default=None)

    # Environment
    ecosystem: Ecosystem = Field(default=Ecosystem.UNKNOWN)
    runtime: Optional[str] = Field(
        default=None, description="e.g. 'node@20', 'python@3.12'"
    )
    package_manager: PackageManager = Field(default=PackageManager.UNKNOWN)
    framework: Optional[str] = Field(
        default=None, description="e.g. 'react', 'nextjs', 'express', 'fastapi'"
    )

    # Dependencies
    dependencies: dict[str, str] = Field(
        default_factory=dict,
        description="Production dependencies: {name: version_spec}",
    )
    dev_dependencies: dict[str, str] = Field(
        default_factory=dict,
        description="Development dependencies: {name: version_spec}",
    )
    lockfile: Optional[str] = Field(
        default=None, description="Detected lockfile filename"
    )

    # Scripts
    build_scripts: list[ScriptInfo] = Field(default_factory=list)
    test_scripts: list[ScriptInfo] = Field(default_factory=list)
    lint_scripts: list[ScriptInfo] = Field(default_factory=list)

    # Structure
    structure: SourceStructure = Field(default_factory=SourceStructure)

    # Raw manifest (optional preservation of package.json / pyproject.toml etc.)
    raw_manifest: Optional[dict] = Field(
        default=None, description="Raw parsed manifest data"
    )
