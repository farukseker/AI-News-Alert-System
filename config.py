from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str
    OPENROUTER_BASE_MODEL: str
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    GEMINI_MODEL: str = "google/gemini-2.5-flash-lite"
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_DOMAIN: str
    SMTP_PORT: str

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()