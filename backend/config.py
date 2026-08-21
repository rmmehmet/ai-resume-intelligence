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
    database_url: str = "sqlite:///./dev.db"

    # Milvus (used starting Phase 5)
    # Preferred: milvus_uri (works for both Zilliz Cloud and self-hosted).
    # milvus_host/milvus_port remain as a convenience fallback for a plain
    # self-hosted Milvus instance (e.g. via docker-compose in production).
    # Not required for the app to run - matching works without Milvus.
    milvus_uri: str = ""
    milvus_token: str = ""
    milvus_host: str = ""
    milvus_port: str = ""

    # Embeddings (Phase 5+)
    # "sentence-bert" gives real semantic embeddings (fixed-dimension,
    # suitable for Milvus). "tfidf" is a lightweight, dependency-light
    # fallback with no model download, but its vectors are NOT
    # fixed-dimension - see services/embeddings/tfidf_provider.py.
    embedding_provider: str = "sentence-bert"
    embedding_model_name: str = ""  # empty = provider's own default

    # Redis (used starting Phase 8)
    redis_url: str = ""

    # Auth (Phase 2)
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # File storage (Phase 3)
    # Local disk for now; abstracted so it can be swapped for S3/GCS later
    # without touching the parsing or router layers.
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 10

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