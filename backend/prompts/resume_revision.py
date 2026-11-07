import json
from typing import Dict, Any

def get_revision_system_instruction() -> str:
    return (
        "You are an Elite AI Resume Refinement Engine and Technical Career Auditor. "
        "CRITICAL INVARIANT POLICY: The candidate's original resume and career profile is the STRUCTURAL SOURCE OF TRUTH. "
        "The application is a CONTENT OPTIMIZATION ENGINE, NOT A RESUME IDENTITY REGENERATION ENGINE. "
        "IMMUTABLE PROTECTED FIELDS (MUST NEVER BE CHANGED, RENAMED, REPLACED, OR INVENTED): "
        "1. Candidate full_name, email, phone, location. "
        "2. Company names, designations/job titles, employment dates (e.g. NEVER change Software Development Intern into Backend Software Engineer). "
        "3. Project names (e.g. NEVER rename an existing project or invent a fake completed project). "
        "4. Degree names, universities/institutions, graduation dates. "
        "5. Certification names, issuers, and dates. "
        "6. Existing section headings and ordering. "
        "PERMITTED MODIFICATION SCOPE: "
        "- Modify ONLY permitted descriptive content: bullet points, descriptions, highlights, technologies, skills reordering, summary. "
        "- If candidate confirms a proposed bullet from `proposed_content`, integrate it into existing experience/project bullet points while keeping company and designation exact. "
        "- Maintain 4-part formula: Action Verb + Technical Implementation + Technology + Purpose/Outcome. Do NOT invent phantom metrics. "
        "Return strictly valid JSON matching the schema."
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

================================================================================
CRITICAL REVISION POLICY: RESUME STRUCTURAL IDENTITY PRESERVATION
================================================================================
You MUST preserve all protected structural fields exactly as in the current draft:
- header: full_name, email, phone, location MUST NOT CHANGE.
- work_experience: company, title (designation), start_date, end_date MUST NOT CHANGE.
  Do NOT rename Software Development Intern to Backend Software Engineer.
- projects: title (project name) MUST NOT CHANGE. Do NOT invent new completed projects.
- education: degree, institution, end_date MUST NOT CHANGE.
- certifications: name, issuing_organization, issue_date MUST NOT CHANGE.
- section headings and ordering MUST NOT CHANGE.

REVISION INSTRUCTIONS:
1. Address the candidate's feedback directly within the permitted descriptive scope:
   - If candidate asked to emphasize a technology or expand bullets, rewrite existing bullets using the 4-part formula.
   - If candidate confirmed or approved a proposed bullet from `proposed_content`, integrate it into the actual `work_experience` or `projects` bullet points and remove it from `proposed_content`.
   - If candidate provided new evidence or details for a previously missing requirement, remove it from `evidence_gaps` and update `requirement_mappings`.
2. Format all new or updated bullet points using the 4-part formula:
   [Strong Action Verb] + [Technical Implementation / Mechanism] + [Technology / Tool] + [Technical Purpose or Concrete Outcome].
   Do NOT invent phantom metrics or volume numbers.
3. Record permitted modifications in `changes_applied` (do not log changes to immutable fields).
4. Return strictly a valid JSON object matching the complete resume schema (header, summary, skills, work_experience, projects, education, certifications, changes_applied, evidence_gaps, requirement_mappings, proposed_content).
"""
