from .celery_app import celery_app

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def evaluate_job(self, job_id: str):
    # TODO: orchestrate parse â†’ retrieve â†’ LLM eval â†’ aggregate
    return {""job_id"": job_id, ""status"": ""completed""}
