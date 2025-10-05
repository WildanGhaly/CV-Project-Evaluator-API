from __future__ import annotations
from sqlalchemy.orm import Session
from app.persistence.repo import start_stage, end_stage, set_job_result, set_job_status
from app.persistence.models import JobStatus, Job
from app.utils.pdf import extract_text
from app.llm.client import LLMClient
from app.llm.cv_eval import evaluate_cv
from app.llm.project_eval import evaluate_project
from app.llm.final_agg import aggregate_results
from app.rag.ingest import run as run_ingestion
from app.rag.retrieve import check_collection_exists
import logging

logger = logging.getLogger(__name__)


def ensure_rag_initialized():
    """Ensure RAG system is initialized with documents."""
    try:
        # Check if collections exist
        if not check_collection_exists("job_descriptions"):
            logger.info("RAG not initialized, running ingestion...")
            run_ingestion()
        else:
            logger.info("RAG already initialized")
    except Exception as e:
        logger.warning(f"Could not initialize RAG: {e}")
        # Continue anyway - will use fallback


def run_evaluation(db: Session, job: Job) -> dict:
    """
    Complete LLM-powered evaluation pipeline with RAG.
    
    Pipeline stages:
    1. Parse CV and Project Report PDFs
    2. Initialize RAG system (if needed)
    3. Evaluate CV against job description using LLM + RAG
    4. Evaluate Project Report against case study brief using LLM + RAG
    5. Aggregate results into final assessment using LLM
    """
    set_job_status(db, job.id, JobStatus.processing)
    
    try:
        # Stage 1: Parse CV
        st1 = start_stage(db, job.id, "parse_cv")
        logger.info(f"Job {job.id}: Parsing CV from {job.cv_file.path}")
        cv_text = extract_text(job.cv_file.path)
        if not cv_text.strip():
            raise Exception("CV is empty or could not be parsed")
        end_stage(db, st1.id, logs=f"CV parsed: {len(cv_text)} characters\n")
        
        # Stage 2: Parse Project Report
        st2 = start_stage(db, job.id, "parse_report")
        logger.info(f"Job {job.id}: Parsing project report from {job.report_file.path}")
        report_text = extract_text(job.report_file.path)
        if not report_text.strip():
            raise Exception("Project report is empty or could not be parsed")
        end_stage(db, st2.id, logs=f"Report parsed: {len(report_text)} characters\n")
        
        # Stage 3: Initialize RAG (if needed)
        st3 = start_stage(db, job.id, "initialize_rag")
        ensure_rag_initialized()
        end_stage(db, st3.id, logs="RAG system ready\n")
        
        # Initialize LLM client
        llm_client = LLMClient()
        if not llm_client.available():
            raise Exception("LLM client not available. Please configure OPENAI_API_KEY.")
        
        # Stage 4: Evaluate CV with LLM + RAG
        st4 = start_stage(db, job.id, "evaluate_cv")
        logger.info(f"Job {job.id}: Evaluating CV with LLM")
        cv_result = evaluate_cv(cv_text, job.job_title, llm_client)
        end_stage(db, st4.id, logs=f"CV Match Rate: {cv_result.get('cv_match_rate', 0):.2f}\n")
        
        # Stage 5: Evaluate Project with LLM + RAG
        st5 = start_stage(db, job.id, "evaluate_project")
        logger.info(f"Job {job.id}: Evaluating project report with LLM")
        project_result = evaluate_project(report_text, llm_client)
        end_stage(db, st5.id, logs=f"Project Score: {project_result.get('project_score', 0):.2f}/5\n")
        
        # Stage 6: Final aggregation with LLM
        st6 = start_stage(db, job.id, "final_aggregation")
        logger.info(f"Job {job.id}: Generating final assessment")
        final_result = aggregate_results(cv_result, project_result, job.job_title, llm_client)
        end_stage(db, st6.id, logs=f"Overall Score: {final_result.get('overall_score', 0):.2f}/5\n")
        
        # Combine all results
        result = {
            "cv_match_rate": cv_result.get("cv_match_rate", 0),
            "cv_feedback": cv_result.get("cv_feedback", ""),
            "project_score": project_result.get("project_score", 0),
            "project_feedback": project_result.get("project_feedback", ""),
            "overall_score": final_result.get("overall_score", 0),
            "overall_summary": final_result.get("overall_summary", ""),
            "recommendation": final_result.get("recommendation", ""),
            # Include detailed breakdowns
            "cv_details": {
                "technical_skills": cv_result.get("technical_skills", {}),
                "experience_level": cv_result.get("experience_level", {}),
                "achievements": cv_result.get("achievements", {}),
                "cultural_fit": cv_result.get("cultural_fit", {})
            },
            "project_details": {
                "correctness": project_result.get("correctness", {}),
                "code_quality": project_result.get("code_quality", {}),
                "resilience": project_result.get("resilience", {}),
                "documentation": project_result.get("documentation", {}),
                "creativity": project_result.get("creativity", {})
            }
        }
        
        logger.info(f"Job {job.id}: Evaluation complete")
        set_job_result(db, job.id, result)
        set_job_status(db, job.id, JobStatus.completed)
        return result
        
    except Exception as e:
        logger.error(f"Job {job.id}: Evaluation failed: {e}")
        set_job_status(db, job.id, JobStatus.failed)
        # Store error in result
        error_result = {
            "error": str(e),
            "cv_match_rate": 0,
            "cv_feedback": f"Evaluation failed: {e}",
            "project_score": 0,
            "project_feedback": f"Evaluation failed: {e}",
            "overall_score": 0,
            "overall_summary": f"Evaluation could not be completed due to an error: {e}"
        }
        set_job_result(db, job.id, error_result)
        raise