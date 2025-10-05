from celery import shared_task
from sqlalchemy.orm import Session
from app.persistence.db import SessionLocal
from app.persistence.repo import get_job, set_job_status
from app.persistence.models import JobStatus
from app.services.evaluation import run_evaluation

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def evaluate_job(self, job_id: str):
    db: Session = SessionLocal()
    try:
        job = get_job(db, job_id)
        if not job:
            return {"error": "job not found"}
        set_job_status(db, job_id, JobStatus.processing)
        result = run_evaluation(db, job)
        return {"job_id": job_id, "status": "completed", "result": result}
    except Exception as e:
        set_job_status(db, job_id, JobStatus.failed)
        raise e
    finally:
        db.close()