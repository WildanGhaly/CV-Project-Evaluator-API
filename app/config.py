from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_env: str = "dev"
    redis_url: str = "redis://redis:6379/0"
    database_url: str = "sqlite:///./app.db"
    upload_dir: str = "./data/uploads"
    
    # Additional environment variables
    vector_db: str = "qdrant"
    api_host: str = "0.0.0.0"
    api_port: str = "8000"

    # Optional LLM settings
    openai_api_key: str | None = None
    openai_model: str = "gpt-5-2025-08-07"
    # Temperature for LLM calls (1.0 for o1/o3/gpt-5 models, 0.3-0.7 for gpt-4)
    openai_temperature: float = 1.0

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields instead of raising validation errors

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()