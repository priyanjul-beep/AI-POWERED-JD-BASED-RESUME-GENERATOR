from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ChangeDetail(BaseModel):
    section: str = Field(description="Section changed: Technical Skills, Work Experience, Projects, Professional Summary")
    change_type: str = Field(description="ADDED, MODIFIED, or REMOVED")
    original_content: str = Field(default="", description="Original text or bullet point before optimization")
    updated_content: str = Field(description="Updated text or bullet point after optimization")
    reason: str = Field(description="Why this change was made to match the JD")
    supporting_evidence: str = Field(default="", description="Evidence from profile or reference resume supporting this change")

class ResumeHeader(BaseModel):
    full_name: str
    headline: str
    email: str
    phone: str
    location: str
    linkedin_url: Optional[str] = ""
    github_url: Optional[str] = ""
    portfolio_url: Optional[str] = ""

class ResumeSkills(BaseModel):
    languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    cloud_and_devops: List[str] = Field(default_factory=list)
    developer_tools: List[str] = Field(default_factory=list)
    other: Optional[List[str]] = Field(default_factory=list)

class WorkExperienceItem(BaseModel):
    title: str
    company: str
    location: Optional[str] = ""
    start_date: str
    end_date: str
    is_current: bool = False
    technologies: List[str] = Field(default_factory=list)
    bullet_points: List[str] = Field(default_factory=list)

class ProjectItem(BaseModel):
    title: str
    role: Optional[str] = ""
    url: Optional[str] = ""
    technologies: List[str] = Field(default_factory=list)
    description: str = ""
    highlights: List[str] = Field(default_factory=list)

class EducationItem(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    grade: Optional[str] = ""
    honors: Optional[str] = ""

class CertificationItem(BaseModel):
    name: str
    issuing_organization: str
    issue_date: Optional[str] = ""
    credential_id: Optional[str] = ""

class StructuredResumeSchema(BaseModel):
    header: ResumeHeader
    summary: str
    skills: ResumeSkills
    work_experience: List[WorkExperienceItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    certifications: List[CertificationItem] = Field(default_factory=list)
    changes_applied: List[ChangeDetail] = Field(default_factory=list)
    evidence_gaps: List[str] = Field(default_factory=list, description="JD requirements without verified supporting evidence")

class JDAnalysisSchema(BaseModel):
    target_role: str
    mandatory_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    cloud_and_tools: List[str] = Field(default_factory=list)
    key_responsibilities: List[str] = Field(default_factory=list)
    important_ats_keywords: List[str] = Field(default_factory=list)
