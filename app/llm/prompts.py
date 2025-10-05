"""
Prompt templates for LLM-powered evaluation.
"""

CV_EVALUATION_SYSTEM = """You are an expert technical recruiter and HR specialist. Your job is to evaluate a candidate's CV against a specific job description and scoring rubric.

You must provide objective, data-driven assessments based on the information provided. Be fair but thorough in your evaluation.

Always respond with valid JSON only, no additional text."""

def build_cv_evaluation_prompt(cv_text: str, job_description: str, scoring_rubric: str) -> str:
    """Build prompt for CV evaluation with RAG context."""
    return f"""Evaluate the following candidate's CV against the job description and scoring rubric provided.

JOB DESCRIPTION:
{job_description}

SCORING RUBRIC:
{scoring_rubric}

CANDIDATE CV:
{cv_text}

Please evaluate the candidate on the following parameters (score each 1-5):
1. Technical Skills Match (40% weight): Alignment with job requirements (backend, databases, APIs, cloud, AI/LLM)
2. Experience Level (25% weight): Years of experience and project complexity
3. Relevant Achievements (20% weight): Impact of past work (scaling, performance, adoption)
4. Cultural / Collaboration Fit (15% weight): Communication, learning mindset, teamwork/leadership

For each parameter, provide:
- A score from 1 to 5 based on the rubric
- A brief justification (1-2 sentences)

Then calculate:
- Weighted average score (as a decimal 0-1, rounded to 2 decimals)
- Overall feedback (2-3 sentences highlighting strengths and gaps)

Respond with JSON in this exact format:
{{
  "technical_skills": {{
    "score": <1-5>,
    "justification": "<text>"
  }},
  "experience_level": {{
    "score": <1-5>,
    "justification": "<text>"
  }},
  "achievements": {{
    "score": <1-5>,
    "justification": "<text>"
  }},
  "cultural_fit": {{
    "score": <1-5>,
    "justification": "<text>"
  }},
  "cv_match_rate": <0.00-1.00>,
  "cv_feedback": "<text>"
}}"""


PROJECT_EVALUATION_SYSTEM = """You are an expert backend engineer and code reviewer. Your job is to evaluate a candidate's project report against a case study brief and scoring rubric.

Focus on technical implementation quality, architectural decisions, and adherence to requirements. Be objective and constructive.

Always respond with valid JSON only, no additional text."""

def build_project_evaluation_prompt(project_text: str, case_study_brief: str, scoring_rubric: str) -> str:
    """Build prompt for project evaluation with RAG context."""
    return f"""Evaluate the following candidate's project report against the case study brief and scoring rubric provided.

CASE STUDY BRIEF:
{case_study_brief}

SCORING RUBRIC:
{scoring_rubric}

CANDIDATE'S PROJECT REPORT:
{project_text}

Please evaluate the project on the following parameters (score each 1-5):
1. Correctness (30% weight): Implements prompt design, LLM chaining, RAG context injection correctly
2. Code Quality & Structure (25% weight): Clean, modular, reusable, tested
3. Resilience & Error Handling (20% weight): Handles long jobs, retries, randomness, API failures
4. Documentation & Explanation (15% weight): README clarity, setup instructions, trade-off explanations
5. Creativity / Bonus (10% weight): Extra features beyond requirements

For each parameter, provide:
- A score from 1 to 5 based on the rubric
- A brief justification (1-2 sentences)

Then calculate:
- Weighted average score (1-5 scale, rounded to 2 decimals)
- Overall feedback (2-3 sentences highlighting implementation quality and areas for improvement)

Respond with JSON in this exact format:
{{
  "correctness": {{
    "score": <1-5>,
    "justification": "<text>"
  }},
  "code_quality": {{
    "score": <1-5>,
    "justification": "<text>"
  }},
  "resilience": {{
    "score": <1-5>,
    "justification": "<text>"
  }},
  "documentation": {{
    "score": <1-5>,
    "justification": "<text>"
  }},
  "creativity": {{
    "score": <1-5>,
    "justification": "<text>"
  }},
  "project_score": <1.00-5.00>,
  "project_feedback": "<text>"
}}"""


FINAL_AGGREGATION_SYSTEM = """You are a senior technical hiring manager making final hiring decisions. Your job is to synthesize CV and project evaluations into a comprehensive overall assessment.

Be balanced, fair, and actionable in your recommendations. Focus on candidate potential and fit for the role.

Always respond with valid JSON only, no additional text."""

def build_final_aggregation_prompt(cv_result: dict, project_result: dict, job_title: str) -> str:
    """Build prompt for final aggregation of CV and project evaluations."""
    return f"""Synthesize the following evaluation results into a final overall assessment for the position of {job_title}.

CV EVALUATION RESULTS:
- Match Rate: {cv_result.get('cv_match_rate', 0.0)}
- Feedback: {cv_result.get('cv_feedback', 'N/A')}
- Technical Skills: {cv_result.get('technical_skills', {}).get('score', 0)}/5
- Experience: {cv_result.get('experience_level', {}).get('score', 0)}/5
- Achievements: {cv_result.get('achievements', {}).get('score', 0)}/5
- Cultural Fit: {cv_result.get('cultural_fit', {}).get('score', 0)}/5

PROJECT EVALUATION RESULTS:
- Project Score: {project_result.get('project_score', 0.0)}/5
- Feedback: {project_result.get('project_feedback', 'N/A')}
- Correctness: {project_result.get('correctness', {}).get('score', 0)}/5
- Code Quality: {project_result.get('code_quality', {}).get('score', 0)}/5
- Resilience: {project_result.get('resilience', {}).get('score', 0)}/5
- Documentation: {project_result.get('documentation', {}).get('score', 0)}/5
- Creativity: {project_result.get('creativity', {}).get('score', 0)}/5

Based on these evaluations, provide:
1. An overall summary (3-5 sentences) that:
   - Highlights the candidate's key strengths
   - Identifies any notable gaps or areas for improvement
   - Provides a clear recommendation (strong fit / moderate fit / needs development / not recommended)
   - Mentions specific next steps or considerations

2. Calculate an overall score that weighs:
   - CV evaluation: 30% weight
   - Project evaluation: 70% weight

Respond with JSON in this exact format:
{{
  "overall_score": <1.00-5.00>,
  "overall_summary": "<text>",
  "recommendation": "<strong fit|moderate fit|needs development|not recommended>"
}}"""