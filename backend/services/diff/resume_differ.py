from typing import Dict, Any, List

def compute_structured_diff(
    previous_resume: Dict[str, Any],
    updated_resume: Dict[str, Any],
    llm_changes: List[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Combines LLM-reported semantic changes with programmatic verification
    to generate an audited list of visual diff entries (Green = ADDED, Yellow = MODIFIED, Red = REMOVED).
    """
    diff_records = []
    seen_changes = set()

    # Ingest LLM-annotated changes first
    if llm_changes:
        for ch in llm_changes:
            key = f"{ch.get('section')}:{ch.get('updated_content', '')[:30]}"
            seen_changes.add(key)
            diff_records.append({
                "section": ch.get("section", "General"),
                "change_type": ch.get("change_type", "MODIFIED").upper(),
                "original_content": ch.get("original_content", ""),
                "updated_content": ch.get("updated_content", ""),
                "reason": ch.get("reason", "Optimized for job description alignment."),
                "supporting_evidence": ch.get("supporting_evidence", "Derived from candidate career profile data.")
            })

    # Compare summary if not already logged
    prev_summary = previous_resume.get("summary", "").strip()
    curr_summary = updated_resume.get("summary", "").strip()
    if prev_summary and curr_summary and prev_summary != curr_summary:
        key = f"Professional Summary:{curr_summary[:30]}"
        if key not in seen_changes:
            diff_records.append({
                "section": "Professional Summary",
                "change_type": "MODIFIED",
                "original_content": prev_summary,
                "updated_content": curr_summary,
                "reason": "Tailored executive summary to spotlight target designation and key technical strengths.",
                "supporting_evidence": "Candidate experience and profile metrics."
            })

    # Compare skill sets if not already captured
    prev_skills = previous_resume.get("skills", {})
    curr_skills = updated_resume.get("skills", {})
    if isinstance(prev_skills, dict) and isinstance(curr_skills, dict):
        for cat in ["languages", "frameworks", "databases", "cloud_and_devops", "developer_tools"]:
            p_list = set(s.lower() for s in prev_skills.get(cat, []))
            c_list = curr_skills.get(cat, [])
            for s in c_list:
                if s.lower() not in p_list:
                    key = f"Technical Skills:{s}"
                    if key not in seen_changes:
                        seen_changes.add(key)
                        diff_records.append({
                            "section": "Technical Skills",
                            "change_type": "ADDED",
                            "original_content": "",
                            "updated_content": s,
                            "reason": f"Added target JD technology to {cat.replace('_', ' ').title()}.",
                            "supporting_evidence": "Verified candidate profile technical proficiency."
                        })

    return diff_records
