"""
Application configuration.

Settings are loaded from environment variables (see .env.example).
No secrets are hard-coded here.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings, populated from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General
    app_name: str = "AI Resume Intelligence & ATS Optimization Platform"
    environment: str = "development"
    debug: bool = True

    # CORS
    cors_origins: str = "http://localhost:5173"

    # Database (used starting Phase 2)
    database_url: str = ""

    # Milvus (used starting Phase 5)
    milvus_host: str = ""
    milvus_port: str = ""

    # Redis (used starting Phase 8)
    redis_url: str = ""

    # Auth (used starting Phase 2)
    jwt_secret: str = ""

    # LLM provider (used starting Phase 7)
    llm_api_key: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse the comma-separated CORS origins string into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()