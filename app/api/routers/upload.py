from fastapi import APIRouter, UploadFile, File
import os, uuid
from app.config import settings

router = APIRouter()

@router.post("/upload")
async def upload_files(cv: UploadFile = File(...), report: UploadFile = File(...)):
    os.makedirs(settings.upload_dir, exist_ok=True)
    def save(f: UploadFile):
        ext = os.path.splitext(f.filename)[1]
        fid = f"{uuid.uuid4()}{ext}"
        path = os.path.join(settings.upload_dir, fid)
        with open(path, "wb") as out:
            out.write(await f.read())
        return fid
    cv_id = await save(cv)
    report_id = await save(report)
    return {"cv_id": cv_id, "report_id": report_id}
