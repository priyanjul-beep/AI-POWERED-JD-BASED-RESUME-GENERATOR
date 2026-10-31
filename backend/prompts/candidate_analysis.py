import json
from typing import Dict, Any

def get_candidate_analysis_system_instruction() -> str:
    return (
        "You are an Elite AI Talent Architect and Career Transition Strategist. "
        "Your task is to compare a target Job Description against two sources: "
        "1. Candidate's Reference Resume "
        "2. Candidate's Complete Career Profile database. "
        "Your goal is to uncover hidden matches, bridge technology gaps with genuine transferable engineering experience, "
        "and flag unevidenced requirements without fabricating any false claims."
    )

def build_candidate_analysis_prompt(
    jd_analysis: Dict[str, Any],
    career_profile_data: Dict[str, Any],
    reference_resume_text: str,
    experience_level: str,
    additional_experience_details: str
) -> str:
    return f"""
TARGET JOB DESCRIPTION ANALYSIS:
{json.dumps(jd_analysis, indent=2)}

CANDIDATE SELECTED EXPERIENCE LEVEL:
{experience_level}

CANDIDATE ADDITIONAL EXPERIENCE DETAILS:
{additional_experience_details or 'None provided'}

CANDIDATE COMPLETE CAREER PROFILE (COMPREHENSIVE DATABASE):
{json.dumps(career_profile_data, indent=2)}

CANDIDATE REFERENCE RESUME TEXT (EXISTING SNAPSHOT):
---
{reference_resume_text or 'No reference resume uploaded; using complete career profile exclusively.'}
---

Perform a deep comparative analysis. Identify:
1. "already_present_in_resume": Skills already explicitly listed in reference resume matching JD.
2. "profile_skills_missing_from_resume": Skills or technologies found in the Complete Career Profile that match the JD but were omitted in the reference resume (e.g. Java/Spring experience candidate has in their profile).
3. "transferable_experiences": How candidate's existing engineering achievements (e.g. distributed systems, API performance, database transactions, concurrency in other tech stacks) translate directly to the target role.
4. "evidence_gaps": JD requirements that have NO supporting evidence in either the reference resume or complete career profile. (Never fabricate these; flag them for user confirmation).

Return strictly a valid JSON object with keys:
- "already_present_in_resume": list of strings
- "profile_skills_missing_from_resume": list of strings
- "transferable_experiences": list of objects with "original_area", "target_jd_area", "relevance_explanation"
- "evidence_gaps": list of strings
"""
