"""
Dynamic industry-standard responsibility patterns and professional bullet structures.
Provides role-agnostic templates following the formula:
Action Verb + Technical Implementation + Technology + Purpose/Outcome.
"""
from typing import Dict, Any, List

# Core industry responsibility patterns by domain
INDUSTRY_RESPONSIBILITY_DOMAINS = {
    "backend": [
        "Architecting and developing modular RESTful APIs and backend services using {primary_tech} to support core business functionality.",
        "Designing relational database schemas, indexing strategies, and writing optimized SQL queries in {database} to maintain data integrity.",
        "Implementing unit testing, automated integration tests, and test-driven validation using {testing_framework} to maintain high code reliability.",
        "Participating actively in Software Development Lifecycle (SDLC) activities including sprint planning, code reviews, and Git-based version control.",
        "Developing scalable backend components and asynchronous processing pipelines using {cloud_or_tool} to handle concurrent traffic.",
        "Configuring CI/CD automation and containerized application deployments with Docker and cloud services."
    ],
    "frontend": [
        "Developing responsive, accessible, and high-performance user interfaces using {primary_tech} adhering to modern component architectures.",
        "Integrating client-side state management and connecting RESTful/GraphQL endpoints for asynchronous data synchronization.",
        "Writing unit and component tests using {testing_framework} to ensure cross-browser compatibility and UI consistency.",
        "Collaborating in Agile/SDLC workflows, conducting peer code reviews, and optimizing client-side bundle size and rendering performance."
    ],
    "fullstack": [
        "Developing end-to-end web applications combining {primary_tech} and modern frontend components with robust backend services.",
        "Designing relational schemas in {database} and engineering secure RESTful API contracts with authentication and validation.",
        "Executing full Software Development Lifecycle (SDLC) practices including automated testing ({testing_framework}), continuous integration, and version control.",
        "Optimizing application latency, managing database migrations, and containerizing microservices using {cloud_or_tool}."
    ],
    "ai_ml": [
        "Developing and evaluating machine learning and deep learning pipelines using {primary_tech} to deliver predictive capabilities.",
        "Designing data ingestion, feature engineering, and preprocessing workflows in {database} and scientific computing libraries.",
        "Integrating trained models into production RESTful microservices with automated inference validation and monitoring.",
        "Conducting reproducible experimentation, versioning datasets with Git/DVC, and participating in end-to-end SDLC workflows."
    ]
}

def detect_domain(target_role: str) -> str:
    role_lower = target_role.lower()
    if any(k in role_lower for k in ["data", "machine learning", "ai", "ml", "deep learning", "nlp"]):
        return "ai_ml"
    elif any(k in role_lower for k in ["frontend", "ui", "react", "angular", "vue", "web developer"]):
        return "frontend"
    elif any(k in role_lower for k in ["full stack", "fullstack", "full-stack"]):
        return "fullstack"
    return "backend"

def get_role_industry_patterns(
    target_role: str,
    experience_level: str,
    primary_tech: str = "Java / Spring Boot",
    database: str = "PostgreSQL",
    testing_framework: str = "JUnit / automated test suites",
    cloud_or_tool: str = "Docker & CI/CD"
) -> List[str]:
    domain = detect_domain(target_role)
    templates = INDUSTRY_RESPONSIBILITY_DOMAINS.get(domain, INDUSTRY_RESPONSIBILITY_DOMAINS["backend"])
    
    formatted = []
    for tmpl in templates:
        formatted.append(tmpl.format(
            primary_tech=primary_tech,
            database=database,
            testing_framework=testing_framework,
            cloud_or_tool=cloud_or_tool
        ))
    return formatted
