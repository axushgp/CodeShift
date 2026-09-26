"""
Service managing default Quick Start demo repository catalog.

Loads the catalog from the single manifest data file (demo_catalog.json).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from app.models.demo import DemoManifest

CATALOG_PATH = Path(__file__).resolve().parent.parent / "demo_catalog.json"


def load_demo_catalog(path: Optional[Path] = None) -> list[DemoManifest]:
    """Load the demo manifest catalog from disk."""
    target_path = path or CATALOG_PATH
    if not target_path.exists():
        return []
    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [DemoManifest(**item) for item in data]


def get_all_demos() -> list[DemoManifest]:
    """Return all available Quick Start demo configurations from the catalog."""
    return load_demo_catalog()


def get_demo_by_id(demo_id: str) -> Optional[DemoManifest]:
    """Retrieve a demo configuration by its ID."""
    for demo in get_all_demos():
        if demo.id == demo_id:
            return demo
    return None
