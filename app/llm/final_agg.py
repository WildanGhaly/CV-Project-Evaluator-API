"""
Final aggregation of CV and project evaluations using LLM.
"""
from app.llm.client import LLMClient
from app.llm.prompts import FINAL_AGGREGATION_SYSTEM, build_final_aggregation_prompt
import logging

logger = logging.getLogger(__name__)


def aggregate_results(cv_result: dict, project_result: dict, job_title: str, llm_client: LLMClient) -> dict:
    """
    Aggregate CV and project evaluation results into final assessment.
    
    Args:
        cv_result: CV evaluation results
        project_result: Project evaluation results
        job_title: Job title for context
        llm_client: LLM client instance
    
    Returns:
        dict with final overall_score and overall_summary
    """
    if not llm_client.available():
        raise Exception("LLM client not available for final aggregation")
    
    try:
        logger.info("Starting final aggregation")
        
        # Build aggregation prompt
        prompt = build_final_aggregation_prompt(
            cv_result=cv_result,
            project_result=project_result,
            job_title=job_title
        )
        
        # Call LLM with structured JSON output (uses configured temperature)
        result = llm_client.eval_json(
            prompt=prompt,
            system=FINAL_AGGREGATION_SYSTEM
        )
        
        logger.info(f"Final aggregation completed: overall_score={result.get('overall_score', 0)}")
        return result
        
    except Exception as e:
        logger.error(f"Error in final aggregation: {e}")
        raise