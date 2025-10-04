from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import File, FileKind, Job, JobStatus, Stage
from typing import Optional

# Files

def create_file(db: Session, kind: FileKind, original_name: str, path: str) -> File:
    f = File(kind=kind, original_name=original_name, path=path)
    db.add(f)
    db.commit()
    db.refresh(f)
    return f

# Jobs

def create_job(db: Session, job_title: str, cv_file_id: str, report_file_id: str) -> Job:
    job = Job(job_title=job_title, cv_file_id=cv_file_id, report_file_id=report_file_id)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_job(db: Session, job_id: str) -> Optional[Job]:
    return db.get(Job, job_id)

def set_job_status(db: Session, job_id: str, status: JobStatus) -> None:
    job = db.get(Job, job_id)
    if not job:
        return
    job.status = status
    db.commit()

# Stages

def start_stage(db: Session, job_id: str, name: str) -> Stage:
    st = Stage(job_id=job_id, name=name)
    db.add(st)
    db.commit()
    db.refresh(st)
    return st

def end_stage(db: Session, stage_id: str, logs: str | None = None) -> None:
    st = db.get(Stage, stage_id)
    if not st:
        return
    from datetime import datetime
    st.ended_at = datetime.utcnow()
    if logs:
        st.logs = (st.logs or "") + logs
    db.commit()

# Results

def set_job_result(db: Session, job_id: str, result: dict) -> None:
    job = db.get(Job, job_id)
    if not job:
        return
    job.result_json = result
    db.commit()