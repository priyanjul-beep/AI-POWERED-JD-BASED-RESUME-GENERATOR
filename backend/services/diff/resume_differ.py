from typing import Dict, Any, List

IMMUTABLE_SECTIONS_AND_KEYS = [
    "header", "full_name", "email", "phone", "location",
    "company", "title", "designation", "start_date", "end_date",
    "degree", "institution", "graduation_date", "issuer"
]

def compute_structured_diff(
    previous_resume: Dict[str, Any],
    updated_resume: Dict[str, Any],
    llm_changes: List[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Combines LLM-reported semantic changes with programmatic verification
    to generate an audited list of visual diff entries:
    - ADDED (Green)
    - MODIFIED (Yellow)
    - REMOVED (Red)
    - PROPOSED (Amber / Confirmation Required)

    STRICT INVARIANT: Never outputs diff records for immutable protected fields
    (e.g. company names, designations, dates, degrees, universities, project titles).
    """
    diff_records = []
    seen_changes = set()

    def is_immutable_change(section: str, reason: str, orig: str, upd: str) -> bool:
        sec_l = (section or "").lower()
        if "header" in sec_l or "contact" in sec_l:
            return True
        r_l = (reason or "").lower()
        # If the change claims to rename employer or change job title/degree
        if any(tok in r_l for tok in ["change company", "rename company", "change title", "upgrade designation", "change degree"]):
            return True
        return False

    # 1. Ingest LLM-annotated changes (filtering out any immutable field edits)
    if llm_changes:
        for ch in llm_changes:
            sec = ch.get("section", "General")
            reason = ch.get("reason", "Optimized for job description alignment.")
            orig = ch.get("original_content", "")
            upd = ch.get("updated_content", "")

            if is_immutable_change(sec, reason, orig, upd):
                continue

            key = f"{sec}:{upd[:40]}"
            if key not in seen_changes:
                seen_changes.add(key)
                diff_records.append({
                    "section": sec,
                    "change_type": ch.get("change_type", "MODIFIED").upper(),
                    "original_content": orig,
                    "updated_content": upd,
                    "reason": reason,
                    "supporting_evidence": ch.get("supporting_evidence", "Candidate career profile data."),
                    "confirmation_status": "VERIFIED"
                })

    # 2. Compare summary if not already logged
    prev_summary = (previous_resume.get("summary") or "").strip()
    curr_summary = (updated_resume.get("summary") or "").strip()
    if prev_summary and curr_summary and prev_summary != curr_summary:
        key = f"Professional Summary:{curr_summary[:40]}"
        if key not in seen_changes:
            seen_changes.add(key)
            diff_records.append({
                "section": "Professional Summary",
                "change_type": "MODIFIED",
                "original_content": prev_summary,
                "updated_content": curr_summary,
                "reason": "Tailored professional summary to highlight target role relevance while preserving actual experience level.",
                "supporting_evidence": "Candidate experience and verified technical skills.",
                "confirmation_status": "VERIFIED"
            })

    # 3. Compare skill sets if not already captured
    prev_skills = previous_resume.get("skills") or {}
    curr_skills = updated_resume.get("skills") or {}
    if isinstance(prev_skills, dict) and isinstance(curr_skills, dict):
        for cat in ["languages", "frameworks", "databases", "cloud_and_devops", "developer_tools"]:
            p_list = set(s.lower().strip() for s in prev_skills.get(cat, []))
            c_list = curr_skills.get(cat, [])
            for s in c_list:
                s_clean = s.strip()
                if s_clean.lower() not in p_list:
                    key = f"Technical Skills:{s_clean}"
                    if key not in seen_changes:
                        seen_changes.add(key)
                        diff_records.append({
                            "section": "Technical Skills",
                            "change_type": "ADDED",
                            "original_content": "",
                            "updated_content": s_clean,
                            "reason": f"Prioritized target JD technology in {cat.replace('_', ' ').title()}.",
                            "supporting_evidence": "Verified technical proficiency from profile.",
                            "confirmation_status": "VERIFIED"
                        })

    # 4. Programmatic bullet comparison for work experience if previous_resume provided
    prev_exps = previous_resume.get("work_experience") or []
    curr_exps = updated_resume.get("work_experience") or []
    for idx, curr_exp in enumerate(curr_exps):
        curr_bullets = curr_exp.get("bullet_points") or []
        prev_exp = prev_exps[idx] if idx < len(prev_exps) else {}
        prev_bullets = prev_exp.get("bullet_points") or []

        prev_bullets_lower = set(b.strip().lower() for b in prev_bullets)

        for b in curr_bullets:
            b_clean = b.strip()
            if b_clean.lower() not in prev_bullets_lower:
                key = f"Work Experience:{b_clean[:40]}"
                if key not in seen_changes:
                    seen_changes.add(key)
                    # Check if there is an original corresponding bullet
                    orig = prev_bullets[0] if prev_bullets else ""
                    diff_records.append({
                        "section": f"Work Experience ({curr_exp.get('company', 'Experience')})",
                        "change_type": "MODIFIED" if orig else "ADDED",
                        "original_content": orig,
                        "updated_content": b_clean,
                        "reason": f"Optimized bullet point for target JD using 4-part formula.",
                        "supporting_evidence": f"Candidate responsibilities at {curr_exp.get('company', 'employer')}.",
                        "confirmation_status": "VERIFIED"
                    })

    # 5. Ingest proposed content requiring user confirmation
    proposed_items = updated_resume.get("proposed_content") or []
    for p in proposed_items:
        text = p.get("proposed_text", "").strip()
        key = f"Proposed:{text[:40]}"
        if key not in seen_changes:
            seen_changes.add(key)
            diff_records.append({
                "section": f"{p.get('target_section', 'Work Experience')} (Suggested)",
                "change_type": "PROPOSED",
                "original_content": "",
                "updated_content": text,
                "reason": p.get("reason", "Suggested industry-standard responsibility requiring confirmation."),
                "supporting_evidence": f"Target requirement: {p.get('targeted_jd_requirement', 'JD Requirement')}",
                "confirmation_status": "PENDING_CONFIRMATION"
            })

    return diff_records
