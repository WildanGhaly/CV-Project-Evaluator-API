from celery import Celery
from app.config import settings

celery_app = Celery(
    "evaluator",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

# Make sure tasks auto-discover works in Docker
celery_app.autodiscover_tasks(["app.workers"])