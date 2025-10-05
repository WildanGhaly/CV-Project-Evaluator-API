"""
Project report evaluation using LLM with RAG-enhanced prompts.
"""
from app.llm.client import LLMClient
from app.llm.prompts import PROJECT_EVALUATION_SYSTEM, build_project_evaluation_prompt
from app.rag.retrieve import retrieve_context
import logging

logger = logging.getLogger(__name__)


def evaluate_project(project_text: str, llm_client: LLMClient) -> dict:
    """
    Evaluate a project report against case study brief using LLM.
    
    Args:
        project_text: Extracted text from candidate's project report
        llm_client: LLM client instance
    
    Returns:
        dict with evaluation results including scores and feedback
    """
    if not llm_client.available():
        raise Exception("LLM client not available for project evaluation")
    
    try:
        logger.info("Starting project evaluation with RAG")
        
        # Retrieve relevant context from vector DB
        case_study_brief = retrieve_context(
            query="case study brief requirements and deliverables",
            collection="case_study",
            top_k=3
        )
        
        scoring_rubric = retrieve_context(
            query="project evaluation scoring rubric parameters",
            collection="scoring_rubrics",
            top_k=2
        )
        
        # Build prompt with RAG context
        prompt = build_project_evaluation_prompt(
            project_text=project_text[:10000],  # Limit to avoid token limits
            case_study_brief=case_study_brief,
            scoring_rubric=scoring_rubric
        )
        
        # Call LLM with structured JSON output (uses configured temperature)
        result = llm_client.eval_json(
            prompt=prompt,
            system=PROJECT_EVALUATION_SYSTEM
        )
        
        logger.info(f"Project evaluation completed: score={result.get('project_score', 0)}")
        return result
        
    except Exception as e:
        logger.error(f"Error in project evaluation: {e}")
        raise