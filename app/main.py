from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import health, upload, evaluate, result
from app.persistence.db import init_db


def create_app() -> FastAPI:
    init_db()
    app = FastAPI(title="cv-project-evaluator-api")
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(health.router)
    app.include_router(upload.router)
    app.include_router(evaluate.router)
    app.include_router(result.router)
    return app

app = create_app()
