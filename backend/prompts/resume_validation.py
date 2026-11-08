from typing import List, Optional, Dict, Any, Union
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
    github_url: Optional[str] = ""
    demo_url: Optional[str] = ""
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

class RequirementMappingItem(BaseModel):
    requirement_name: str
    category: str = "General"
    classification: str = "MANDATORY"
    candidate_evidence: str = ""
    evidence_source: str = ""
    status: str = "VERIFIED"  # VERIFIED, TRANSFERABLE, USER_CONFIRMATION_REQUIRED, UNSUPPORTED, PROPOSED
    recommended_action: str = ""

class ProposedContentItem(BaseModel):
    target_section: str = "Work Experience"
    proposed_text: str
    targeted_jd_requirement: str
    reason: str
    requires_user_confirmation: bool = True

class EvidenceGapDetail(BaseModel):
    requirement: str
    reason_missing: str = "Evidence not found in candidate profile or reference resume."
    transferable_evidence: Optional[str] = ""
    suggested_user_input: Optional[str] = ""
    industry_pattern: Optional[str] = ""
    requires_confirmation: bool = True

class StructuredResumeSchema(BaseModel):
    header: ResumeHeader
    summary: str
    skills: ResumeSkills
    work_experience: List[WorkExperienceItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    certifications: List[CertificationItem] = Field(default_factory=list)
    achievements_and_coding: List[str] = Field(default_factory=list, description="Combined Achievements, Hackathons, and Competitive Coding Profiles")
    changes_applied: List[ChangeDetail] = Field(default_factory=list)
    evidence_gaps: List[Union[EvidenceGapDetail, str]] = Field(default_factory=list, description="JD requirements without verified supporting evidence")
    requirement_mappings: Optional[List[RequirementMappingItem]] = Field(default_factory=list)
    proposed_content: Optional[List[ProposedContentItem]] = Field(default_factory=list)

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
