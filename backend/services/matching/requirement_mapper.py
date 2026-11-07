"""
Requirement-to-Evidence Mapping Engine.
Maps each JD requirement to candidate evidence across their Complete Career Profile
and Reference Resume, categorizing status into:
- VERIFIED
- TRANSFERABLE
- USER_CONFIRMATION_REQUIRED
- UNSUPPORTED
- PROPOSED
"""
import re
from typing import Dict, Any, List, Set, Tuple

# Technical Equivalence & Transferability Dictionary
TRANSFERABLE_EQUIVALENTS = {
    "software development lifecycle": ["sdlc", "agile", "scrum", "git", "github", "jira", "ci/cd", "sprint", "code review"],
    "sdlc": ["software development lifecycle", "agile", "scrum", "git", "github", "jira", "ci/cd"],
    "software testing": ["unit testing", "functional testing", "test automation", "junit", "pytest", "jest", "cypress", "postman", "selenium", "integration test"],
    "unit testing": ["junit", "mockito", "pytest", "jest", "mocha", "chai", "test automation", "testing"],
    "functional testing": ["manual testing", "integration testing", "system testing", "postman", "selenium", "cypress", "unit testing"],
    "test automation": ["selenium", "cypress", "playwright", "junit", "pytest", "jest", "automated testing"],
    "scalable systems": ["microservices", "distributed systems", "caching", "redis", "load balancing", "docker", "kubernetes", "concurrency", "performance"],
    "rest apis": ["restful apis", "rest", "api development", "endpoints", "express", "fastapi", "spring boot", "django", "flask"],
    "restful apis": ["rest apis", "rest", "api development", "endpoints", "express", "fastapi", "spring boot"],
    "relational databases": ["sql", "postgresql", "mysql", "sqlite", "oracle", "mariadb", "sql server"],
    "sql": ["postgresql", "mysql", "sqlite", "oracle", "mariadb", "relational databases"],
    "java": ["core java", "java 8", "java 11", "java 17", "java 21", "j2ee", "jakarta ee"],
    "j2ee": ["java", "java ee", "jakarta ee", "spring boot", "servlets", "enterprise java"],
    "spring boot": ["spring mvc", "spring framework", "spring", "microservices"],
    "microservices": ["spring boot", "docker", "rest apis", "distributed systems", "kubernetes"],
    "cloud technologies": ["aws", "gcp", "azure", "docker", "kubernetes", "cloud services"]
}

def _clean_token(text: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]', '', str(text).lower())

def _matches_requirement_name(req_lower: str, text_lower: str) -> bool:
    """
    Carefully checks if requirement name matches text without false positives
    (e.g., 'Java' must never match 'JavaScript').
    """
    if req_lower == "java":
        return bool(re.search(r'\bjava\b(?!script)', text_lower))
    if req_lower == "c":
        return bool(re.search(r'\bc\b(?![\+\#])', text_lower))
    if len(req_lower) <= 4:
        return bool(re.search(rf'\b{re.escape(req_lower)}\b', text_lower))
    return req_lower in text_lower or _clean_token(req_lower) in _clean_token(text_lower)

def _extract_candidate_evidence_pool(
    career_profile_data: Dict[str, Any],
    reference_resume_text: str = ""
) -> Dict[str, List[Dict[str, str]]]:
    """
    Extracts all evidence items from candidate profile and reference resume with source attribution.
    """
    pool: Dict[str, List[Dict[str, str]]] = {
        "projects": [],
        "experiences": [],
        "skills": [],
        "education": [],
        "certifications": [],
        "reference_resume": []
    }

    # Projects from profile (checked first for practical engineering proof)
    for proj in career_profile_data.get('projects', []):
        title = proj.get('title', '')
        src = f"Project: {title}"
        for tech in proj.get('technologies', []):
            pool["projects"].append({"text": str(tech), "source": src})
        if proj.get('description'):
            pool["projects"].append({"text": proj.get('description'), "source": src})
        for hl in proj.get('highlights', []):
            pool["projects"].append({"text": str(hl), "source": src})

    # Experiences from profile
    for exp in career_profile_data.get('experiences', []):
        title = exp.get('title', '')
        company = exp.get('company', '')
        src = f"Experience at {company} ({title})"
        for tech in exp.get('technologies', []):
            pool["experiences"].append({"text": str(tech), "source": src})
        for bullet in exp.get('bullet_points', []):
            pool["experiences"].append({"text": str(bullet), "source": src})

    # Skills from profile
    for skill in career_profile_data.get('skills', []):
        s_name = skill.get('name', '') if isinstance(skill, dict) else str(skill)
        if s_name:
            pool["skills"].append({"text": s_name, "source": f"Career Profile Skill ({s_name})"})

    # Education
    for edu in career_profile_data.get('education', []):
        deg = edu.get('degree', '')
        field = edu.get('field_of_study', '')
        pool["education"].append({"text": f"{deg} in {field}", "source": f"Education ({edu.get('institution', '')})"})

    # Certifications
    for cert in career_profile_data.get('certifications', []):
        c_name = cert.get('name', '')
        pool["certifications"].append({"text": c_name, "source": f"Certification ({c_name})"})

    # Reference resume text chunks
    if reference_resume_text:
        for line in reference_resume_text.splitlines():
            line_str = line.strip()
            if len(line_str) > 5:
                pool["reference_resume"].append({"text": line_str, "source": "Reference Resume"})

    return pool

