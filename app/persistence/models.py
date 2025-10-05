from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum as SAEnum, ForeignKey, DateTime, Text, JSON
from datetime import datetime
from enum import Enum
import uuid
from .db import Base

class FileKind(str, Enum):
    cv = "cv"
    report = "report"

class File(Base):
    __tablename__ = "files"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    kind: Mapped[FileKind] = mapped_column(SAEnum(FileKind), nullable=False)
    original_name: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_title: Mapped[str] = mapped_column(String, nullable=False)
    cv_file_id: Mapped[str] = mapped_column(String, ForeignKey("files.id"), nullable=False)
    report_file_id: Mapped[str] = mapped_column(String, ForeignKey("files.id"), nullable=False)
    status: Mapped[JobStatus] = mapped_column(SAEnum(JobStatus), default=JobStatus.queued, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    result_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    cv_file: Mapped[File] = relationship(foreign_keys=[cv_file_id])
    report_file: Mapped[File] = relationship(foreign_keys=[report_file_id])
    stages: Mapped[list[Stage]] = relationship("Stage", back_populates="job", cascade="all, delete-orphan")

class Stage(Base):
    __tablename__ = "stages"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(String, ForeignKey("jobs.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    logs: Mapped[str | None] = mapped_column(Text, nullable=True)

    job: Mapped[Job] = relationship("Job", back_populates="stages")