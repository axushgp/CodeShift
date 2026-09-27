"""
Demo configuration model for CodeShift Quick Start demos.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class DemoManifest(BaseModel):
    """
    Lightweight manifest representing a verified Quick Start demo repository.
    """

    id: str = Field(description="Unique identifier for the demo")
    name: str = Field(description="Human-readable title for the demo")
    repository_url: str = Field(description="Public Git repository URL")
    description: Optional[str] = Field(default="", description="Brief summary of the demo project")
    package: Optional[str] = Field(default=None, description="Package or runtime being upgraded")
    source_version: Optional[str] = Field(default=None, description="Source version of the package in the repository")
    target_version: Optional[str] = Field(default=None, description="Target version for the migration rehearsal")
