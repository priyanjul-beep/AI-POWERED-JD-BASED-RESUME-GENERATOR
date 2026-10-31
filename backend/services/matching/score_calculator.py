import re
from typing import Dict, Any, List, Set

def _normalize_token(text: str) -> str:
    """Normalize tech name for fuzzy matching (e.g. 'React.js' -> 'react', 'Spring-Boot' -> 'springboot')."""
    return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

def _extract_all_resume_tokens(resume_data: Dict[str, Any]) -> Set[str]:
    """Collects normalized tokens from all fields of the resume."""
    tokens = set()
    raw_strings = []

    # Header
    header = resume_data.get('header', {})
    raw_strings.append(header.get('headline', ''))

    # Summary
    raw_strings.append(resume_data.get('summary', ''))

    # Skills
    skills = resume_data.get('skills', {})
    if isinstance(skills, dict):
        for category, skill_list in skills.items():
            if isinstance(skill_list, list):
                for s in skill_list:
                    raw_strings.append(str(s))
                    tokens.add(_normalize_token(str(s)))
    elif isinstance(skills, list):
        for s in skills:
            raw_strings.append(str(s))
            tokens.add(_normalize_token(str(s)))

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

    # Extract word tokens from all collected text
    combined_text = " ".join(raw_strings).lower()
    word_tokens = re.findall(r'\b[a-zA-Z0-9_\+#\.\-]{2,}\b', combined_text)
    for wt in word_tokens:
        tokens.add(_normalize_token(wt))

    return tokens, combined_text

def calculate_jd_match_scores(
    jd_analysis: Dict[str, Any],
    resume_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes deterministic, evidence-backed matching scores between the JD analysis
    and the generated resume data.
    """
    tokens, combined_text = _extract_all_resume_tokens(resume_data)

    mandatory_skills = jd_analysis.get('mandatory_skills', [])
    preferred_skills = jd_analysis.get('preferred_skills', [])
    ats_keywords = jd_analysis.get('important_ats_keywords', [])
    responsibilities = jd_analysis.get('key_responsibilities', [])

    # 1. Mandatory Skills Coverage
    matched_mandatory = []
    missing_mandatory = []
    for skill in mandatory_skills:
        clean = _normalize_token(skill)
        if clean in tokens or skill.lower() in combined_text:
            matched_mandatory.append(skill)
        else:
            missing_mandatory.append(skill)

    mandatory_score = (len(matched_mandatory) / len(mandatory_skills) * 100) if mandatory_skills else 100.0

    # 2. Preferred Skills Coverage
    matched_preferred = []
    missing_preferred = []
    for skill in preferred_skills:
        clean = _normalize_token(skill)
        if clean in tokens or skill.lower() in combined_text:
            matched_preferred.append(skill)
        else:
            missing_preferred.append(skill)

    preferred_score = (len(matched_preferred) / len(preferred_skills) * 100) if preferred_skills else 100.0

    # 3. Technical ATS Keywords Coverage
    matched_keywords = []
    missing_keywords = []
    for kw in ats_keywords:
        clean = _normalize_token(kw)
        if clean in tokens or kw.lower() in combined_text:
            matched_keywords.append(kw)
        else:
            missing_keywords.append(kw)

    keyword_score = (len(matched_keywords) / len(ats_keywords) * 100) if ats_keywords else 100.0

    # 4. Experience Relevance Score (checking for role title, seniority, and key domain tokens)
    target_role = jd_analysis.get('target_role', '')
    role_tokens = [_normalize_token(w) for w in target_role.split() if len(w) > 2]
    matched_role_tokens = [t for t in role_tokens if t in tokens]
    experience_score = (len(matched_role_tokens) / len(role_tokens) * 100) if role_tokens else 85.0
    # Minimum reasonable experience baseline if work experience items exist
    if resume_data.get('work_experience') and len(resume_data['work_experience']) > 0:
        experience_score = max(experience_score, 75.0)

    # 5. Overall Evidence-Backed Coverage
    # Weighted calculation: 40% mandatory, 20% preferred, 25% keywords, 15% experience
    overall_score = (
        (mandatory_score * 0.40) +
        (preferred_score * 0.20) +
        (keyword_score * 0.25) +
        (experience_score * 0.15)
    )

    evidence_gaps = resume_data.get('evidence_gaps', [])
    # If there are explicit unverified gaps, deduct penalty to ensure score reflects genuine evidence
    if evidence_gaps:
        penalty = min(len(evidence_gaps) * 4, 20)
        overall_score = max(30.0, overall_score - penalty)

    return {
        "overall_evidence_score": round(overall_score, 1),
        "keyword_coverage_score": round(keyword_score, 1),
        "mandatory_skills_score": round(mandatory_score, 1),
        "preferred_skills_score": round(preferred_score, 1),
        "experience_relevance_score": round(experience_score, 1),
        "matched_mandatory_skills": matched_mandatory,
        "missing_mandatory_skills": missing_mandatory,
        "matched_preferred_skills": matched_preferred,
        "missing_preferred_skills": missing_preferred,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "evidence_gaps": evidence_gaps,
    }
