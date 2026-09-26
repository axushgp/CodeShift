"""
Repository Scanner — JavaScript / TypeScript + Node/npm.

Deterministic scan: reads package.json and lockfiles only. No LLM.

Produces a RepositoryProfile from a local repository path.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from app.models.repository_profile import (
    Ecosystem,
    PackageManager,
    RepositoryProfile,
    ScriptInfo,
    SourceStructure,
)

logger = logging.getLogger(__name__)

# Lockfile → package manager mapping (ordered by priority).
_LOCKFILE_PM: list[tuple[str, PackageManager]] = [
    ("bun.lockb", PackageManager.BUN),
    ("bun.lock", PackageManager.BUN),
    ("pnpm-lock.yaml", PackageManager.PNPM),
    ("yarn.lock", PackageManager.YARN),
    ("package-lock.json", PackageManager.NPM),
]

# Scripts whose names suggest build/test/lint roles.
_BUILD_SCRIPT_NAMES = {"build", "compile", "bundle", "prebuild", "postbuild"}
_TEST_SCRIPT_NAMES = {"test", "test:unit", "test:e2e", "test:integration", "jest", "vitest"}
_LINT_SCRIPT_NAMES = {"lint", "lint:fix", "eslint", "prettier", "format", "typecheck", "type-check"}

# Candidate source directories.
_SRC_DIRS = ["src", "lib", "app", "source"]
_TEST_DIRS = ["test", "tests", "__tests__", "spec", "e2e"]

# Known configuration filenames.
_CONFIG_FILES = [
    "tsconfig.json",
    "tsconfig.base.json",
    ".babelrc",
    "babel.config.js",
    "babel.config.json",
    ".eslintrc.js",
    ".eslintrc.cjs",
    ".eslintrc.json",
    ".eslintrc.yaml",
    "eslint.config.js",
    "eslint.config.mjs",
    "jest.config.js",
    "jest.config.ts",
    "jest.config.json",
    "vitest.config.ts",
    "vitest.config.js",
    "vite.config.ts",
    "vite.config.js",
    "webpack.config.js",
    "webpack.config.ts",
    "rollup.config.js",
    "next.config.js",
    "next.config.ts",
    "nuxt.config.ts",
    ".prettierrc",
    ".prettierrc.json",
    ".npmrc",
    ".nvmrc",
    ".node-version",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
]

# Dependency name → framework label.
_FRAMEWORK_HINTS: list[tuple[str, str]] = [
    ("next", "nextjs"),
    ("nuxt", "nuxt"),
    ("gatsby", "gatsby"),
    ("remix", "@remix-run/node"),
    ("@remix-run/node", "remix"),
    ("@remix-run/react", "remix"),
    ("react", "react"),
    ("vue", "vue"),
    ("svelte", "svelte"),
    ("angular", "angular"),
    ("@angular/core", "angular"),
    ("express", "express"),
    ("fastify", "fastify"),
    ("koa", "koa"),
    ("hapi", "hapi"),
    ("nestjs", "nestjs"),
    ("@nestjs/core", "nestjs"),
    ("electron", "electron"),
]


class ScanError(Exception):
    """Raised when scanning fails unrecoverably."""


def scan_repository(repo_path: Path, rehearsal_id: str) -> RepositoryProfile:
    """
    Scan the repository at *repo_path* and return a populated RepositoryProfile.

    Only JavaScript/TypeScript + Node/npm ecosystems are supported in the MVP.
    If no package.json is found, returns a minimal profile with UNKNOWN ecosystem.
    """
    profile = RepositoryProfile(
        rehearsal_id=rehearsal_id,
        name=repo_path.name,
    )

    pkg_json_path = repo_path / "package.json"
    if not pkg_json_path.exists():
        logger.info("No package.json found in %s — marking as UNKNOWN ecosystem", repo_path)
        return profile

    try:
        raw = json.loads(pkg_json_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to parse package.json: %s", exc)
        return profile

    profile.ecosystem = Ecosystem.NODE
    profile.raw_manifest = raw

    # Repository name
    if "name" in raw:
        profile.name = raw["name"]

    # Runtime from engines field
    engines = raw.get("engines", {})
    if "node" in engines:
        node_ver = engines["node"].strip()
        profile.runtime = f"node@{node_ver}"
    else:
        # Look for .nvmrc / .node-version
        for fname in (".nvmrc", ".node-version"):
            fpath = repo_path / fname
            if fpath.exists():
                try:
                    ver = fpath.read_text(encoding="utf-8").strip().lstrip("v")
                    profile.runtime = f"node@{ver}"
                    break
                except OSError:
                    pass

    # Package manager from lockfiles
    detected_lockfile: Optional[str] = None
    for lockfile_name, pm in _LOCKFILE_PM:
        if (repo_path / lockfile_name).exists():
            profile.package_manager = pm
            detected_lockfile = lockfile_name
            break
    if detected_lockfile is None and (repo_path / "package.json").exists():
        # Default to npm if no lockfile found
        profile.package_manager = PackageManager.NPM

    profile.lockfile = detected_lockfile

    # Dependencies
    profile.dependencies = {
        k: str(v) for k, v in (raw.get("dependencies") or {}).items()
    }
    profile.dev_dependencies = {
        k: str(v) for k, v in (raw.get("devDependencies") or {}).items()
    }

    # Framework detection — check both deps and devDeps
    all_deps = {**profile.dependencies, **profile.dev_dependencies}
    profile.framework = _detect_framework(all_deps)

    # Scripts
    scripts: dict[str, str] = raw.get("scripts") or {}
    for name, cmd in scripts.items():
        info = ScriptInfo(name=name, command=cmd)
        name_lower = name.lower()
        if name_lower in _BUILD_SCRIPT_NAMES or name_lower.startswith("build"):
            profile.build_scripts.append(info)
        if name_lower in _TEST_SCRIPT_NAMES or name_lower.startswith("test"):
            profile.test_scripts.append(info)
        if name_lower in _LINT_SCRIPT_NAMES or name_lower.startswith("lint"):
            profile.lint_scripts.append(info)

    # Source structure
    profile.structure = _detect_structure(repo_path)

    logger.info(
        "Scan complete: ecosystem=%s pm=%s framework=%s deps=%d devDeps=%d",
        profile.ecosystem,
        profile.package_manager,
        profile.framework,
        len(profile.dependencies),
        len(profile.dev_dependencies),
    )
    return profile


def _detect_framework(deps: dict[str, str]) -> Optional[str]:
    """Return the first matching framework name from dependency keys."""
    for dep_name, framework in _FRAMEWORK_HINTS:
        if dep_name in deps:
            return framework
    return None


def _detect_structure(repo_path: Path) -> SourceStructure:
    """Walk the repo root and identify source/test dirs and config files."""
    src_dirs: list[str] = []
    test_dirs: list[str] = []
    config_files: list[str] = []
    entry_points: list[str] = []

    for candidate in _SRC_DIRS:
        if (repo_path / candidate).is_dir():
            src_dirs.append(candidate)

    for candidate in _TEST_DIRS:
        if (repo_path / candidate).is_dir():
            test_dirs.append(candidate)

    for candidate in _CONFIG_FILES:
        if (repo_path / candidate).exists():
            config_files.append(candidate)

    # Common entry points
    for entry in ("index.js", "index.ts", "index.mjs", "server.js", "server.ts"):
        if (repo_path / entry).exists():
            entry_points.append(entry)
    # Also check src/index.*
    for entry in ("index.js", "index.ts", "index.mjs"):
        if (repo_path / "src" / entry).exists():
            entry_points.append(f"src/{entry}")

    return SourceStructure(
        src_dirs=src_dirs,
        test_dirs=test_dirs,
        config_files=config_files,
        entry_points=entry_points,
    )
