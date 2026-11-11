import json

def get_jd_analysis_system_instruction() -> str:
    return (
        "You are an expert Technical Recruiter, Staff Engineering Hiring Manager, and ATS Optimization Specialist. "
        "Your task is to analyze a Job Description (JD) and extract explicit and implicit technical requirements, "
        "distinguishing mandatory skills, preferred skills, core programming languages, frameworks, databases, "
        "cloud technologies, tools, software testing methodologies (e.g. Unit Testing, Test Automation, Functional Testing), "
        "engineering practices (e.g. SDLC, Agile, Microservices, Scalable Systems), responsibilities, and high-value ATS search keywords. "
        "You must return ONLY a structured JSON object strictly matching the required schema."
    )

def build_jd_analysis_prompt(target_role: str, target_company: str, jd_text: str) -> str:
    return f"""
Analyze the following Job Description for the target role: "{target_role}" (Company: {target_company or 'Not Specified'}).

JOB DESCRIPTION CONTENT:
---
{jd_text}
---

Extract the requirements comprehensively into a valid JSON object with the following exact keys:
1. "target_role": Extracted or normalized target role name.
2. "mandatory_skills": List of must-have technical skills, languages, testing methodologies, or engineering practices (e.g., Software Development Lifecycle, Unit Testing, Java, Spring Boot, SQL, Scalable Systems).
3. "preferred_skills": List of nice-to-have or bonus qualifications (e.g., Kafka, Docker, Kubernetes, Cloud certifications).
4. "programming_languages": List of programming languages (e.g., Java, Python, TypeScript, SQL, Go).
5. "frameworks": List of frameworks and libraries (e.g., Spring Boot, J2EE, React, Django).
6. "databases": List of database technologies (e.g., PostgreSQL, MySQL, Redis, MongoDB, Oracle).
7. "cloud_and_tools": List of DevOps, cloud, build, test, and monitoring tools (e.g., Docker, AWS, Git, Maven, JUnit, Jenkins).
8. "key_responsibilities": List of the top 4-6 primary job duties described in the JD (e.g., designing RESTful APIs, participating in SDLC, writing unit tests).
9. "important_ats_keywords": List of high-priority industry and technical terms an ATS scanner will index (including testing, architectural patterns, and methodologies).

Output strictly valid JSON.
"""
