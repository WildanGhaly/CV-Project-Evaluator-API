from fastapi import FastAPI
from app.api.routers import health, upload, evaluate, result
from app.persistence.db import init_db


def create_app() -> FastAPI:
    init_db()
    app = FastAPI(title="cv-project-evaluator-api")
    app.include_router(health.router)
    app.include_router(upload.router)
    app.include_router(evaluate.router)
    app.include_router(result.router)
    return app

app = create_app()
