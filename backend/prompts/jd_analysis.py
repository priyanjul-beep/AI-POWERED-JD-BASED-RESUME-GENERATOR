import json

def get_jd_analysis_system_instruction() -> str:
    return (
        "You are an expert Technical Recruiter and ATS Optimization Specialist. "
        "Your task is to analyze a Job Description (JD) and extract explicit and implicit technical requirements, "
        "distinguishing mandatory skills, preferred skills, core programming languages, frameworks, databases, "
        "cloud technologies, tools, responsibilities, and high-value ATS search keywords. "
        "You must return ONLY a structured JSON object strictly matching the required schema."
    )

def build_jd_analysis_prompt(target_role: str, target_company: str, jd_text: str) -> str:
    return f"""
Analyze the following Job Description for the target role: "{target_role}" (Company: {target_company or 'Not Specified'}).

JOB DESCRIPTION CONTENT:
---
{jd_text}
---

Extract the requirements into a valid JSON object with the following exact keys:
1. "target_role": Extracted or normalized target role name.
2. "mandatory_skills": List of must-have technical skills, languages, or tools explicitly requested.
3. "preferred_skills": List of nice-to-have or bonus qualifications.
4. "programming_languages": List of programming languages (e.g. Java, Python, TypeScript, SQL).
5. "frameworks": List of frameworks and libraries (e.g. Spring Boot, React, Django).
6. "databases": List of database technologies (e.g. PostgreSQL, MySQL, Redis, MongoDB).
7. "cloud_and_tools": List of DevOps, cloud, build, and monitoring tools (e.g. Docker, AWS, Git, Maven).
8. "key_responsibilities": List of the top 4-6 primary job duties described in the JD.
9. "important_ats_keywords": List of high-priority industry and technical terms an ATS scanner will index.

Output strictly valid JSON.
"""
