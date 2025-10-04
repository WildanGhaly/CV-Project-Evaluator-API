from pydantic import BaseSettings

class Settings(BaseSettings):
    app_env: str = "dev"
    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "sqlite:///./app.db"
    upload_dir: str = "./data/uploads"

settings = Settings()
