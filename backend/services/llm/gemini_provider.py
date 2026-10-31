import json
import logging
import re
import time
from typing import Any, Dict, Optional, Type
from django.conf import settings
from pydantic import BaseModel, ValidationError

from .base import BaseLLMProvider, LLMProviderError, LLMRateLimitError, LLMAuthenticationError

logger = logging.getLogger(__name__)

class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini implementation of BaseLLMProvider.
    Uses official google.generativeai SDK with structured JSON output,
    exponential backoff retry handling, and schema validation.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        max_retries: Optional[int] = None,
        timeout: Optional[int] = None
    ):
        self.api_key = api_key or getattr(settings, 'GEMINI_API_KEY', '')
        raw_model = model_name or getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash')
        deprecated_map = {
            'gemini-1.5-flash': 'gemini-2.5-flash',
            'models/gemini-1.5-flash': 'gemini-2.5-flash',
            'gemini-1.5-pro': 'gemini-2.5-pro',
            'models/gemini-1.5-pro': 'gemini-2.5-pro',
            'gemini-1.0-pro': 'gemini-2.5-flash',
        }
        self.model_name = deprecated_map.get(raw_model, raw_model)
        self.max_retries = max_retries or getattr(settings, 'GEMINI_MAX_RETRIES', 3)
        self.timeout = timeout or getattr(settings, 'GEMINI_TIMEOUT_SECONDS', 60)
        self._client_initialized = False

    @property
    def provider_name(self) -> str:
        return 'gemini'

    def _init_client(self):
        if self._client_initialized:
            return

        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not configured in backend settings or .env.")

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client_initialized = True
        except Exception as e:
            raise LLMProviderError(f"Failed to configure Gemini SDK: {str(e)}")

    def _clean_json_text(self, text: str) -> str:
        """Strip markdown fences (```json ... ```) or whitespace."""
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
            text = re.sub(r"```$", "", text, flags=re.MULTILINE)
        return text.strip()

    def generate_structured(
        self,
        prompt: str,
        system_instruction: str = "",
        schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        Calls Gemini with structured JSON output enforced, retries on transient errors,
        and parses into a dictionary (validated by Pydantic schema if provided).
        """
        if not self.api_key:
            # Fallback mock mode if no API key is supplied yet, so local tests and UI work without crashing
            logger.warning("GEMINI_API_KEY not configured. Generating fallback mock response.")
            return self._generate_fallback_mock(prompt, schema)

        self._init_client()
        import google.generativeai as genai

        generation_config = {
            "temperature": temperature,
            "response_mime_type": "application/json",
        }

        # If schema is provided, pass schema declaration if supported or enforce via prompt
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_instruction or None,
            generation_config=generation_config
        )

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Invoking Gemini model '{self.model_name}' (attempt {attempt}/{self.max_retries})")
                response = model.generate_content(prompt)
                
                if not response or not response.text:
                    raise LLMProviderError("Empty response received from Gemini.")

                cleaned_text = self._clean_json_text(response.text)
                try:
                    data = json.loads(cleaned_text)
                except json.JSONDecodeError as jde:
                    logger.error(f"Failed to parse Gemini JSON output: {cleaned_text}")
                    raise LLMProviderError(f"Malformed JSON returned by Gemini: {str(jde)}")

                # Validate with Pydantic if provided
                if schema:
                    try:
                        validated_obj = schema.model_validate(data)
                        return validated_obj.model_dump()
                    except ValidationError as ve:
                        logger.error(f"Schema validation failed on Gemini output: {ve.errors()}")
                        # Still return data if it has standard fields
                        return data

                return data

            except Exception as e:
                err_str = str(e).lower()
                last_error = e
                if ('not found' in err_str or '404' in err_str) and self.model_name != 'gemini-2.5-flash':
                    logger.warning(f"Gemini model '{self.model_name}' not found or not supported. Falling back to 'gemini-2.5-flash'.")
                    self.model_name = 'gemini-2.5-flash'
                    model = genai.GenerativeModel(
                        model_name=self.model_name,
                        system_instruction=system_instruction or None,
                        generation_config=generation_config
                    )
                    continue
                elif 'quota' in err_str or 'rate' in err_str or '429' in err_str or 'exhausted' in err_str:
                    sleep_time = (2 ** attempt) + 1
                    logger.warning(f"Gemini rate limit hit. Sleeping {sleep_time}s before retry...")
                    time.sleep(sleep_time)
                elif 'auth' in err_str or 'api_key' in err_str or 'permission' in err_str:
                    raise LLMAuthenticationError(f"Gemini API authentication failed: {str(e)}")
                else:
                    sleep_time = attempt * 2
                    logger.warning(f"Gemini transient error on attempt {attempt}: {str(e)}. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)

        raise LLMProviderError(f"Failed to generate structured response after {self.max_retries} attempts: {str(last_error)}")

    def generate_text(
        self,
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.3
    ) -> str:
        if not self.api_key:
            return "Note: Gemini API Key not set. This is a local development placeholder text."

        self._init_client()
        import google.generativeai as genai

        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_instruction or None,
            generation_config={"temperature": temperature}
        )

        for attempt in range(1, self.max_retries + 1):
            try:
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                time.sleep(attempt * 2)

        return ""

    def _generate_fallback_mock(self, prompt: str, schema: Optional[Type[BaseModel]]) -> Dict[str, Any]:
        """
        Graceful local mock when GEMINI_API_KEY is not configured in .env.
        Allows immediate testing of the entire end-to-end workflow (UI, DB, review, approval, PDF).
        """
        # Determine intent from prompt
        if "analyze_jd" in prompt.lower() or "mandatory_skills" in prompt.lower():
            return {
                "target_role": "Backend / Java Developer",
                "mandatory_skills": ["Java", "Spring Boot", "REST APIs", "SQL", "Microservices"],
                "preferred_skills": ["Docker", "Kubernetes", "AWS", "Kafka", "CI/CD"],
                "programming_languages": ["Java", "SQL", "Python"],
                "frameworks": ["Spring Boot", "Spring MVC", "Hibernate"],
                "databases": ["PostgreSQL", "MySQL"],
                "cloud_and_tools": ["Docker", "Git", "Maven"],
                "key_responsibilities": [
                    "Design, develop, and maintain high-throughput backend microservices using Java and Spring Boot.",
                    "Build and optimize robust RESTful APIs with database transaction integrity.",
                    "Participate in agile code reviews, automated unit testing, and production deployment."
                ],
                "important_ats_keywords": ["Java 17", "Spring Boot", "RESTful Web Services", "Microservices Architecture", "JUnit", "Relational Database", "Scalability", "Clean Architecture"]
            }

        # Default Resume Generation mock
        return {
            "header": {
                "full_name": "Priyanjul Sonkar",
                "headline": "Backend Java Engineer | Spring Boot & Scalable Microservices",
                "email": "priyanjul@example.com",
                "phone": "+1 (555) 234-5678",
                "location": "New York, NY",
                "linkedin_url": "https://linkedin.com/in/priyanjul",
                "github_url": "https://github.com/priyanjul"
            },
            "summary": "Results-driven Software Engineer with extensive experience designing resilient backend systems, RESTful microservices, and database pipelines. Proven track record of architecting high-performance Java and Spring Boot services, optimizing relational schemas, and applying clean design patterns to deliver scalable enterprise solutions aligned with mission-critical requirements.",
            "skills": {
                "languages": ["Java (8/11/17)", "SQL", "JavaScript/TypeScript", "Python"],
                "frameworks": ["Spring Boot", "Spring MVC", "Spring Data JPA", "Hibernate", "Node.js/Express"],
                "databases": ["PostgreSQL", "MySQL", "MongoDB", "Redis"],
                "cloud_and_devops": ["Docker", "AWS (EC2, S3)", "CI/CD Pipelines", "Git", "Maven", "Gradle"],
                "developer_tools": ["IntelliJ IDEA", "Postman", "JUnit", "Mockito", "JIRA"]
            },
            "work_experience": [
                {
                    "title": "Backend Software Engineer",
                    "company": "Enterprise Tech Solutions",
                    "location": "Remote",
                    "start_date": "Jan 2023",
                    "end_date": "Present",
                    "is_current": True,
                    "technologies": ["Java 17", "Spring Boot", "PostgreSQL", "Docker", "REST APIs"],
                    "bullet_points": [
                        "Architected and deployed 8+ production microservices using Spring Boot and Java 17, processing over 1.2M daily transactions with sub-80ms p95 latency.",
                        "Engineered secure RESTful endpoints adhering to OpenAPI specifications, integrating OAuth2 token authentication and role-based access control.",
                        "Refactored relational database queries in PostgreSQL, eliminating N+1 query bottlenecks and improving data retrieval throughput by 42%.",
                        "Authored comprehensive unit and integration test suites using JUnit 5 and Mockito, raising code coverage from 64% to 91%."
                    ]
                },
                {
                    "title": "Software Development Intern",
                    "company": "Apex Cloud Systems",
                    "location": "San Francisco, CA",
                    "start_date": "Jun 2022",
                    "end_date": "Dec 2022",
                    "is_current": False,
                    "technologies": ["Java", "Spring MVC", "MySQL", "REST APIs", "Git"],
                    "bullet_points": [
                        "Collaborated in an agile scrum team to develop automated payment reconciliation endpoints using Java and Spring MVC.",
                        "Integrated third-party banking webhooks and structured transaction persistence with ACID compliance in MySQL.",
                        "Containerized backend micro-services with Docker to standardize local and staging environment deployments."
                    ]
                }
            ],
            "projects": [
                {
                    "title": "Distributed Financial Ledger Microservice",
                    "role": "Lead Backend Developer",
                    "url": "https://github.com/priyanjul/ledger-service",
                    "technologies": ["Java 17", "Spring Boot", "PostgreSQL", "Redis", "Docker"],
                    "description": "High-throughput double-entry accounting ledger system designed for concurrent financial transactions.",
                    "highlights": [
                        "Implemented pessimistic locking and Redis distributed caching, preventing double-spend anomalies across concurrent worker instances.",
                        "Designed comprehensive REST API suite with automated Swagger/OpenAPI documentation and Prometheus metrics monitoring."
                    ]
                },
                {
                    "title": "Enterprise E-Commerce API Gateway",
                    "role": "Backend Engineer",
                    "url": "https://github.com/priyanjul/ecommerce-gateway",
                    "technologies": ["Java", "Spring Cloud Gateway", "PostgreSQL", "JWT"],
                    "description": "API Gateway managing traffic routing, rate limiting, and token validation for 5 downstream backend services.",
                    "highlights": [
                        "Built custom rate-limiting filters using token bucket algorithm to mitigate DDoS traffic spikes by 99.8%.",
                        "Structured resilient database schema migrations using Flyway and PostgreSQL."
                    ]
                }
            ],
            "education": [
                {
                    "institution": "State University of Technology",
                    "degree": "Bachelor of Science in Computer Science",
                    "field_of_study": "Software Engineering & Distributed Systems",
                    "start_date": "2019",
                    "end_date": "2023",
                    "grade": "3.8 / 4.0 GPA",
                    "honors": "Dean's Honor List (4 Semesters)"
                }
            ],
            "certifications": [
                {
                    "name": "Oracle Certified Professional: Java SE Developer",
                    "issuing_organization": "Oracle",
                    "issue_date": "2023",
                    "credential_id": "OCP-JAVA-88219"
                }
            ],
            "changes_applied": [
                {
                    "section": "Technical Skills",
                    "change_type": "ADDED",
                    "original_content": "React, Node.js, Express, MongoDB",
                    "updated_content": "Java 17, Spring Boot, Spring MVC, PostgreSQL, REST APIs, Microservices",
                    "reason": "Prioritized mandatory Java and Spring Boot technical skills specified in the target Job Description, supported by candidate's backend engineering background and verified profile technologies.",
                    "supporting_evidence": "Candidate career profile lists completed backend engineering experience and core relational database systems."
                },
                {
                    "section": "Work Experience",
                    "change_type": "MODIFIED",
                    "original_content": "Built full-stack web applications using MERN stack.",
                    "updated_content": "Architected and deployed 8+ production microservices using Spring Boot and Java 17, processing over 1.2M daily transactions with sub-80ms p95 latency.",
                    "reason": "Emphasized transferable distributed backend systems, REST API scalability, and transaction management aligned with JD requirements without fabricating unverified companies.",
                    "supporting_evidence": "Verifiable backend development internship and enterprise system responsibilities."
                },
                {
                    "section": "Projects",
                    "change_type": "ADDED",
                    "original_content": "Frontend React portfolio website.",
                    "updated_content": "Distributed Financial Ledger Microservice (Java 17, Spring Boot, PostgreSQL, Redis)",
                    "reason": "Surfaced role-specific backend project from complete career profile demonstrating hands-on Java 17, Spring Boot, and database concurrency mastery.",
                    "supporting_evidence": "Detailed project entry in candidate complete career profile database."
                }
            ],
            "evidence_gaps": []
        }
