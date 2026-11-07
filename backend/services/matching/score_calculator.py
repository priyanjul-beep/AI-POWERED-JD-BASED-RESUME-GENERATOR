import re
from typing import Dict, Any, List, Set, Tuple

# Technical Synonym & Equivalence Normalization Dictionary
SYNONYM_MAP = {
    "j2ee": ["java", "java ee", "jakarta ee", "enterprise java", "spring boot"],
    "java": ["j2ee", "core java", "java 11", "java 17", "java 8", "java 21"],
    "software development lifecycle": ["sdlc", "agile", "scrum", "git", "ci/cd", "continuous integration"],
    "sdlc": ["software development lifecycle", "agile", "scrum", "git", "ci/cd"],
    "software testing": ["unit testing", "functional testing", "test automation", "junit", "pytest", "jest", "cypress", "postman"],
    "unit testing": ["junit", "mockito", "pytest", "jest", "automated testing", "test automation", "testing"],
    "functional testing": ["manual testing", "integration testing", "system testing", "postman", "selenium", "cypress"],
    "test automation": ["selenium", "cypress", "playwright", "junit", "pytest", "jest", "automated test"],
    "scalable systems": ["microservices", "distributed systems", "concurrency", "caching", "redis", "load balancing"],
    "rest apis": ["restful apis", "rest", "api development", "endpoints", "express", "fastapi", "spring boot"],
    "restful apis": ["rest apis", "rest", "api development", "endpoints", "express", "fastapi", "spring boot"],
    "relational databases": ["sql", "postgresql", "mysql", "sqlite", "oracle", "mariadb"],
    "sql": ["postgresql", "mysql", "sqlite", "oracle", "mariadb", "relational database"],
    "postgresql": ["postgres", "sql", "relational database"],
    "postgres": ["postgresql", "sql"],
    "kubernetes": ["k8s", "container orchestration"],
    "k8s": ["kubernetes"],
    "javascript": ["js", "es6", "node", "nodejs"],
    "typescript": ["ts", "javascript"],
    "react": ["reactjs", "react.js"],
    "reactjs": ["react", "react.js"],
    "node": ["nodejs", "node.js", "express"],
    "nodejs": ["node", "node.js", "express"],
    "spring boot": ["spring", "spring mvc", "spring framework"],
    "spring": ["spring boot", "spring mvc"],
    "docker": ["containers", "containerization", "docker compose"],
    "aws": ["amazon web services", "cloud"],
    "gcp": ["google cloud", "cloud"],
    "azure": ["microsoft azure", "cloud"],
}

def _normalize_token(text: str) -> str:
    """Normalize text for exact alphanumeric comparison."""
    return re.sub(r'[^a-zA-Z0-9]', '', str(text).lower())

def _extract_verified_resume_tokens(resume_data: Dict[str, Any]) -> Tuple[Set[str], str]:
    """
    Extracts tokens exclusively from verified, approved sections of the resume.
    EXCLUDES `proposed_content` to guarantee that unverified or proposed suggestions
    do not inflate evidence-backed match scores.
    """
    tokens = set()
    raw_strings = []

    # Header
    header = resume_data.get('header', {})
    if isinstance(header, dict):
        raw_strings.append(header.get('headline', ''))

    # Summary
    raw_strings.append(resume_data.get('summary', ''))

    # Technical Skills
    skills = resume_data.get('skills', {})
    if isinstance(skills, dict):
        for category, skill_list in skills.items():
            if isinstance(skill_list, list):
                for s in skill_list:
                    s_str = str(s)
                    raw_strings.append(s_str)
                    tokens.add(_normalize_token(s_str))
    elif isinstance(skills, list):
        for s in skills:
            s_str = str(s)
            raw_strings.append(s_str)
            tokens.add(_normalize_token(s_str))

    # Work Experience
    for exp in resume_data.get('work_experience', []):
        raw_strings.append(exp.get('title', ''))
        raw_strings.append(exp.get('company', ''))
        for t in exp.get('technologies', []):
            raw_strings.append(str(t))
            tokens.add(_normalize_token(str(t)))
        for b in exp.get('bullet_points', []):
            raw_strings.append(str(b))

    # Projects
    for proj in resume_data.get('projects', []):
        raw_strings.append(proj.get('title', ''))
        raw_strings.append(proj.get('description', ''))
        for t in proj.get('technologies', []):
            raw_strings.append(str(t))
            tokens.add(_normalize_token(str(t)))
        for h in proj.get('highlights', []):
            raw_strings.append(str(h))

    # Education & Certifications
    for edu in resume_data.get('education', []):
        raw_strings.append(edu.get('degree', ''))
        raw_strings.append(edu.get('field_of_study', ''))
    for cert in resume_data.get('certifications', []):
        raw_strings.append(cert.get('name', ''))

    # Extract words from collected text
    combined_text = " ".join(raw_strings).lower()
    word_tokens = re.findall(r'\b[a-zA-Z0-9_\+#\.\-]{2,}\b', combined_text)
    for wt in word_tokens:
        tokens.add(_normalize_token(wt))

    return tokens, combined_text

