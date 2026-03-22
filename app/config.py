"""
Application configuration loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """AIBench application settings."""
    GROQ_API_KEY: str
    DATABASE_URL: str
    MAX_RETRIES: int = 3

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()