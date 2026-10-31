import json
from typing import Dict, Any

def get_revision_system_instruction() -> str:
    return (
        "You are an Elite AI Resume Refinement Engine. "
        "The candidate has reviewed their draft resume and provided specific instructions and feedback. "
        "Your task is to refine the existing draft resume strictly addressing the candidate's feedback, "
        "while ensuring all improvements remain fully aligned with the Job Description and grounded in genuine candidate experience. "
        "Never discard valid unaffected content; update the resume surgically and document the new changes."
    )

def build_resume_revision_prompt(
    previous_resume_data: Dict[str, Any],
    user_comment: str,
    target_role: str,
    jd_analysis: Dict[str, Any],
    career_profile_data: Dict[str, Any]
) -> str:
    return f"""
TARGET ROLE: {target_role}

USER'S SPECIFIC REVISION INSTRUCTIONS / FEEDBACK:
"{user_comment}"

ORIGINAL JOB DESCRIPTION ANALYSIS:
{json.dumps(jd_analysis, indent=2)}

CURRENT DRAFT RESUME (PREVIOUS ITERATION):
{json.dumps(previous_resume_data, indent=2)}

CANDIDATE COMPLETE CAREER PROFILE (SUPPORTING EVIDENCE POOL):
{json.dumps(career_profile_data, indent=2)}

REVISION INSTRUCTIONS:
1. Address the candidate's feedback directly (e.g. adjust technical skills, expand experience bullets, polish summary, reframe projects).
2. Maintain strict truthful alignment with the candidate's verified profile experience; do not invent fictional employment.
3. Update the `changes_applied` array to record the new modifications performed specifically in this revision step, including the reason and supporting evidence.
4. Return strictly a valid JSON object matching the complete resume schema (header, summary, skills, work_experience, projects, education, certifications, changes_applied, evidence_gaps).
"""
