"""Application settings for MemOps."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Network = Literal["mainnet", "testnet", "signet", "regtest"]


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="MEMOPS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    backend_url: str = "https://mempool.space"
    network: Network = "mainnet"
    export_dir: Path = Path("demo/output")

    @field_validator("backend_url")
    @classmethod
    def normalize_backend_url(cls, value: str) -> str:
        """Normalize the configured backend URL."""
        normalized = value.strip()
        if not normalized:
            msg = "backend_url must not be empty"
            raise ValueError(msg)
        return normalized.rstrip("/")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
