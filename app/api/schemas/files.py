from pydantic import BaseModel

class UploadResponse(BaseModel):
    cv_id: str
    report_id: str
