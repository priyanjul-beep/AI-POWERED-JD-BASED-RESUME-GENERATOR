import json
from typing import Dict, Any, List
from .industry_patterns import get_role_industry_patterns

def get_experience_guidance(experience_level: str) -> str:
    level = experience_level.upper()
    if 'FRESHER' in level or 'NO_INTERNSHIP' in level or 'NO INTERNSHIP' in level:
        return """
SCENARIO: FRESHER / ENTRY-LEVEL (Academic & Project Focus)
- Prioritize: Technical skills, Academic projects, Personal projects, Practical development experience, Certifications, and Relevant coursework.
- Detail the engineering challenges solved in their projects (architecture, database schema, algorithm efficiency, API contracts, unit testing, Git/SDLC).
- STRICT RULE: Do NOT fabricate senior commercial responsibilities, team leadership of commercial enterprise products, or phantom job titles.
- Present them truthfully and compellingly as an enthusiastic, high-capability junior/entry-level engineer with demonstrable project engineering mastery.
"""
    elif 'INTERNSHIP' in level:
        return """
SCENARIO: CANDIDATE WITH INTERNSHIP EXPERIENCE
- Prioritize: Real-world engineering contributions during the internship: feature delivery, REST API development, bug fixes, automated test writing, code review participation, database queries, and tools used.
- Frame bullets to emphasize professional engineering hygiene, agile collaboration, SDLC processes, and measurable project outcomes.
"""
    elif 'APPRENTICE' in level:
        return """
SCENARIO: CANDIDATE WITH APPRENTICE EXPERIENCE
- Prioritize: Hands-on apprenticeship engineering tasks, paired programming, structured mentorship learning, and tangible code contributions to enterprise systems.
- Emphasize adherence to coding standards, defect triage, and system testing.
"""
    elif '1' in level or '2' in level:
        return """
SCENARIO: EARLY CAREER (1–2 YEARS EXPERIENCE)
- Prioritize: Relevant professional experience, feature implementation, API development, database operations, software testing, technical contributions, and project outcomes.
- Emphasize end-to-end feature ownership, production deployments, microservices/REST APIs, query optimization, automated CI/CD pipeline integration, and cross-functional team collaboration.
"""
    else:
        return """
SCENARIO: EXPERIENCED ENGINEER (3–5+ YEARS EXPERIENCE)
- Prioritize: Technical ownership, system design and architecture contributions, production systems, scalability, engineering decisions, and measurable business achievements.
- Emphasize deep architectural decisions, concurrency, caching, transaction boundaries, system integration, technical mentorship, and resilience.
"""

def get_generation_system_instruction() -> str:
    return (
        "You are an Elite Technical Resume Strategist, Principal ATS Architect, and Staff Recruiter. "
        "CRITICAL INVARIANT POLICY: The candidate's original resume and career profile is the STRUCTURAL SOURCE OF TRUTH. "
        "The application is a CONTENT OPTIMIZATION AND REFINEMENT ENGINE, NOT A RESUME IDENTITY REGENERATION ENGINE. "
        "IMMUTABLE PROTECTED FIELDS (MUST NEVER BE CHANGED, RENAMED, REPLACED, OR INVENTED): "
        "1. Candidate full_name, email, phone, location. "
        "2. Company names, designations/job titles, employment dates (e.g. NEVER change Software Development Intern into Backend Software Engineer). "
        "3. Project names (e.g. NEVER rename an existing project or invent a fake completed project). "
        "4. Degree names, universities/institutions, graduation dates. "
        "5. Certification names, issuers, and dates. "
        "6. Existing section headings and ordering. "
        "PERMITTED MODIFICATION SCOPE: "
        "- Skills: Reorder by JD relevance, include verified skills from profile, normalize terminology. "
        "- Work Experience: Rewrite/optimize bullet points, improve verbs, ATS alignment, technical explanations. Company and designation must remain exact. "
        "- Projects: Rewrite descriptions and bullet points/highlights. Project name must remain exact. "
        "- Summary: Rewrite for role relevance without changing actual experience level or career history. "
        "- Missing Skills: If unsupported by profile evidence, place into `proposed_content` requiring candidate confirmation. NEVER silently inject into verified employment history. "
        "- Formula: Action Verb + Technical Implementation + Technology + Purpose/Outcome. Do NOT invent phantom metrics or volume numbers. "
        "Output valid JSON strictly matching the required schema."
    )

