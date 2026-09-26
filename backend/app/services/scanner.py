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


def _parse_package_manager_field(field_val: str) -> tuple[Optional[PackageManager], Optional[str]]:
    """
    Parse packageManager string from package.json (e.g. 'yarn@3.8.0', 'pnpm@8.6.0+sha224...', 'npm@10.2.0', 'bun@1.1.0').
    Returns (PackageManager, version_str) or (None, None).
    """
    if not field_val or not isinstance(field_val, str):
        return None, None
    parts = field_val.strip().split("@")
    if not parts or not parts[0]:
        return None, None
    tool = parts[0].strip().lower()
    version: Optional[str] = None
    if len(parts) > 1 and parts[1]:
        # Strip sha hash suffix if present
        version = parts[1].split("+")[0].strip()

    mapping = {
        "npm": PackageManager.NPM,
        "yarn": PackageManager.YARN,
        "pnpm": PackageManager.PNPM,
        "bun": PackageManager.BUN,
    }
    return mapping.get(tool), version

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

    # Environment requirements
    env_reqs: dict[str, str] = {}
    engines = raw.get("engines", {})
    if isinstance(engines, dict):
        for k, v in engines.items():
            env_reqs[f"engines.{k}"] = str(v)
    if "packageManager" in raw and isinstance(raw["packageManager"], str):
        env_reqs["packageManager"] = str(raw["packageManager"])
    profile.environment_requirements = env_reqs

    # Runtime from engines field
    if isinstance(engines, dict) and "node" in engines:
        node_ver = str(engines["node"]).strip()
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
        if profile.runtime is None:
            profile.runtime = "node"

    # Package manager detection in required order:
    # 1. package.json -> packageManager field when present
    # 2. lockfile detection
    # 3. sensible npm fallback
    pm_from_field: Optional[PackageManager] = None
    pm_version_from_field: Optional[str] = None
    if "packageManager" in raw and isinstance(raw["packageManager"], str):
        pm_from_field, pm_version_from_field = _parse_package_manager_field(raw["packageManager"])

    detected_lockfile: Optional[str] = None
    pm_from_lockfile: Optional[PackageManager] = None
    for lockfile_name, pm in _LOCKFILE_PM:
        if (repo_path / lockfile_name).exists():
            detected_lockfile = lockfile_name
            pm_from_lockfile = pm
            break

    profile.lockfile = detected_lockfile

    if pm_from_field is not None:
        profile.package_manager = pm_from_field
        profile.package_manager_version = pm_version_from_field
    elif pm_from_lockfile is not None:
        profile.package_manager = pm_from_lockfile
    elif (repo_path / "package.json").exists():
        # Sensible npm fallback
        profile.package_manager = PackageManager.NPM

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
    profile.relevant_scripts = {str(k): str(v) for k, v in scripts.items()}
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
