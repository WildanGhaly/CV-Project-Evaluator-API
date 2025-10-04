from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_env: str = "dev"
    redis_url: str = "redis://redis:6379/0"
    database_url: str = "sqlite:///./app.db"
    upload_dir: str = "./data/uploads"

    # Optional LLM settings
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()