def build_resume_generation_prompt(
    target_role: str,
    target_company: str,
    experience_level: str,
    additional_experience_details: str,
    jd_analysis: Dict[str, Any],
    career_profile_data: Dict[str, Any],
    reference_resume_text: str,
    complete_jd_text: str = "",
    requirement_mappings: List[Dict[str, Any]] = None
) -> str:
    guidance = get_experience_guidance(experience_level)
    
    # Extract JD components
    mandatory_skills = jd_analysis.get('mandatory_skills', [])
    preferred_skills = jd_analysis.get('preferred_skills', [])
    jd_responsibilities = jd_analysis.get('key_responsibilities', [])
    ats_keywords = jd_analysis.get('important_ats_keywords', [])
    
    # Generate industry responsibility patterns
    primary_tech = ", ".join(jd_analysis.get('programming_languages', [])[:2] + jd_analysis.get('frameworks', [])[:2]) or target_role
    primary_db = ", ".join(jd_analysis.get('databases', [])[:2]) or "Relational Databases (SQL)"
    industry_patterns = get_role_industry_patterns(
        target_role=target_role,
        experience_level=experience_level,
        primary_tech=primary_tech,
        database=primary_db
    )

    return f"""
================================================================================
CRITICAL POLICY: RESUME STRUCTURAL IDENTITY PRESERVATION
================================================================================
The candidate's original resume / career profile is the STRUCTURAL SOURCE OF TRUTH.
This system is a CONTENT OPTIMIZATION ENGINE, NOT A RESUME IDENTITY REGENERATION ENGINE.

STRICT INVARIANTS: You MUST preserve the original:
- Candidate name and contact information (`header.full_name`, `header.email`, `header.phone`, `header.location`)
- Company names (`work_experience[].company`)
- Job designations (`work_experience[].title`)
- Employment dates (`work_experience[].start_date`, `work_experience[].end_date`)
- Internship details (Do NOT change a Software Development Intern into a Backend Software Engineer)
- Project names (`projects[].title` - Do NOT rename an existing project into a different project name; do NOT invent a new project)
- Education details (`education[].degree`, `education[].institution`, `education[].end_date`)
- Certifications (`certifications[].name`, `certifications[].issuing_organization`, `certifications[].issue_date`)
- Section headings and ordering.

Do not rename, replace, invent, or modify these protected fields.
Do not replace the candidate's degree or university with another institution.
Do not upgrade a fresher into an experienced professional.
Do not add fictional companies, internships, employment history, certifications, or educational qualifications.

PERMITTED MODIFICATION SCOPE:
1. Technical Skills:
   - Reorder existing skills according to JD relevance.
   - Include relevant skills already supported by candidate's career profile.
   - Normalize technical terminology and improve categorization.
   - Remove irrelevant skills when appropriate.
2. Work Experience:
   - Rewrite existing bullet points to improve technical descriptions, action verbs, and ATS alignment.
   - Highlight relevant responsibilities using the 4-part formula.
   - Add additional bullet points missing in profile based on supported work.
   - STRICT RULE: The company name, designation, employment dates, and experience identity must remain exactly as provided. Only descriptive content may change.
3. Projects:
   - Rewrite project descriptions and highlights/bullet points.
   - Highlight relevant technologies and implementation details.
   - STRICT RULE: Never change original project name. Only descriptive content may be optimized.
4. Professional Summary:
   - Rewrite summary to make it relevant to the target role.
   - STRICT RULE: Do not change actual experience level, total years of experience, professional designation, or career history.
5. Missing JD Requirements Handling (4-STEP WORKFLOW):
   - STEP 1: Search the complete career profile for evidence of these skills.
   - STEP 2: If a technology is present in candidate's actual experience or projects but missing from reference resume, incorporate it into the appropriate existing section.
   - STEP 3: If candidate has transferable experience, improve existing bullet points to highlight relevant engineering responsibilities without falsely claiming use of a different technology.
   - STEP 4: If a required technology has NO supporting evidence, generate an industry-standard suggested bullet separately in `proposed_content` with `requires_user_confirmation: true`. Never silently convert suggested responsibilities into verified experience!

================================================================================
1. TARGET JOB ROLE: {target_role}
2. TARGET COMPANY: {target_company or 'Enterprise Tech'}
3. CANDIDATE PROFESSIONAL EXPERIENCE LEVEL: {experience_level}
4. ADDITIONAL EXPERIENCE DETAILS: {additional_experience_details or 'None provided'}
================================================================================

5. COMPLETE JOB DESCRIPTION (RAW TEXT):
---
{complete_jd_text or 'Refer to JD Analysis below.'}
---

6. EXTRACTED JD MANDATORY SKILLS:
{json.dumps(mandatory_skills, indent=2)}

7. EXTRACTED JD PREFERRED SKILLS:
{json.dumps(preferred_skills, indent=2)}

8. EXTRACTED JD KEY RESPONSIBILITIES:
{json.dumps(jd_responsibilities, indent=2)}

9. EXTRACTED ATS HIGH-PRIORITY KEYWORDS:
{json.dumps(ats_keywords, indent=2)}

10. REQUIREMENT-TO-EVIDENCE MAPPING (AUDIT BENCHMARK):
{json.dumps(requirement_mappings or [], indent=2)}

11. CANDIDATE COMPLETE CAREER PROFILE (COMPREHENSIVE MASTER RECORD):
{json.dumps(career_profile_data, indent=2)}

12. CANDIDATE REFERENCE RESUME TEXT (EXISTING SNAPSHOT):
---
{reference_resume_text or 'No reference resume provided. Construct resume purely from Complete Career Profile.'}
---

13. EXPERIENCE-LEVEL SPECIFIC GUIDELINES:
{guidance}

14. INDUSTRY-STANDARD PROFESSIONAL RESPONSIBILITY PATTERNS:
{json.dumps(industry_patterns, indent=2)}

================================================================================
BULLET-POINT WRITING PATTERN (MANDATORY):
================================================================================
Every bullet point in `work_experience` and `projects` MUST follow this formula:
[Action Verb] + [Technical Implementation / Mechanism] + [Verified Technology] + [Technical Purpose or Concrete Outcome]

Standard patterns:
- Developed backend APIs using the relevant verified technology.
- Implemented database integration and optimized data access.
- Designed application-level validation and error-handling mechanisms.
- Wrote unit and integration tests using verified testing frameworks.
- Improved backend service reliability through verified engineering practices.

DO NOT invent metrics, performance improvements, transaction volumes, production deployments, or achievements not in records.

AUDIT TRAIL (`changes_applied`):
Document modifications to permitted descriptive content only with:
`section`, `change_type`, `original_content`, `updated_content`, `reason`, `supporting_evidence`.
Do NOT log changes to immutable fields because those fields must never change.ce`.

Return strictly a valid JSON object matching the complete schema:
{{
  "header": {{
    "full_name": "string",
    "headline": "string",
    "email": "string",
    "phone": "string",
    "location": "string",
    "linkedin_url": "string",
    "github_url": "string",
    "portfolio_url": "string"
  }},
  "summary": "string (3-4 sentences aligned with target role and experience level)",
  "skills": {{
    "languages": ["string"],
    "frameworks": ["string"],
    "databases": ["string"],
    "cloud_and_devops": ["string"],
    "developer_tools": ["string"]
  }},
  "work_experience": [
    {{
      "title": "string",
      "company": "string",
      "location": "string",
      "start_date": "string",
      "end_date": "string",
      "is_current": boolean,
      "technologies": ["string"],
      "bullet_points": ["string (following the 4-part formula)"]
    }}
  ],
  "projects": [
    {{
      "title": "string",
      "role": "string",
      "url": "string",
      "technologies": ["string"],
      "description": "string",
      "highlights": ["string (following the 4-part formula)"]
    }}
  ],
  "education": [
    {{
      "institution": "string",
      "degree": "string",
      "field_of_study": "string",
      "start_date": "string",
      "end_date": "string",
      "grade": "string",
      "honors": "string"
    }}
  ],
  "certifications": [
    {{
      "name": "string",
      "issuing_organization": "string",
      "issue_date": "string",
      "credential_id": "string"
    }}
  ],
  "changes_applied": [
    {{
      "section": "string",
      "change_type": "ADDED|MODIFIED|REMOVED",
      "original_content": "string",
      "updated_content": "string",
      "reason": "string",
      "supporting_evidence": "string"
    }}
  ],
  "evidence_gaps": [
    {{
      "requirement": "string",
      "reason_missing": "string",
      "transferable_evidence": "string",
      "suggested_user_input": "string",
      "industry_pattern": "string",
      "requires_confirmation": true
    }}
  ],
  "requirement_mappings": [
    {{
      "requirement_name": "string",
      "category": "string",
      "classification": "MANDATORY|PREFERRED",
      "candidate_evidence": "string",
      "evidence_source": "string",
      "status": "VERIFIED|TRANSFERABLE|USER_CONFIRMATION_REQUIRED|UNSUPPORTED|PROPOSED",
      "recommended_action": "string"
    }}
  ],
  "proposed_content": [
    {{
      "target_section": "string",
      "proposed_text": "string",
      "targeted_jd_requirement": "string",
      "reason": "string",
      "requires_user_confirmation": true
    }}
  ]
}}
"""
