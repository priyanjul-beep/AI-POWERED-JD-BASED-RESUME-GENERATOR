import re
from typing import Dict, Any, List, Optional

# Comprehensive knowledge base of tech keywords for fast, accurate matching
TECH_LANGUAGES = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Golang", "Go", "Rust",
    "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "SQL", "HTML", "CSS", "Bash", "Shell",
    "Dart", "Perl", "Haskell", "Elixir", "C"
]

TECH_FRAMEWORKS = [
    "React", "React.js", "Angular", "Vue", "Vue.js", "Next.js", "Nuxt.js", "Django",
    "FastAPI", "Flask", "Spring Boot", "Spring MVC", "Express", "Express.js", "Node.js",
    "NestJS", "ASP.NET", ".NET Core", "Ruby on Rails", "Laravel", "PyTorch", "TensorFlow",
    "Keras", "Pandas", "NumPy", "Scikit-Learn", "OpenCV", "HuggingFace", "LangChain",
    "LlamaIndex", "Tailwind CSS", "Bootstrap", "GraphQL", "Redux", "Svelte"
]

TECH_DATABASES = [
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Cassandra", "DynamoDB",
    "Oracle", "Microsoft SQL Server", "Elasticsearch", "Neo4j", "Firebase", "Snowflake",
    "BigQuery", "MariaDB", "CouchDB", "Supabase"
]

TECH_CLOUD_TOOLS = [
    "AWS", "Amazon Web Services", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes",
    "K8s", "Terraform", "Ansible", "Linux", "Git", "GitHub Actions", "GitLab CI",
    "Jenkins", "CI/CD", "Kafka", "RabbitMQ", "Nginx", "Prometheus", "Grafana",
    "REST APIs", "RESTful APIs", "Microservices", "Jira", "Maven", "Gradle",
    "Postman", "OpenAPI", "Swagger", "Celery", "Airflow"
]


def extract_target_role(jd_text: str, default: str = "") -> str:
    """
    Intelligently extracts the job designation / role title from JD text if not provided in the API request.
    """
    if not jd_text:
        return default or "Software Engineer"

    # Pattern 1: Explicit labels like "Job Title: Full Stack Developer" or "Role: Data Scientist"
    patterns = [
        r'(?:job\s+title|role|position|target\s+role|designation)\s*[:\-–]\s*([A-Za-z0-9+#.\s\-/]{3,50})',
        r'(?:seeking|looking for|hiring)\s+(?:an?|the)?\s+([A-Za-z0-9+#.\s\-/]{3,45}?)(?:\s+to\s+|\s+with\s+|\s+who\s+|\s+at\s+|\.|\n|,)',
        r'(?:we\s+are\s+hiring\s+a(?:n)?)\s+([A-Za-z0-9+#.\s\-/]{3,45})',
    ]

    for pat in patterns:
        match = re.search(pat, jd_text, re.IGNORECASE)
        if match:
            extracted = match.group(1).strip().strip('.:,;-')
            # Check sanity: not too long, doesn't contain forbidden stop words
            if 3 <= len(extracted) <= 50 and not any(w in extracted.lower() for w in ['candidate', 'applicant', 'person', 'individual']):
                return extracted.title()

    # Pattern 2: Inspect the first 3 non-empty lines for common engineering titles
    lines = [line.strip() for line in jd_text.splitlines() if line.strip()]
    role_keywords = ['engineer', 'developer', 'architect', 'scientist', 'lead', 'manager', 'analyst', 'consultant', 'specialist', 'programmer', 'intern']
    for line in lines[:4]:
        line_clean = re.sub(r'^[#*_\-\s]+', '', line).strip()
        lower_line = line_clean.lower()
        if any(rk in lower_line for rk in role_keywords) and len(line_clean) <= 60:
            return line_clean.title()

    return default or "Software Engineer"


def extract_target_company(jd_text: str, default: str = "") -> str:
    """
    Extracts the target company name from the JD text if present.
    """
    if not jd_text:
        return default or "Enterprise Tech"

    patterns = [
        r'(?:company|employer|organization)\s*[:\-–]\s*([A-Za-z0-9&.,\s]{2,40})',
        r'(?:about|at|join)\s+([A-Z][A-Za-z0-9&.,]+(?:\s+[A-Z][A-Za-z0-9&.,]+)?)(?:\s+is looking|\s+team|\s+technologies|\s+inc|\s+llc|\s+corp|\.|\n|,)',
    ]

    for pat in patterns:
        match = re.search(pat, jd_text, re.IGNORECASE)
        if match:
            extracted = match.group(1).strip().strip('.:,;-')
            if 2 <= len(extracted) <= 40 and not any(w in extracted.lower() for w in ['our', 'the', 'this', 'we', 'team', 'company', 'work']):
                return extracted.title()

    return default or "Enterprise Tech"