def map_single_requirement(
    req_name: str,
    category: str,
    classification: str,
    evidence_pool: Dict[str, List[Dict[str, str]]],
    experience_level: str
) -> Dict[str, Any]:
    """
    Evaluates a single requirement against the candidate evidence pool.
    """
    req_lower = req_name.lower().strip()

    # 1. Exact match check (prioritizing projects, experiences, skills)
    for section in ["projects", "experiences", "skills", "certifications", "education", "reference_resume"]:
        items = evidence_pool.get(section, [])
        for item in items:
            text = item["text"]
            text_lower = text.lower()
            
            # Direct match without false positives
            if _matches_requirement_name(req_lower, text_lower):
                return {
                    "requirement_name": req_name,
                    "category": category,
                    "classification": classification,
                    "candidate_evidence": text[:120],
                    "evidence_source": item["source"],
                    "status": "VERIFIED",
                    "recommended_action": f"Include in Technical Skills & Highlight in {section.title()}"
                }

    # 2. Transferable match check
    equiv_keywords = TRANSFERABLE_EQUIVALENTS.get(req_lower, [])
    for equiv in equiv_keywords:
        for section in ["projects", "experiences", "skills", "certifications", "education", "reference_resume"]:
            items = evidence_pool.get(section, [])
            for item in items:
                text = item["text"]
                if _matches_requirement_name(equiv.lower(), text.lower()):
                    return {
                        "requirement_name": req_name,
                        "category": category,
                        "classification": classification,
                        "candidate_evidence": f"Transferable engineering concept found: '{item['text'][:100]}'",
                        "evidence_source": item["source"],
                        "status": "TRANSFERABLE",
                        "recommended_action": f"Highlight transferable {req_name} capabilities grounded in {item['source']}"
                    }

    # 3. Plausible for experience level but unconfirmed
    is_fresher = "FRESHER" in experience_level.upper() or "INTERNSHIP" in experience_level.upper()
    foundational_requirements = ["software development lifecycle", "sdlc", "unit testing", "software testing", "debugging", "version control", "git"]
    if any(fr in req_lower for fr in foundational_requirements):
        return {
            "requirement_name": req_name,
            "category": category,
            "classification": classification,
            "candidate_evidence": "Foundational engineering practice implied by development work but explicit tools/metrics not specified.",
            "evidence_source": "Engineering Methodology",
            "status": "USER_CONFIRMATION_REQUIRED",
            "recommended_action": f"Propose industry-standard {req_name} bullet requiring user confirmation before finalizing."
        }

    # 4. Proposed standard responsibility
    if classification == "MANDATORY":
        return {
            "requirement_name": req_name,
            "category": category,
            "classification": classification,
            "candidate_evidence": "No explicit historical proof found.",
            "evidence_source": "None",
            "status": "PROPOSED",
            "recommended_action": f"Provide as a suggested project or proposed bullet requiring user confirmation; do not present as factual employment."
        }

    # 5. Unsupported
    return {
        "requirement_name": req_name,
        "category": category,
        "classification": classification,
        "candidate_evidence": "None found.",
        "evidence_source": "None",
        "status": "UNSUPPORTED",
        "recommended_action": "Record in Evidence Gap Report with actionable candidate suggestion."
    }

def build_requirement_evidence_mapping(
    jd_analysis: Dict[str, Any],
    career_profile_data: Dict[str, Any],
    reference_resume_text: str,
    experience_level: str
) -> List[Dict[str, Any]]:
    """
    Builds the complete structured requirement-to-evidence mapping list.
    """
    evidence_pool = _extract_candidate_evidence_pool(career_profile_data, reference_resume_text)
    mappings: List[Dict[str, Any]] = []

    # Map Mandatory Skills
    for skill in jd_analysis.get('mandatory_skills', []):
        mappings.append(map_single_requirement(skill, "Mandatory Technical Skill", "MANDATORY", evidence_pool, experience_level))

    # Map Programming Languages
    for lang in jd_analysis.get('programming_languages', []):
        if not any(m['requirement_name'].lower() == lang.lower() for m in mappings):
            mappings.append(map_single_requirement(lang, "Programming Language", "MANDATORY", evidence_pool, experience_level))

    # Map Frameworks
    for fw in jd_analysis.get('frameworks', []):
        if not any(m['requirement_name'].lower() == fw.lower() for m in mappings):
            mappings.append(map_single_requirement(fw, "Framework / Library", "MANDATORY", evidence_pool, experience_level))

    # Map Databases
    for db in jd_analysis.get('databases', []):
        if not any(m['requirement_name'].lower() == db.lower() for m in mappings):
            mappings.append(map_single_requirement(db, "Database & Storage", "PREFERRED", evidence_pool, experience_level))

    # Map Cloud & Tools
    for tool in jd_analysis.get('cloud_and_tools', []):
        if not any(m['requirement_name'].lower() == tool.lower() for m in mappings):
            mappings.append(map_single_requirement(tool, "Cloud & DevOps Tool", "PREFERRED", evidence_pool, experience_level))

    # Map Key Responsibilities
    for resp in jd_analysis.get('key_responsibilities', []):
        mappings.append(map_single_requirement(resp[:60], "Core Responsibility", "MANDATORY", evidence_pool, experience_level))

    # Map Preferred Skills
    for pskill in jd_analysis.get('preferred_skills', []):
        if not any(m['requirement_name'].lower() == pskill.lower() for m in mappings):
            mappings.append(map_single_requirement(pskill, "Preferred Skill", "PREFERRED", evidence_pool, experience_level))

    return mappings
