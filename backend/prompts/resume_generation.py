import json
from typing import Dict, Any

def get_experience_guidance(experience_level: str) -> str:
    level = experience_level.upper()
    if 'FRESHER' in level or 'NO INTERNSHIP' in level:
        return """
SCENARIO: FRESHER / ENTRY-LEVEL (No commercial or internship experience)
- Focus heavily on Technical Skills, Personal Projects, Academic Capstones, Open Source contributions, and relevant Coursework.
- Detail the engineering challenges solved in their projects (architecture, database schema, algorithm efficiency, API contracts).
- STRICT RULE: Do NOT fabricate senior commercial responsibilities, team leadership of commercial products, or phantom job titles. Represent them truthfully as an enthusiastic, high-capability junior/entry-level engineer with demonstrable project mastery.
"""
    elif 'INTERNSHIP' in level:
        return """
SCENARIO: CANDIDATE WITH INTERNSHIP EXPERIENCE
- Prioritize real-world engineering contributions during the internship: feature delivery, REST API development, bug fixes, automated test writing, code review participation, and tools used.
- Frame bullets to emphasize professional engineering hygiene, agile collaboration, and measurable project outcomes.
"""
    elif 'APPRENTICE' in level:
        return """
SCENARIO: CANDIDATE WITH APPRENTICE EXPERIENCE
- Highlight hands-on apprenticeship engineering tasks, paired programming, structured mentorship learning, and tangible code contributions to enterprise systems.
"""
    elif '1' in level or '2' in level:
        return """
SCENARIO: EARLY CAREER (1–2 YEARS EXPERIENCE)
- Prioritize professional work experience: end-to-end feature ownership, production deployments, microservices/REST API engineering, database query optimization, automated CI/CD pipeline integration, and cross-functional collaboration.
- Highlight project achievements and technical breadth.
"""
    else:
        return """
SCENARIO: EXPERIENCED ENGINEER (3–5+ YEARS EXPERIENCE)
- Prioritize high-impact technical ownership, system design and architecture contributions, high-throughput backend services, reliability/scalability engineering, technical mentorship, and business outcomes.
- Emphasize deep architectural decisions, concurrency, caching, transaction boundaries, and system integration.
"""

def get_generation_system_instruction() -> str:
    return (
        "You are an Elite Technical Resume Strategist and Principal ATS Optimization Engine. "
        "Your mission is to generate a role-specific, ATS-optimized, high-impact resume tailored exactly to the target Job Description. "
        "CRITICAL RULES: "
        "1. Never fabricate fake companies, false employment history, or nonexistent projects. "
        "2. Surface and prioritize all relevant experience, skills, and projects found in the candidate's Complete Career Profile that were omitted from their reference resume. "
        "3. Rewrite and rephrase existing genuine engineering achievements to highlight transferable engineering principles aligned with the target role (e.g. backend concurrency, API design, database transactions, scalability). "
        "4. Focus optimizations strictly on Technical Skills, Work Experience, and Projects (with a cohesive Professional Summary). "
        "5. Output valid JSON matching the exact required schema including a granular list of changes_applied with supporting evidence."
    )

def build_resume_generation_prompt(
    target_role: str,
    target_company: str,
    experience_level: str,
    additional_experience_details: str,
    jd_analysis: Dict[str, Any],
    career_profile_data: Dict[str, Any],
    reference_resume_text: str
) -> str:
    guidance = get_experience_guidance(experience_level)

    return f"""
TARGET ROLE: {target_role}
TARGET COMPANY: {target_company or 'Enterprise Tech'}
CANDIDATE EXPERIENCE LEVEL: {experience_level}

EXPERIENCE-SPECIFIC GENERATION GUIDELINES:
{guidance}

ADDITIONAL CANDIDATE EXPERIENCE DETAILS:
{additional_experience_details or 'None provided'}

JOB DESCRIPTION ANALYSIS (TARGET BENCHMARK):
{json.dumps(jd_analysis, indent=2)}

CANDIDATE COMPLETE CAREER PROFILE (COMPREHENSIVE HISTORICAL RECORD):
{json.dumps(career_profile_data, indent=2)}

CANDIDATE REFERENCE RESUME TEXT (EXISTING SNAPSHOT):
---
{reference_resume_text or 'No reference resume provided. Construct resume purely from Complete Career Profile.'}
---

OPTIMIZATION MANDATES:
1. TECHNICAL SKILLS:
   - Organize into: languages, frameworks, databases, cloud_and_devops, developer_tools.
   - Include all JD-relevant skills the candidate has demonstrable evidence for (from profile or resume).
   - If candidate used related technologies (e.g. Node/Express backend vs Java/Spring), highlight transferable backend engineering concepts and incorporate verified Java/Spring from the career profile.

2. WORK EXPERIENCE:
   - Rewrite bullet points to use strong action verbs, quantifiable metrics (latency reductions, throughput, user base, test coverage), and target JD keywords where backed by genuine work.
   - Emphasize transferable engineering responsibilities.

3. PROJECTS:
   - Surface the most relevant projects from the candidate's career profile that demonstrate the skills demanded by the target JD.
   - Frame descriptions and highlights around architecture, performance, and key technologies.

4. PROFESSIONAL SUMMARY:
   - Craft a compelling, role-aligned 3-4 sentence professional summary reflecting the candidate's actual experience level and target designation.

5. AUDIT TRAIL (CHANGES APPLIED):
   - For every substantial modification, addition, or removal in Skills, Work Experience, or Projects, record an entry in `changes_applied`:
     - `section`: ("Technical Skills" | "Work Experience" | "Projects" | "Professional Summary")
     - `change_type`: ("ADDED" | "MODIFIED" | "REMOVED")
     - `original_content`: The original text before change
     - `updated_content`: The optimized text
     - `reason`: Why this aligns with the JD
     - `supporting_evidence`: Why this is truthful based on candidate profile/resume.

6. EVIDENCE GAPS:
   - If the JD requires specific tools/languages that have NO evidence anywhere in the candidate's profile or resume, list them in `evidence_gaps`. DO NOT fabricate them into the resume text.

Return strictly a valid JSON object matching this schema:
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
  "summary": "string",
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
      "bullet_points": ["string"]
    }}
  ],
  "projects": [
    {{
      "title": "string",
      "role": "string",
      "url": "string",
      "technologies": ["string"],
      "description": "string",
      "highlights": ["string"]
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
  "evidence_gaps": ["string"]
}}
"""
