"""
CV evaluation using LLM with RAG-enhanced prompts.
"""
from app.llm.client import LLMClient
from app.llm.prompts import CV_EVALUATION_SYSTEM, build_cv_evaluation_prompt
from app.rag.retrieve import retrieve_context
import logging

logger = logging.getLogger(__name__)


def evaluate_cv(cv_text: str, job_title: str, llm_client: LLMClient) -> dict:
    """
    Evaluate a CV against job requirements using LLM.
    
    Args:
        cv_text: Extracted text from candidate's CV
        job_title: Job title for context
        llm_client: LLM client instance
    
    Returns:
        dict with evaluation results including scores and feedback
    """
    if not llm_client.available():
        raise Exception("LLM client not available for CV evaluation")
    
    try:
        logger.info("Starting CV evaluation with RAG")
        
        # Retrieve relevant context from vector DB
        job_description = retrieve_context(
            query=f"job description requirements for {job_title}",
            collection="job_descriptions",
            top_k=3
        )
        
        scoring_rubric = retrieve_context(
            query="CV evaluation scoring rubric parameters",
            collection="scoring_rubrics",
            top_k=2
        )
        
        # Build prompt with RAG context
        prompt = build_cv_evaluation_prompt(
            cv_text=cv_text[:8000],  # Limit to avoid token limits
            job_description=job_description,
            scoring_rubric=scoring_rubric
        )
        
        # Call LLM with structured JSON output
        result = llm_client.eval_json(
            prompt=prompt,
            system=CV_EVALUATION_SYSTEM,
            temperature=0.3  # Low temperature for consistency
        )
        
        logger.info(f"CV evaluation completed: match_rate={result.get('cv_match_rate', 0)}")
        return result
        
    except Exception as e:
        logger.error(f"Error in CV evaluation: {e}")
        raise