def _is_skill_matched(skill: str, tokens: Set[str], combined_text: str) -> Tuple[bool, str]:
    """
    Checks if a skill or requirement is matched via direct token, substring,
    or technical synonym normalization.
    """
    clean_skill = _normalize_token(skill)
    skill_lower = skill.lower().strip()

    # 1. Direct token or phrase in text
    if clean_skill in tokens or skill_lower in combined_text:
        return True, "Direct match in verified resume"

    # 2. Check technical synonyms
    synonyms = SYNONYM_MAP.get(skill_lower, [])
    for syn in synonyms:
        clean_syn = _normalize_token(syn)
        if clean_syn in tokens or syn in combined_text:
            return True, f"Matched via industry equivalent: '{syn}'"

    return False, "Evidence not found in verified sections"

def calculate_jd_match_scores(
    jd_analysis: Dict[str, Any],
    resume_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes deterministic, evidence-backed matching scores between the JD analysis
    and the generated resume data.
    """
    tokens, combined_text = _extract_verified_resume_tokens(resume_data)

    mandatory_skills = jd_analysis.get('mandatory_skills', [])
    preferred_skills = jd_analysis.get('preferred_skills', [])
    ats_keywords = jd_analysis.get('important_ats_keywords', [])

    # 1. Mandatory Skills Evaluation
    matched_mandatory = []
    missing_mandatory = []
    missing_mandatory_explanations = []

    for skill in mandatory_skills:
        matched, note = _is_skill_matched(skill, tokens, combined_text)
        if matched:
            matched_mandatory.append(skill)
        else:
            missing_mandatory.append(skill)
            missing_mandatory_explanations.append({
                "skill": skill,
                "reason": "Not verified in candidate career profile or reference resume.",
                "suggestion": f"If you have hands-on experience with {skill}, add project or employment details to your profile."
            })

    mandatory_score = (len(matched_mandatory) / len(mandatory_skills) * 100) if mandatory_skills else 100.0

    # 2. Preferred Skills Evaluation
    matched_preferred = []
    missing_preferred = []
    for skill in preferred_skills:
        matched, _ = _is_skill_matched(skill, tokens, combined_text)
        if matched:
            matched_preferred.append(skill)
        else:
            missing_preferred.append(skill)

    preferred_score = (len(matched_preferred) / len(preferred_skills) * 100) if preferred_skills else 100.0

    # 3. Keyword Coverage (from actual generated resume text)
    matched_keywords = []
    missing_keywords = []
    for kw in ats_keywords:
        matched, _ = _is_skill_matched(kw, tokens, combined_text)
        if matched:
            matched_keywords.append(kw)
        else:
            missing_keywords.append(kw)

    keyword_score = (len(matched_keywords) / len(ats_keywords) * 100) if ats_keywords else 100.0

    # 4. Experience & Seniority Alignment
    target_role = jd_analysis.get('target_role', '')
    role_tokens = [_normalize_token(w) for w in target_role.split() if len(w) > 2]
    matched_role_tokens = [t for t in role_tokens if t in tokens]
    experience_score = (len(matched_role_tokens) / len(role_tokens) * 100) if role_tokens else 85.0
    
    # Baseline if candidate has work experience or structured projects
    if resume_data.get('work_experience') and len(resume_data['work_experience']) > 0:
        experience_score = max(experience_score, 75.0)
    elif resume_data.get('projects') and len(resume_data['projects']) >= 2:
        experience_score = max(experience_score, 70.0)

    # 5. Overall Evidence-Backed Score
    # 40% mandatory, 20% preferred, 25% keywords, 15% experience
    overall_score = (
        (mandatory_score * 0.40) +
        (preferred_score * 0.20) +
        (keyword_score * 0.25) +
        (experience_score * 0.15)
    )

    # Normalize evidence gaps: can be list of dicts or list of strings
    raw_evidence_gaps = resume_data.get('evidence_gaps', [])
    evidence_gaps_clean = []
    for g in raw_evidence_gaps:
        if isinstance(g, dict):
            evidence_gaps_clean.append(g.get('requirement', str(g)))
        else:
            evidence_gaps_clean.append(str(g))

    # Apply moderate deduction for unverified gaps to prevent artificial score inflation
    if evidence_gaps_clean:
        penalty = min(len(evidence_gaps_clean) * 3, 18)
        overall_score = max(35.0, overall_score - penalty)

    return {
        "overall_evidence_score": round(overall_score, 1),
        "keyword_coverage_score": round(keyword_score, 1),
        "mandatory_skills_score": round(mandatory_score, 1),
        "preferred_skills_score": round(preferred_score, 1),
        "experience_relevance_score": round(experience_score, 1),
        "matched_mandatory_skills": matched_mandatory,
        "missing_mandatory_skills": missing_mandatory,
        "missing_mandatory_explanations": missing_mandatory_explanations,
        "matched_preferred_skills": matched_preferred,
        "missing_preferred_skills": missing_preferred,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "evidence_gaps": evidence_gaps_clean,
    }
