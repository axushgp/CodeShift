"""
Demo configuration model for CodeShift Quick Start demos.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class DemoManifest(BaseModel):
    """
    Lightweight manifest representing a verified Quick Start demo repository.
    """

    id: str = Field(description="Unique identifier for the demo")
    name: str = Field(description="Human-readable title for the demo")
    repository_url: str = Field(description="Public Git repository URL")
    description: str = Field(description="Brief summary of the demo project")
    package: str = Field(default="react", description="Package or runtime being upgraded")
    source_version: str = Field(description="Source version of the package in the repository")
    target_version: str = Field(description="Target version for the migration rehearsal")
