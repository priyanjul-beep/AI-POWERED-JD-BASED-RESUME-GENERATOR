import copy
import re
from typing import Dict, Any, List, Set

def filter_resume_for_jd(
    resume_data: Dict[str, Any],
    jd_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Produces a laser-focused, JD-tailored resume by omitting technical skills
    and bullet points that are NOT required for the target job.
    
    1. Technical Skills: Only retains skills that match mandatory/preferred requirements,
       languages, frameworks, databases, too ls, or ATS keywords in the JD.
    2. Work Experience Bullets: Filters out bullets that have no connection to the
       target job's requirements, keeping the experience high-impact and relevant.
    3. Projects: Omits irrelevant project bullets or projects that don't align with the JD.
    """
    if not resume_data or not isinstance(resume_data, dict):
        return {}

    filtered = copy.deepcopy(resume_data)
    if not jd_analysis or not isinstance(jd_analysis, dict):
        return filtered

    # Collect JD keywords
    target_terms: Set[str] = set()
    categories_to_check = [
        'mandatory_skills', 'preferred_skills', 'programming_languages',
        'frameworks', 'databases', 'cloud_and_tools', 'important_ats_keywords',
        'key_responsibilities'
    ]
    for cat in categories_to_check:
        for item in jd_analysis.get(cat) or []:
            clean = str(item).lower().strip()
            if clean:
                target_terms.add(clean)
                for part in re.split(r'[^a-zA-Z0-9+#\.]+', clean):
                    if len(part) >= 2 and part not in {'and', 'the', 'for', 'with', 'using', 'etc', 'such', 'into'}:
                        target_terms.add(part)

    target_role = (jd_analysis.get('target_role') or '').lower()
    for part in re.split(r'[^a-zA-Z0-9+#\.]+', target_role):
        if len(part) >= 3:
            target_terms.add(part)

    def is_relevant(text: str) -> bool:
        t_clean = text.lower()
        for term in target_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', t_clean):
                return True
        return False

    # 1. Filter Technical Skills: omit skills that are NOT required for the JD
    raw_skills = filtered.get('skills')
    if isinstance(raw_skills, dict):
        tailored_skills = {}
        for cat_name, skill_list in raw_skills.items():
            if isinstance(skill_list, list):
                kept_skills = [s for s in skill_list if is_relevant(str(s))]
                # If everything in this category was filtered out, preserve top 1-2 to avoid empty category
                tailored_skills[cat_name] = kept_skills if kept_skills else skill_list[:2]
            else:
                tailored_skills[cat_name] = skill_list
        filtered['skills'] = tailored_skills

    # 2. Filter Work Experience Bullets: omit non-relevant bullets
    for exp in filtered.get('work_experience', []):
        bullets = exp.get('bullet_points', [])
        kept_bullets = [b for b in bullets if is_relevant(str(b))]
        # Keep at least 2 bullets per work experience
        if len(kept_bullets) < 2 and len(bullets) >= 2:
            exp['bullet_points'] = kept_bullets + [b for b in bullets if b not in kept_bullets][:2 - len(kept_bullets)]
        else:
            exp['bullet_points'] = kept_bullets if kept_bullets else bullets[:2]

    # 3. Filter Project Highlights: omit non-relevant project highlights
    for proj in filtered.get('projects', []):
        highlights = proj.get('highlights', [])
        kept_highlights = [h for h in highlights if is_relevant(str(h))]
        if len(kept_highlights) < 2 and len(highlights) >= 2:
            proj['highlights'] = kept_highlights + [h for h in highlights if h not in kept_highlights][:2 - len(kept_highlights)]
        else:
            proj['highlights'] = kept_highlights if kept_highlights else highlights[:2]

    return filtered

