from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).resolve().parent
    DATABASE_URL: str
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    SUMMARIZER_MODEL: str = "openai/gpt-4.1-nano"
    OPENROUTER_BASE_MODEL: str
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_DOMAIN: str
    SMTP_PORT: str
    TO_EMAIL: list[str]
    SELENIUM_REMOTE_SERVER_ADDR: str
    SELENIUM_REMOTE_SERVER_HOST: str
    SENTRY_DSN: str
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )



@lru_cache()
def get_settings() -> Settings:
    return Settings()


__all__ = "get_settings",