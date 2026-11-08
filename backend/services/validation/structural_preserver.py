"""
Structural Preserver and Identity Validator.

Enforces the strict invariant policy:
"The candidate's original resume / career profile is the structural source of truth.
The application is a CONTENT OPTIMIZATION ENGINE, NOT A RESUME IDENTITY REGENERATION ENGINE."

Protected Fields (MUST NEVER CHANGE):
- header.full_name
- header.email
- header.phone
- header.location
- work_experience[].company
- work_experience[].title (designation)
- work_experience[].start_date
- work_experience[].end_date
- projects[].title (project name)
- education[].degree
- education[].institution
- education[].end_date (graduation date)
- certifications[].name
- certifications[].issuing_organization
- certifications[].issue_date
"""

import copy
import logging
import re
from typing import Dict, Any, List, Tuple, Optional

logger = logging.getLogger(__name__)

PROTECTED_HEADER_FIELDS = ["full_name", "email", "phone", "location"]
PROTECTED_EXPERIENCE_FIELDS = ["company", "title", "start_date", "end_date", "location", "is_current"]
PROTECTED_PROJECT_FIELDS = ["title"]
PROTECTED_EDUCATION_FIELDS = ["institution", "degree", "field_of_study", "start_date", "end_date", "grade", "honors"]
PROTECTED_CERTIFICATION_FIELDS = ["name", "issuing_organization", "issue_date", "credential_id"]


