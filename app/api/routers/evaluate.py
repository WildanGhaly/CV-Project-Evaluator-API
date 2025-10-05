from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.schemas.jobs import EvaluateRequest
from app.persistence.db import get_db
from app.persistence.repo import create_job
from app.persistence.models import File
from app.workers.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/evaluate")
def evaluate(req: EvaluateRequest, db: Session = Depends(get_db)):
    # Ensure files exist
    cv = db.get(File, req.cv_id)
    rp = db.get(File, req.report_id)
    if not cv or not rp:
        raise HTTPException(status_code=404, detail="cv_id or report_id not found")

    job = create_job(db, job_title=req.job_title, cv_file_id=req.cv_id, report_file_id=req.report_id)

    # Enqueue async evaluation using send_task (doesn't require importing the task)
    try:
        celery_app.send_task(
            'app.workers.tasks.evaluate_job',
            args=[job.id],
            queue='celery'
        )
        logger.info(f"Job {job.id} queued successfully")
    except Exception as e:
        logger.error(f"Failed to queue job {job.id}: {e}")
        raise HTTPException(
            status_code=503, 
            detail=f"Failed to queue evaluation job. Please ensure Redis and Celery worker are running. Error: {str(e)}"
        )

    return {"id": job.id, "status": "queued"}