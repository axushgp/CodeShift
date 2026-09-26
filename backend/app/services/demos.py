"""
Service managing verified Quick Start demo configurations.
"""

from __future__ import annotations

from typing import Optional

from app.models.demo import DemoManifest

DEMO_CATALOG: list[DemoManifest] = [
    DemoManifest(
        id="datocms-plugin-iframe-tab",
        name="DatoCMS Plugin Iframe Tab",
        repository_url="https://github.com/thebuilder/datocms-plugin-iframe-tab",
        description="Public DatoCMS plugin built with React 17, Vite, and Yarn.",
        package="react",
        source_version="17.0.2",
        target_version="18.0.0",
    ),
    DemoManifest(
        id="vite-react-17-template",
        name="Vite React 17 Starter",
        repository_url="https://github.com/colinbarry/vite-react-17-template",
        description="Clean minimal React 17 application built with Vite and npm.",
        package="react",
        source_version="17.0.2",
        target_version="18.0.0",
    ),
    DemoManifest(
        id="vite-react17-tailwind",
        name="Vite React 17 Tailwind Starter",
        repository_url="https://github.com/CrzMarvin/Vite-React17-Tailwind3-",
        description="React 17 application configured with Tailwind CSS 3 and Vite.",
        package="react",
        source_version="17.0.2",
        target_version="18.0.0",
    ),
]


def get_all_demos() -> list[DemoManifest]:
    """Return all available Quick Start demo configurations."""
    return list(DEMO_CATALOG)


def get_demo_by_id(demo_id: str) -> Optional[DemoManifest]:
    """Retrieve a demo configuration by its ID."""
    for demo in DEMO_CATALOG:
        if demo.id == demo_id:
            return demo
    return None
