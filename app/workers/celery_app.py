from celery import Celery
from app.config import settings

celery_app = Celery(
    "evaluator",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,  # Retry connection on startup
    broker_connection_retry=True,
    broker_connection_max_retries=10,
)

# Make sure tasks auto-discover works in Docker
celery_app.autodiscover_tasks(["app.workers"])