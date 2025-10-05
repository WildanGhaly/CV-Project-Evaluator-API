from pydantic import BaseModel

class EvaluateRequest(BaseModel):
    job_title: str
    cv_id: str
    report_id: str