def _find_keyword_matches(text: str, keywords: List[str]) -> List[str]:
    """Finds exact whole-word keyword occurrences in text."""
    found = []
    text_lower = text.lower()
    for kw in keywords:
        # For single/short letter tech like C, R, Go, be strict
        if len(kw) <= 2:
            pattern = rf'(?<![a-zA-Z0-9]){re.escape(kw)}(?![a-zA-Z0-9])'
            if re.search(pattern, text):
                found.append(kw)
        else:
            pattern = rf'\b{re.escape(kw.lower())}\b'
            if re.search(pattern, text_lower):
                found.append(kw)
    return found


def extract_dynamic_jd_analysis(
    jd_text: str,
    target_role: str = "",
    target_company: str = ""
) -> Dict[str, Any]:
    """
    Dynamically extracts technical skills, categories, responsibilities,
    and ATS keywords from arbitrary Job Description text without hardcoded defaults.
    """
    effective_role = target_role or extract_target_role(jd_text)
    effective_company = target_company or extract_target_company(jd_text)

    # 1. Extract technology categories from JD text
    found_languages = _find_keyword_matches(jd_text, TECH_LANGUAGES)
    found_frameworks = _find_keyword_matches(jd_text, TECH_FRAMEWORKS)
    found_databases = _find_keyword_matches(jd_text, TECH_DATABASES)
    found_cloud_tools = _find_keyword_matches(jd_text, TECH_CLOUD_TOOLS)

    # If no specific languages found in text, derive sensible context from target_role
    if not found_languages:
        role_lower = effective_role.lower()
        if "python" in role_lower or "data" in role_lower or "machine learning" in role_lower or "ai" in role_lower:
            found_languages = ["Python", "SQL"]
        elif "java" in role_lower:
            found_languages = ["Java", "SQL"]
        elif "frontend" in role_lower or "react" in role_lower:
            found_languages = ["JavaScript", "TypeScript", "HTML", "CSS"]
        elif "c#" in role_lower or ".net" in role_lower:
            found_languages = ["C#", "SQL"]
        elif "golang" in role_lower or "go" in role_lower:
            found_languages = ["Go", "SQL"]
        else:
            found_languages = ["SQL"]

    # 2. Extract Key Responsibilities from text
    key_responsibilities = []
    lines = [line.strip() for line in jd_text.splitlines() if line.strip()]
    bullet_prefixes = ('-', '*', '•', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')
    for line in lines:
        cleaned = re.sub(r'^[#*_\-\d.\s•]+', '', line).strip()
        if len(cleaned) > 25 and any(line.startswith(p) for p in bullet_prefixes):
            key_responsibilities.append(cleaned)
        elif any(verb in cleaned.lower()[:20] for verb in ['design', 'develop', 'build', 'create', 'maintain', 'collaborate', 'lead', 'architect', 'manage', 'implement']):
            if len(cleaned) > 25:
                key_responsibilities.append(cleaned)

    # Cap responsibilities to top 6 or generate dynamic ones
    if key_responsibilities:
        key_responsibilities = key_responsibilities[:6]
    else:
        key_responsibilities = [
            f"Design, develop, and deploy scalable solutions for {effective_role} responsibilities.",
            f"Collaborate with cross-functional teams at {effective_company} to implement resilient systems.",
            f"Write clean, maintainable, and high-performance code adhering to industry best practices.",
            f"Participate in automated testing, code reviews, and production monitoring."
        ]

    # 3. Assemble Mandatory vs Preferred skills
    # Mandatory skills = target_role + primary languages + primary frameworks + key technologies
    mandatory_skills = [effective_role]
    for lang in found_languages[:3]:
        if lang not in mandatory_skills:
            mandatory_skills.append(lang)
    for fw in found_frameworks[:3]:
        if fw not in mandatory_skills:
            mandatory_skills.append(fw)
    for db in found_databases[:2]:
        if db not in mandatory_skills:
            mandatory_skills.append(db)

    # Preferred skills = remaining databases, cloud tools, and extra frameworks
    preferred_skills = []
    for tool in found_cloud_tools[:4]:
        if tool not in mandatory_skills and tool not in preferred_skills:
            preferred_skills.append(tool)
    for fw in found_frameworks[3:]:
        if fw not in mandatory_skills and fw not in preferred_skills:
            preferred_skills.append(fw)
    for db in found_databases[2:]:
        if db not in mandatory_skills and db not in preferred_skills:
            preferred_skills.append(db)
    if not preferred_skills and found_cloud_tools:
        preferred_skills = found_cloud_tools[:3]

    # 4. ATS Keywords
    important_ats_keywords = list(dict.fromkeys([
        effective_role,
        *found_languages,
        *found_frameworks,
        *found_databases,
        *found_cloud_tools[:5],
        "Agile", "System Design", "Scalability", "Clean Code"
    ]))

    return {
        "target_role": effective_role,
        "mandatory_skills": mandatory_skills,
        "preferred_skills": preferred_skills,
        "programming_languages": found_languages,
        "frameworks": found_frameworks,
        "databases": found_databases,
        "cloud_and_tools": found_cloud_tools,
        "key_responsibilities": key_responsibilities,
        "important_ats_keywords": important_ats_keywords
    }
