from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.schemas.jobs import EvaluateRequest
from app.persistence.db import get_db
from app.persistence.repo import create_job
from app.persistence.models import File
from app.workers.tasks import evaluate_job

router = APIRouter()

@router.post("/evaluate")
def evaluate(req: EvaluateRequest, db: Session = Depends(get_db)):
    # Ensure files exist
    cv = db.get(File, req.cv_id)
    rp = db.get(File, req.report_id)
    if not cv or not rp:
        raise HTTPException(status_code=404, detail="cv_id or report_id not found")

    job = create_job(db, job_title=req.job_title, cv_file_id=req.cv_id, report_file_id=req.report_id)

    # Enqueue async evaluation
    evaluate_job.delay(job.id)

    return {"id": job.id, "status": "queued"}