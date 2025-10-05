from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import os, uuid
from sqlalchemy.orm import Session
from app.config import settings
from app.persistence.db import get_db
from app.persistence.repo import create_file
from app.persistence.models import FileKind

router = APIRouter()

async def _save_upload(f: UploadFile) -> str:
    os.makedirs(settings.upload_dir, exist_ok=True)
    ext = os.path.splitext(f.filename)[1]
    fid = f"{uuid.uuid4()}{ext}"
    path = os.path.join(settings.upload_dir, fid)
    data = await f.read()
    with open(path, "wb") as out:
        out.write(data)
    return path

@router.post("/upload")
async def upload_files(cv: UploadFile = File(...), report: UploadFile = File(...), db: Session = Depends(get_db)):
    if not cv.filename or not report.filename:
        raise HTTPException(status_code=400, detail="Both cv and report are required")
    cv_path = await _save_upload(cv)
    rpt_path = await _save_upload(report)
    cv_rec = create_file(db, FileKind.cv, cv.filename, cv_path)
    rpt_rec = create_file(db, FileKind.report, report.filename, rpt_path)
    return {"cv_id": cv_rec.id, "report_id": rpt_rec.id}