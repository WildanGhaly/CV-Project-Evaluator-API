from fastapi import APIRouter
from pydantic import BaseModel
import uuid

router = APIRouter()

class EvaluateReq(BaseModel):
    job_title: str
    cv_id: str
    report_id: str

# Stub: enqueue background task via Celery in real implementation
jobs = {}

@router.post("/evaluate")
def evaluate(req: EvaluateReq):
    jid = str(uuid.uuid4())
    jobs[jid] = {"status": "queued"}
    return {"id": jid, "status": "queued"}
