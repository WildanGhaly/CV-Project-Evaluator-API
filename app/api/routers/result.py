from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.persistence.db import get_db
from app.persistence.repo import get_job

router = APIRouter()

@router.get("/result/{job_id}")
def result(job_id: str, db: Session = Depends(get_db)):
    job = get_job(db, job_id)
    if not job:
        return {"id": job_id, "status": "unknown"}
    return {"id": job.id, "status": job.status.value, "result": job.result_json}