from fastapi import FastAPI
from app.api.routers import health, upload, evaluate, result

def create_app() -> FastAPI:
    app = FastAPI(title="cv-project-evaluator-api")
    app.include_router(health.router, prefix="")
    app.include_router(upload.router, prefix="")
    app.include_router(evaluate.router, prefix="")
    app.include_router(result.router, prefix="")
    return app

app = create_app()
