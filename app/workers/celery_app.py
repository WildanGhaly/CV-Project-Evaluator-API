from celery import Celery
import os

celery_app = Celery(
    ""evaluator"",
    broker=os.getenv(""REDIS_URL"", ""redis://localhost:6379/0""),
    backend=os.getenv(""REDIS_URL"", ""redis://localhost:6379/0""),
)
