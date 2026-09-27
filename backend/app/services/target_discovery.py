"""
Target Discovery Service — Automatic Framework Detection & Click-to-Select Upgrade Target.

Implements the data-driven migration knowledge registry:
- Scans repository metadata to detect primary framework, version, and surrounding tooling.
- Queries migration_knowledge/frameworks/*.json for known versions and migration paths.
- Provides available upgrade targets with recommended option, without hardcoding framework logic.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Optional

from app.models.repository_profile import RepositoryProfile
from app.services import scanner as scanner_svc

logger = logging.getLogger(__name__)

_KNOWLEDGE_DIR = Path(__file__).parent.parent / "migration_knowledge"
_FRAMEWORKS_DIR = _KNOWLEDGE_DIR / "frameworks"
_RECIPES_DIR = _KNOWLEDGE_DIR / "recipes"


def load_framework_registry() -> dict[str, dict[str, Any]]:
    """
    Load all framework definitions from migration_knowledge/frameworks/*.json.
    Keyed by framework ID.
    """
    registry: dict[str, dict[str, Any]] = {}
    if not _FRAMEWORKS_DIR.exists():
        return registry

    for fpath in _FRAMEWORKS_DIR.glob("*.json"):
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
            fid = data.get("id") or fpath.stem
            registry[fid.lower()] = data
        except Exception as exc:
            logger.warning("Failed to load framework knowledge from %s: %s", fpath, exc)

    return registry


def find_framework_by_package(package_name: str) -> Optional[dict[str, Any]]:
    """Look up framework definition by primary package name (e.g. 'react', 'vue', '@angular/core')."""
    registry = load_framework_registry()
    pkg_clean = package_name.lower().strip()
    
    # 1. Exact match on package or id
    for fw in registry.values():
        if fw.get("package", "").lower() == pkg_clean or fw.get("id", "").lower() == pkg_clean:
            return fw

    # 2. Substring match
    for fw in registry.values():
        if pkg_clean in fw.get("package", "").lower():
            return fw

    return None


def clean_version(version_str: Optional[str]) -> Optional[str]:
    """Clean semver version string (e.g. '^17.0.2' -> '17.0.2', '~2.6.14' -> '2.6.14')."""
    if not version_str:
        return None
    # Strip leading non-digit characters (^, ~, >=, <=, =, v)
    cleaned = re.sub(r"^[^\d]*", "", version_str.strip())
    # Cut off anything after space or semicolon
    cleaned = re.split(r"[\s;]", cleaned)[0]
    return cleaned if cleaned else version_str.strip()


def detect_tooling(profile: RepositoryProfile) -> dict[str, str]:
    """
    Detect surrounding tooling from repository profile:
    build_tool, runtime, package_manager.
    """
    deps = {**profile.dependencies, **profile.dev_dependencies}
    build_tool = "Standard"

    # Detect build tool
    if "vite" in deps or any("vite" in c for c in profile.structure.config_files):
        build_tool = "Vite"
    elif "react-scripts" in deps:
        build_tool = "Create React App"
    elif "next" in deps or any("next" in c for c in profile.structure.config_files):
        build_tool = "Next.js"
    elif "nuxt" in deps or any("nuxt" in c for c in profile.structure.config_files):
        build_tool = "Nuxt"
    elif "webpack" in deps or any("webpack" in c for c in profile.structure.config_files):
        build_tool = "Webpack"
    elif "rollup" in deps or any("rollup" in c for c in profile.structure.config_files):
        build_tool = "Rollup"
    elif "esbuild" in deps:
        build_tool = "esbuild"

    # Runtime
    runtime = "Node.js"
    if profile.runtime and profile.runtime != "node":
        runtime = f"Node.js ({profile.runtime.replace('node@', '')})"

    # Package manager
    pm_display = profile.package_manager.value if profile.package_manager else "npm"
    if profile.package_manager_version:
        pm_display = f"{pm_display} {profile.package_manager_version}"

    return {
        "build_tool": build_tool,
        "runtime": runtime,
        "package_manager": pm_display,
    }


def discover_migration_targets(profile: RepositoryProfile) -> dict[str, Any]:
    """
    Determine primary framework, detected version, surrounding tooling,
    and available upgrade target options for a scanned repository.
    """
    deps = {**profile.dependencies, **profile.dev_dependencies}
    registry = load_framework_registry()

    # Identify primary framework
    detected_fw_dict: Optional[dict[str, Any]] = None
    detected_fw_id: Optional[str] = None
    detected_pkg: Optional[str] = None
    raw_version: Optional[str] = None

    # Priority 1: Check known registry frameworks in repository dependencies
    for fid, fw in registry.items():
        primary_pkg = fw.get("package", "")
        if primary_pkg in deps:
            detected_fw_dict = fw
            detected_fw_id = fid
            detected_pkg = primary_pkg
            raw_version = deps[primary_pkg]
            break

    # Priority 2: Use profile.framework if detected by scanner
    if detected_fw_dict is None and profile.framework:
        detected_fw_dict = find_framework_by_package(profile.framework)
        if detected_fw_dict:
            detected_fw_id = detected_fw_dict.get("id")
            detected_pkg = detected_fw_dict.get("package")
            raw_version = deps.get(detected_pkg, deps.get(profile.framework))
        else:
            detected_fw_id = profile.framework
            detected_pkg = profile.framework
            raw_version = deps.get(profile.framework)

    cleaned_ver = clean_version(raw_version)
    tooling = detect_tooling(profile)

    # Resolve target options from registry
    target_options: list[dict[str, Any]] = []
    recommended_target: Optional[str] = None
    has_certified_recipe = False
    knowledge_updated = "2026-09"

    if detected_fw_dict is not None:
        knowledge_updated = detected_fw_dict.get("knowledge_updated", "2026-09")
        rec_target = detected_fw_dict.get("recommended_target")
        major_ver = cleaned_ver.split(".")[0] if cleaned_ver else ""

        # Match migration paths
        paths = detected_fw_dict.get("migration_paths", [])
        matched_paths: list[dict[str, Any]] = []

        for p in paths:
            from_spec = p.get("from", "").replace(".x", "")
            # Check if current version matches 'from'
            if not from_spec or from_spec == major_ver or cleaned_ver.startswith(from_spec):
                matched_paths.append(p)

        if not matched_paths and paths:
            # Fall back to all known migration paths for this framework
            matched_paths = paths

        for p in matched_paths:
            is_rec = bool(p.get("is_recommended", False) or (rec_target and p.get("target_version") == rec_target))
            has_recipe = bool(p.get("has_certified_recipe", False))
            if has_recipe:
                has_certified_recipe = True
            if is_rec and not recommended_target:
                recommended_target = p.get("target_version")

            target_options.append({
                "target_version": p.get("target_version", p.get("to", "")),
                "label": p.get("label", f"{detected_fw_dict.get('name')} {p.get('to')}"),
                "badge": p.get("badge", "Recommended" if is_rec else None),
                "is_recommended": is_rec,
                "has_certified_recipe": has_recipe,
                "recipe": p.get("recipe"),
                "description": p.get("description", ""),
            })

        if not recommended_target and target_options:
            recommended_target = target_options[0]["target_version"]
            target_options[0]["is_recommended"] = True

    # If framework detected without predefined options or unknown framework
    if not target_options:
        fw_name = detected_fw_dict.get("name", detected_fw_id.capitalize()) if detected_fw_dict and detected_fw_id else (detected_fw_id.capitalize() if detected_fw_id else "Node Application")
        target_options.append({
            "target_version": "latest",
            "label": f"{fw_name} (AI-Assisted)",
            "badge": "Human Review",
            "is_recommended": True,
            "has_certified_recipe": False,
            "recipe": None,
            "description": "No certified automated migration recipe available. Will produce an AI-assisted analysis and human review plan.",
        })
        recommended_target = "latest"

    fw_display_name = (
        detected_fw_dict.get("name", detected_fw_id.capitalize())
        if detected_fw_dict and detected_fw_id
        else (detected_fw_id.capitalize() if detected_fw_id else "Unknown")
    )

    return {
        "detected_framework": {
            "id": detected_fw_id or "unknown",
            "name": fw_display_name,
            "package": detected_pkg or (detected_fw_id or "unknown"),
        },
        "detected_version": cleaned_ver or raw_version or "Unknown",
        "raw_version": raw_version,
        "tooling": tooling,
        "upgrade_target": {
            "current": f"{fw_display_name} {cleaned_ver or 'Unknown'}",
            "recommended_target": recommended_target,
            "has_certified_recipe": has_certified_recipe,
            "options": target_options,
        },
        "knowledge_updated": knowledge_updated,
    }
