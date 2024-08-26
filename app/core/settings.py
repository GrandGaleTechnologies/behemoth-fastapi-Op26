import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """The settings for the application."""

    model_config = SettingsConfigDict(env_file=".env")

    # App
    DEBUG: bool = os.environ.get("DEBUG")  # type: ignore
    UPLOAD_DIR: str = os.environ.get("UPLOAD_DIR")  # type: ignore

    # Security
    SECRET_KEY: str = os.environ.get("SECRET_KEY")  # type: ignore
    ACCESS_TOKEN_EXPIRE_MIN: int = os.environ.get("ACCESS_TOKEN_EXPIRE_MIN")  # type: ignore
    ENCRYPTION_KEY: str = os.environ.get("ENCRYPTION_KEY")  # type: ignore

    # DB Settings
    POSTGRES_DATABASE_URL: str = os.environ.get("POSTGRES_DATABASE_URL")  # type: ignore


@lru_cache
def get_settings():
    """This function returns the settings obj for the application."""
    return Settings()
