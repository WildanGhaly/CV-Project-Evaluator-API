from __future__ import annotations
from sqlalchemy.orm import Session
from pathlib import Path
from app.persistence.repo import start_stage, end_stage, set_job_result, set_job_status
from app.persistence.models import JobStatus, Job
from app.utils.pdf import extract_text
from app.services.scoring import keyword_overlap_score, bounded_to_scale

SYSTEM_DOCS = Path("data/system_docs")


def _read_first_jd_text() -> str:
    jds = sorted((SYSTEM_DOCS / "job_descriptions").glob("*"))
    for jd in jds:
        if jd.suffix.lower() == ".pdf":
            return extract_text(str(jd))
        else:
            try:
                return jd.read_text(encoding="utf-8")
            except Exception:
                continue
    return ""


def _read_case_brief_text() -> str:
    pdf = SYSTEM_DOCS / "case_study_brief.pdf"
    if pdf.exists():
        return extract_text(str(pdf))
    # fallback to any text doc
    for f in SYSTEM_DOCS.glob("case_study_brief.*"):
        if f.suffix != ".pdf":
            try:
                return f.read_text(encoding="utf-8")
            except Exception:
                pass
    return ""


def run_evaluation(db: Session, job: Job) -> dict:
    """Heuristic baseline pipeline (LLM optional via future hook)."""
    set_job_status(db, job.id, JobStatus.processing)

    st1 = start_stage(db, job.id, "parse_cv")
    cv_text = extract_text(job.cv_file.path)
    end_stage(db, st1.id, logs=f"CV chars={len(cv_text)}\n")

    st2 = start_stage(db, job.id, "parse_report")
    report_text = extract_text(job.report_file.path)
    end_stage(db, st2.id, logs=f"Report chars={len(report_text)}\n")

    st3 = start_stage(db, job.id, "retrieve_context")
    jd_text = _read_first_jd_text()
    brief_text = _read_case_brief_text()
    end_stage(db, st3.id, logs=f"JD chars={len(jd_text)}, Brief chars={len(brief_text)}\n")

    st4 = start_stage(db, job.id, "score_cv")
    cv_match_rate = keyword_overlap_score(cv_text, jd_text)
    cv_feedback = (
        "Good alignment with role requirements." if cv_match_rate > 0.35 else
        "Partial alignment; highlight relevant projects and skills." if cv_match_rate > 0.15 else
        "Low alignment; tailor CV to the JD keywords and outcomes."
    )
    end_stage(db, st4.id, logs=f"cv_match_rate={cv_match_rate}\n")

    st5 = start_stage(db, job.id, "score_project")
    proj_signal = keyword_overlap_score(report_text, brief_text or jd_text)
    project_score = bounded_to_scale(proj_signal, 0.0, 0.5, 5)  # mild scaling
    project_feedback = (
        "Strong structure and relevance." if project_score >= 4 else
        "Solid baseline; add error handling and tests." if project_score >= 3 else
        "Improve correctness, logging, and docs per brief."
    )
    end_stage(db, st5.id, logs=f"project_signal={proj_signal}; project_score={project_score}\n")

    st6 = start_stage(db, job.id, "aggregate")
    overall = round(0.2 * cv_match_rate * 5 + 0.8 * project_score, 2)  # map cv (0..1) to 0..5 first
    overall_summary = (
        "Candidate shows promising fit and a well-structured project." if overall >= 4
        else "Candidate demonstrates baseline fit; refine resilience and documentation."
    )
    result = {
        "cv_match_rate": cv_match_rate,
        "cv_feedback": cv_feedback,
        "project_score": project_score,
        "project_feedback": project_feedback,
        "overall_score": overall,
        "overall_summary": overall_summary,
    }
    end_stage(db, st6.id, logs=f"overall={overall}\n")

    set_job_result(db, job.id, result)
    set_job_status(db, job.id, JobStatus.completed)
    return result