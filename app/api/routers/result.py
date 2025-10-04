from fastapi import APIRouter
from .evaluate import jobs

router = APIRouter()

@router.get("/result/{job_id}")
def result(job_id: str):
    return {"id": job_id, "status": jobs.get(job_id, {}).get("status", "unknown")}
