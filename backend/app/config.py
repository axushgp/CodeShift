"""
Application configuration management.

Settings are loaded from environment variables and an optional .env file.
No credentials are hardcoded. Use .env.example as a template.

Environment variables use the CODESHIFT_ prefix to avoid collisions
with system variables (e.g. DEBUG, PORT used by other tools).
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="CODESHIFT_",
    )

    # Application
    app_name: str = "CodeShift"
    app_version: str = "1.0.0"
    environment: str = "development"
    log_level: str = "INFO"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Persistence
    data_dir: str = "data"

    # Watsonx
    watsonx_api_key: str = ""
    watsonx_project_id: str = ""
    watsonx_url: str = "https://us-south.ml.cloud.ibm.com"
    watsonx_model_id: str = "ibm/granite-4-h-small"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings instance."""
    return Settings()