def build_baseline_from_profile_and_resume(
    profile_data: Optional[Dict[str, Any]] = None,
    reference_resume_data: Optional[Dict[str, Any]] = None,
    reference_resume_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Constructs a normalized baseline structural identity dictionary from
    CareerProfileSerializer data and/or parsed reference resume data.
    """
    baseline = {
        "header": {
            "full_name": "",
            "headline": "",
            "email": "",
            "phone": "",
            "location": "",
            "linkedin_url": "",
            "github_url": "",
            "portfolio_url": ""
        },
        "summary": "",
        "skills": {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "cloud_and_devops": [],
            "developer_tools": [],
            "other": []
        },
        "work_experience": [],
        "projects": [],
        "education": [],
        "certifications": [],
        "achievements_and_coding": []
    }

    # Ingest from profile_data
    if profile_data:
        for f in ["full_name", "headline", "email", "phone", "location", "linkedin_url", "github_url", "portfolio_url"]:
            if profile_data.get(f):
                baseline["header"][f] = profile_data[f]

        if profile_data.get("summary"):
            baseline["summary"] = profile_data["summary"]

        # Experiences
        raw_exps = profile_data.get("experiences") or profile_data.get("work_experience") or []
        for exp in raw_exps:
            baseline["work_experience"].append({
                "company": (exp.get("company") or "").strip(),
                "title": (exp.get("title") or "").strip(),
                "location": (exp.get("location") or "").strip(),
                "start_date": (exp.get("start_date") or "").strip(),
                "end_date": (exp.get("end_date") or "").strip(),
                "is_current": bool(exp.get("is_current", False)),
                "technologies": exp.get("technologies") or [],
                "bullet_points": exp.get("bullet_points") or []
            })

        # Projects
        raw_projs = profile_data.get("projects") or []
        for proj in raw_projs:
            baseline["projects"].append({
                "title": (proj.get("title") or "").strip(),
                "role": (proj.get("role") or "").strip(),
                "url": (proj.get("url") or "").strip(),
                "github_url": (proj.get("github_url") or "").strip(),
                "demo_url": (proj.get("demo_url") or "").strip(),
                "technologies": proj.get("technologies") or [],
                "description": (proj.get("description") or "").strip(),
                "highlights": proj.get("highlights") or []
            })

        # Education
        raw_edu = profile_data.get("education") or []
        for edu in raw_edu:
            baseline["education"].append({
                "institution": (edu.get("institution") or "").strip(),
                "degree": (edu.get("degree") or "").strip(),
                "field_of_study": (edu.get("field_of_study") or "").strip(),
                "start_date": (edu.get("start_date") or "").strip(),
                "end_date": (edu.get("end_date") or "").strip(),
                "grade": (edu.get("grade") or "").strip(),
                "honors": (edu.get("honors") or "").strip()
            })

        # Certifications
        raw_certs = profile_data.get("certifications") or []
        for cert in raw_certs:
            baseline["certifications"].append({
                "name": (cert.get("name") or "").strip(),
                "issuing_organization": (cert.get("issuing_organization") or "").strip(),
                "issue_date": (cert.get("issue_date") or "").strip(),
                "credential_id": (cert.get("credential_id") or "").strip()
            })

        # Skills
        raw_skills = profile_data.get("skills") or []
        if isinstance(raw_skills, list):
            for sk in raw_skills:
                if isinstance(sk, dict):
                    name = sk.get("name")
                    cat = (sk.get("category") or "").upper()
                    if name:
                        if "LANG" in cat:
                            baseline["skills"]["languages"].append(name)
                        elif "FRAMEWORK" in cat or "LIB" in cat:
                            baseline["skills"]["frameworks"].append(name)
                        elif "DATA" in cat:
                            baseline["skills"]["databases"].append(name)
                        elif "CLOUD" in cat or "DEVOPS" in cat:
                            baseline["skills"]["cloud_and_devops"].append(name)
                        elif "TOOL" in cat:
                            baseline["skills"]["developer_tools"].append(name)
                        else:
                            baseline["skills"]["other"].append(name)
                elif isinstance(sk, str):
                    baseline["skills"]["languages"].append(sk)

    # Ingest from reference_resume_data if baseline items are missing
    if reference_resume_data and isinstance(reference_resume_data, dict):
        ref_header = reference_resume_data.get("header") or {}
        for f in PROTECTED_HEADER_FIELDS:
            if not baseline["header"].get(f) and ref_header.get(f):
                baseline["header"][f] = ref_header[f]

        if not baseline["work_experience"] and reference_resume_data.get("work_experience"):
            for exp in reference_resume_data["work_experience"]:
                baseline["work_experience"].append({
                    "company": (exp.get("company") or "").strip(),
                    "title": (exp.get("title") or "").strip(),
                    "location": (exp.get("location") or "").strip(),
                    "start_date": (exp.get("start_date") or "").strip(),
                    "end_date": (exp.get("end_date") or "").strip(),
                    "is_current": bool(exp.get("is_current", False)),
                    "technologies": exp.get("technologies") or [],
                    "bullet_points": exp.get("bullet_points") or []
                })

        if not baseline["projects"] and reference_resume_data.get("projects"):
            for proj in reference_resume_data["projects"]:
                baseline["projects"].append({
                    "title": (proj.get("title") or "").strip(),
                    "role": (proj.get("role") or "").strip(),
                    "url": (proj.get("url") or "").strip(),
                    "github_url": (proj.get("github_url") or "").strip(),
                    "demo_url": (proj.get("demo_url") or "").strip(),
                    "technologies": proj.get("technologies") or [],
                    "description": (proj.get("description") or "").strip(),
                    "highlights": proj.get("highlights") or []
                })

        if not baseline["education"] and reference_resume_data.get("education"):
            for edu in reference_resume_data["education"]:
                baseline["education"].append({
                    "institution": (edu.get("institution") or "").strip(),
                    "degree": (edu.get("degree") or "").strip(),
                    "field_of_study": (edu.get("field_of_study") or "").strip(),
                    "start_date": (edu.get("start_date") or "").strip(),
                    "end_date": (edu.get("end_date") or "").strip(),
                    "grade": (edu.get("grade") or "").strip(),
                    "honors": (edu.get("honors") or "").strip()
                })

        if not baseline["certifications"] and reference_resume_data.get("certifications"):
            for cert in reference_resume_data["certifications"]:
                baseline["certifications"].append({
                    "name": (cert.get("name") or "").strip(),
                    "issuing_organization": (cert.get("issuing_organization") or "").strip(),
                    "issue_date": (cert.get("issue_date") or "").strip(),
                    "credential_id": (cert.get("credential_id") or "").strip()
                })

    # Ingest achievements_and_coding if present in profile or reference resume
    ach_list = (
        (profile_data.get("achievements_and_coding") if profile_data else None)
        or (profile_data.get("achievements") if profile_data else None)
        or (reference_resume_data.get("achievements_and_coding") if isinstance(reference_resume_data, dict) else None)
        or (reference_resume_data.get("achievements") if isinstance(reference_resume_data, dict) else None)
    )
    if isinstance(ach_list, list):
        baseline["achievements_and_coding"] = [str(x).strip() for x in ach_list if str(x).strip()]

    return baseline


def _clean_str(val: Any) -> str:
    return str(val or "").strip().lower()


def enforce_structural_identity(
    baseline: Dict[str, Any],
    generated_resume: Dict[str, Any],
    reference_resume_text: str = ""
) -> Dict[str, Any]:
    """
    Enforces the candidate's baseline structural identity onto the generated resume.
    
    1. Header: full_name, email, phone, location are strictly restored.
    2. Work Experience:
       - Every item's company, title, start_date, end_date, location, is_current
         are strictly restored to match baseline records.
       - Any extra fictional work experiences generated by LLM are stripped,
         and their bullet points moved to proposed_content.
       - Only bullet_points and technologies are allowed to be optimized.
    3. Projects:
       - Every item's project title is strictly restored.
       - Any extra fictional projects generated by LLM are stripped,
         and their highlights moved to proposed_content.
       - Only description, highlights, technologies, and role are allowed to be optimized.
    4. Education:
       - degree, institution, start_date, end_date, field_of_study, grade, honors
         are strictly restored to match baseline records.
    5. Certifications:
       - name, issuing_organization, issue_date, credential_id
         are strictly restored to match baseline records.
    6. Audit Trail (changes_applied):
       - Removes any records modifying protected fields.
    """
    sanitized = copy.deepcopy(generated_resume)

    if not isinstance(sanitized.get("header"), dict):
        sanitized["header"] = {}

    base_header = baseline.get("header") or {}

    # 1. ENFORCE HEADER
    for field in PROTECTED_HEADER_FIELDS:
        if base_header.get(field):
            sanitized["header"][field] = base_header[field]

    # Preserve URLs if baseline has them
    for url_field in ["linkedin_url", "github_url", "portfolio_url"]:
        if base_header.get(url_field) and not sanitized["header"].get(url_field):
            sanitized["header"][url_field] = base_header[url_field]

    # Ensure proposed_content list exists
    if sanitized.get("proposed_content") is None or not isinstance(sanitized["proposed_content"], list):
        sanitized["proposed_content"] = []

    # 2. ENFORCE WORK EXPERIENCE
    base_experiences = baseline.get("work_experience") or []
    gen_experiences = sanitized.get("work_experience") or []
    sanitized_experiences = []
    ref_lower = (reference_resume_text or "").lower()

    if not base_experiences:
        if ref_lower:
            # Check if generated experiences are substantiated by reference resume text
            for gen_exp in gen_experiences:
                gen_co = _clean_str(gen_exp.get("company"))
                gen_ti = _clean_str(gen_exp.get("title"))
                co_words = [w for w in re.split(r'[^a-zA-Z0-9]+', gen_co) if len(w) > 3]
                ti_words = [w for w in re.split(r'[^a-zA-Z0-9]+', gen_ti) if len(w) > 3]
                is_substantiated = (
                    (gen_co and gen_co in ref_lower) or
                    (gen_ti and gen_ti in ref_lower) or
                    (co_words and any(w in ref_lower for w in co_words)) or
                    (ti_words and any(w in ref_lower for w in ti_words))
                )
                if is_substantiated:
                    sanitized_experiences.append(gen_exp)
                else:
                    bullets = gen_exp.get("bullet_points") or []
                    for b in bullets:
                        sanitized["proposed_content"].append({
                            "target_section": "Work Experience",
                            "proposed_text": b,
                            "targeted_jd_requirement": gen_exp.get("title") or "Work Experience",
                            "reason": f"Proposed responsibility bullet for target role (not verified in profile history).",
                            "requires_user_confirmation": True
                        })
            sanitized["work_experience"] = sanitized_experiences
        else:
            # Candidate has NO work experience / internship in baseline (e.g. Fresher)
            # Any generated experience is a hallucination / fictional employer.
            for phantom_exp in gen_experiences:
                bullets = phantom_exp.get("bullet_points") or []
                for b in bullets:
                    sanitized["proposed_content"].append({
                        "target_section": "Work Experience",
                        "proposed_text": b,
                        "targeted_jd_requirement": phantom_exp.get("title") or "Work Experience",
                        "reason": f"Proposed responsibility bullet for target role (not verified in profile history).",
                        "requires_user_confirmation": True
                    })
            sanitized["work_experience"] = []
    else:
        # Align generated experiences with baseline experiences
        # Match by company name or index
        used_gen_indices = set()
        for idx, base_exp in enumerate(base_experiences):
            best_gen = None
            best_gen_idx = None

            # First try matching by company or title
            base_co = _clean_str(base_exp.get("company"))
            base_ti = _clean_str(base_exp.get("title"))

            for g_idx, gen_exp in enumerate(gen_experiences):
                if g_idx in used_gen_indices:
                    continue
                gen_co = _clean_str(gen_exp.get("company"))
                gen_ti = _clean_str(gen_exp.get("title"))

                if base_co and (base_co in gen_co or gen_co in base_co):
                    best_gen = gen_exp
                    best_gen_idx = g_idx
                    break
                elif base_ti and (base_ti in gen_ti or gen_ti in base_ti):
                    best_gen = gen_exp
                    best_gen_idx = g_idx
                    break

            # Fallback to positional match
            if best_gen is None and idx < len(gen_experiences) and idx not in used_gen_indices:
                best_gen = gen_experiences[idx]
                best_gen_idx = idx

            if best_gen is not None:
                used_gen_indices.add(best_gen_idx)
                # STRICT RESTORATION of protected fields
                merged_exp = {
                    "company": base_exp["company"],
                    "title": base_exp["title"],
                    "location": base_exp.get("location") or best_gen.get("location") or "",
                    "start_date": base_exp.get("start_date") or best_gen.get("start_date") or "",
                    "end_date": base_exp.get("end_date") or best_gen.get("end_date") or "",
                    "is_current": base_exp.get("is_current", best_gen.get("is_current", False)),
                    "technologies": best_gen.get("technologies") or base_exp.get("technologies") or [],
                    "bullet_points": best_gen.get("bullet_points") or base_exp.get("bullet_points") or []
                }
                sanitized_experiences.append(merged_exp)
            else:
                # Omitted baseline item; restore fully
                sanitized_experiences.append(copy.deepcopy(base_exp))

        # Check for extra experiences beyond baseline count
        for g_idx, gen_exp in enumerate(gen_experiences):
            if g_idx not in used_gen_indices:
                gen_co = _clean_str(gen_exp.get("company"))
                gen_ti = _clean_str(gen_exp.get("title"))
                co_words = [w for w in re.split(r'[^a-zA-Z0-9]+', gen_co) if len(w) > 3]
                ti_words = [w for w in re.split(r'[^a-zA-Z0-9]+', gen_ti) if len(w) > 3]
                is_substantiated = (
                    ref_lower and (
                        (gen_co and gen_co in ref_lower) or
                        (gen_ti and gen_ti in ref_lower) or
                        (co_words and any(w in ref_lower for w in co_words)) or
                        (ti_words and any(w in ref_lower for w in ti_words))
                    )
                )
                if is_substantiated:
                    sanitized_experiences.append(gen_exp)
                else:
                    bullets = gen_exp.get("bullet_points") or []
                    for b in bullets:
                        sanitized["proposed_content"].append({
                            "target_section": "Work Experience",
                            "proposed_text": b,
                            "targeted_jd_requirement": gen_exp.get("title") or "Work Experience",
                            "reason": f"Proposed role-specific bullet from {gen_exp.get('company', 'suggested experience')}.",
                            "requires_user_confirmation": True
                        })

        sanitized["work_experience"] = sanitized_experiences

    # 3. ENFORCE PROJECTS
    base_projects = baseline.get("projects") or []
    gen_projects = sanitized.get("projects") or []
    sanitized_projects = []

    if not base_projects:
        if ref_lower:
            for gen_proj in gen_projects:
                gen_title = _clean_str(gen_proj.get("title"))
                proj_words = [w for w in re.split(r'[^a-zA-Z0-9]+', gen_title) if len(w) > 3]
                is_substantiated = (
                    (gen_title and gen_title in ref_lower) or
                    (proj_words and any(w in ref_lower for w in proj_words))
                )
                if is_substantiated:
                    sanitized_projects.append(gen_proj)
                else:
                    highlights = gen_proj.get("highlights") or []
                    desc = gen_proj.get("description")
                    items = ([desc] if desc else []) + highlights
                    for h in items:
                        sanitized["proposed_content"].append({
                            "target_section": "Projects",
                            "proposed_text": h,
                            "targeted_jd_requirement": gen_proj.get("title") or "Project Engineering",
                            "reason": f"Suggested project implementation bullet requiring candidate confirmation.",
                            "requires_user_confirmation": True
                        })
            sanitized["projects"] = sanitized_projects
        else:
            for phantom_proj in gen_projects:
                highlights = phantom_proj.get("highlights") or []
                desc = phantom_proj.get("description")
                items = ([desc] if desc else []) + highlights
                for h in items:
                    sanitized["proposed_content"].append({
                        "target_section": "Projects",
                        "proposed_text": h,
                        "targeted_jd_requirement": phantom_proj.get("title") or "Project Engineering",
                        "reason": f"Suggested project implementation bullet requiring candidate confirmation.",
                        "requires_user_confirmation": True
                    })
            sanitized["projects"] = []
    else:
        used_proj_indices = set()
        for idx, base_proj in enumerate(base_projects):
            best_gen = None
            best_gen_idx = None
            base_title = _clean_str(base_proj.get("title"))

            for g_idx, gen_proj in enumerate(gen_projects):
                if g_idx in used_proj_indices:
                    continue
                gen_title = _clean_str(gen_proj.get("title"))
                if base_title and (base_title in gen_title or gen_title in base_title):
                    best_gen = gen_proj
                    best_gen_idx = g_idx
                    break

            if best_gen is None and idx < len(gen_projects) and idx not in used_proj_indices:
                best_gen = gen_projects[idx]
                best_gen_idx = idx

            if best_gen is not None:
                used_proj_indices.add(best_gen_idx)
                merged_proj = {
                    "title": base_proj["title"],  # NEVER CHANGE ORIGINAL PROJECT NAME
                    "role": best_gen.get("role") or base_proj.get("role") or "",
                    "url": base_proj.get("url") or best_gen.get("url") or "",
                    "github_url": best_gen.get("github_url") or base_proj.get("github_url") or "",
                    "demo_url": best_gen.get("demo_url") or base_proj.get("demo_url") or "",
                    "technologies": best_gen.get("technologies") or base_proj.get("technologies") or [],
                    "description": best_gen.get("description") or base_proj.get("description") or "",
                    "highlights": best_gen.get("highlights") or base_proj.get("highlights") or []
                }
                sanitized_projects.append(merged_proj)
            else:
                sanitized_projects.append(copy.deepcopy(base_proj))

        # Check for extra projects beyond baseline count
        for g_idx, gen_proj in enumerate(gen_projects):
            if g_idx not in used_proj_indices:
                gen_title = _clean_str(gen_proj.get("title"))
                proj_words = [w for w in re.split(r'[^a-zA-Z0-9]+', gen_title) if len(w) > 3]
                is_substantiated = (
                    ref_lower and (
                        (gen_title and gen_title in ref_lower) or
                        (proj_words and any(w in ref_lower for w in proj_words))
                    )
                )
                if is_substantiated:
                    sanitized_projects.append(gen_proj)
                else:
                    highlights = gen_proj.get("highlights") or []
                    desc = gen_proj.get("description")
                    items = ([desc] if desc else []) + highlights
                    for h in items:
                        sanitized["proposed_content"].append({
                            "target_section": "Projects",
                            "proposed_text": h,
                            "targeted_jd_requirement": gen_proj.get("title") or "Suggested Project",
                            "reason": f"Suggested implementation bullet for target JD (not in candidate projects).",
                            "requires_user_confirmation": True
                        })

        sanitized["projects"] = sanitized_projects

    # 4. ENFORCE EDUCATION
    base_education = baseline.get("education") or []
    gen_education = sanitized.get("education") or []
    sanitized_education = []

    if base_education:
        for idx, base_edu in enumerate(base_education):
            gen_edu = gen_education[idx] if idx < len(gen_education) else {}
            sanitized_education.append({
                "institution": base_edu["institution"],  # STRICT
                "degree": base_edu["degree"],            # STRICT
                "field_of_study": base_edu.get("field_of_study") or gen_edu.get("field_of_study") or "",
                "start_date": base_edu.get("start_date") or gen_edu.get("start_date") or "",
                "end_date": base_edu.get("end_date") or gen_edu.get("end_date") or "",
                "grade": base_edu.get("grade") or gen_edu.get("grade") or "",
                "honors": base_edu.get("honors") or gen_edu.get("honors") or ""
            })
        sanitized["education"] = sanitized_education
    elif gen_education:
        sanitized["education"] = gen_education

    # 5. ENFORCE CERTIFICATIONS
    base_certifications = baseline.get("certifications") or []
    gen_certifications = sanitized.get("certifications") or []
    sanitized_certifications = []

    if base_certifications:
        for idx, base_cert in enumerate(base_certifications):
            gen_cert = gen_certifications[idx] if idx < len(gen_certifications) else {}
            sanitized_certifications.append({
                "name": base_cert["name"],                                     # STRICT
                "issuing_organization": base_cert["issuing_organization"],     # STRICT
                "issue_date": base_cert.get("issue_date") or gen_cert.get("issue_date") or "",
                "credential_id": base_cert.get("credential_id") or gen_cert.get("credential_id") or ""
            })
        sanitized["certifications"] = sanitized_certifications
    elif gen_certifications:
        sanitized["certifications"] = gen_certifications

    # 6. ENFORCE/INTEGRATE VERIFIED TECHNICAL SKILLS FROM PROFILE
    base_skills = baseline.get("skills") or {}
    if not isinstance(sanitized.get("skills"), dict):
        sanitized["skills"] = {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "cloud_and_devops": [],
            "developer_tools": []
        }
    if isinstance(base_skills, dict):
        for cat in ["languages", "frameworks", "databases", "cloud_and_devops", "developer_tools"]:
            existing = sanitized["skills"].get(cat) or []
            existing_lower = set(s.strip().lower() for s in existing)
            for b_skill in base_skills.get(cat, []):
                if b_skill.strip().lower() not in existing_lower:
                    existing.append(b_skill)
            sanitized["skills"][cat] = existing

    # 7. ENFORCE ACHIEVEMENTS, HACKATHONS & CODING PROFILES
    ach_coding = (
        sanitized.get("achievements_and_coding")
        or sanitized.get("achievements")
        or baseline.get("achievements_and_coding")
        or []
    )
    if ach_coding:
        sanitized["achievements_and_coding"] = ach_coding

    # 8. SANITIZE AUDIT TRAIL (changes_applied)
    # "Do not highlight changes to immutable fields because those fields must never change."
    raw_changes = sanitized.get("changes_applied") or []
    clean_changes = []

    # Prohibited patterns in audit changes
    immutable_tokens = [
        "company", "employer", "organization", "designation", "job title",
        "intern to", "degree", "university", "college", "school",
        "full name", "email", "phone", "location", "certification"
    ]

    for ch in raw_changes:
        sec = (ch.get("section") or "").strip().lower()
        reason = (ch.get("reason") or "").lower()
        orig = (ch.get("original_content") or "").lower()
        upd = (ch.get("updated_content") or "").lower()

        # Reject if change claims to have altered header or immutable identity
        if "header" in sec or "contact" in sec or "identity" in sec:
            continue

        # Reject if reason or update indicates changing company name or job title
        is_immutable_change = False
        for tok in immutable_tokens:
            if (tok in reason or tok in orig or tok in upd) and ("bullet" not in reason and "bullet" not in orig and "bullet" not in upd and "technology" not in reason):
                # Check if it was an actual company or title rename
                if any(k in reason for k in ["rename company", "change title", "upgrade designation", "change degree"]):
                    is_immutable_change = True
                    break

        if not is_immutable_change:
            clean_changes.append(ch)

    sanitized["changes_applied"] = clean_changes

    # 7. PRESERVE SECTION ORDERING
    ordered_schema_keys = [
        "header",
        "summary",
        "skills",
        "work_experience",
        "projects",
        "education",
        "certifications",
        "changes_applied",
        "evidence_gaps",
        "requirement_mappings",
        "proposed_content"
    ]
    ordered_result = {}
    for key in ordered_schema_keys:
        if key in sanitized:
            ordered_result[key] = sanitized[key]
    # In case any other top-level keys exist
    for key, val in sanitized.items():
        if key not in ordered_result:
            ordered_result[key] = val

    return ordered_result


def validate_structural_identity(
    baseline: Dict[str, Any],
    candidate_resume: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Validates that candidate_resume preserves all protected fields from baseline.
    Returns (is_valid, list_of_violations).
    """
    violations = []

    # 1. Header validation
    base_header = baseline.get("header") or {}
    cand_header = candidate_resume.get("header") or {}

    for f in PROTECTED_HEADER_FIELDS:
        expected = base_header.get(f)
        if expected and cand_header.get(f) != expected:
            violations.append(f"Header field '{f}' modified: expected '{expected}', found '{cand_header.get(f)}'")

    # 2. Work Experience validation
    base_exps = baseline.get("work_experience") or []
    cand_exps = candidate_resume.get("work_experience") or []

    if len(cand_exps) != len(base_exps):
        violations.append(f"Work experience count mismatch: expected {len(base_exps)}, found {len(cand_exps)}")

    for i, base_exp in enumerate(base_exps):
        if i >= len(cand_exps):
            break
        cand_exp = cand_exps[i]
        for f in ["company", "title", "start_date", "end_date"]:
            expected = base_exp.get(f)
            if expected and cand_exp.get(f) != expected:
                violations.append(f"Experience[{i}] field '{f}' modified: expected '{expected}', found '{cand_exp.get(f)}'")

    # 3. Projects validation
    base_projs = baseline.get("projects") or []
    cand_projs = candidate_resume.get("projects") or []

    if len(cand_projs) != len(base_projs):
        violations.append(f"Project count mismatch: expected {len(base_projs)}, found {len(cand_projs)}")

    for i, base_proj in enumerate(base_projs):
        if i >= len(cand_projs):
            break
        cand_proj = cand_projs[i]
        expected_title = base_proj.get("title")
        if expected_title and cand_proj.get("title") != expected_title:
            violations.append(f"Project[{i}] title modified: expected '{expected_title}', found '{cand_proj.get('title')}'")

    # 4. Education validation
    base_edu = baseline.get("education") or []
    cand_edu = candidate_resume.get("education") or []

    for i, be in enumerate(base_edu):
        if i >= len(cand_edu):
            violations.append(f"Education[{i}] missing in candidate resume")
            continue
        ce = cand_edu[i]
        for f in ["institution", "degree"]:
            expected = be.get(f)
            if expected and ce.get(f) != expected:
                violations.append(f"Education[{i}] field '{f}' modified: expected '{expected}', found '{ce.get(f)}'")

    # 5. Certifications validation
    base_certs = baseline.get("certifications") or []
    cand_certs = candidate_resume.get("certifications") or []

    for i, bc in enumerate(base_certs):
        if i >= len(cand_certs):
            violations.append(f"Certification[{i}] missing in candidate resume")
            continue
        cc = cand_certs[i]
        for f in ["name", "issuing_organization"]:
            expected = bc.get(f)
            if expected and cc.get(f) != expected:
                violations.append(f"Certification[{i}] field '{f}' modified: expected '{expected}', found '{cc.get(f)}'")

    return (len(violations) == 0, violations)
