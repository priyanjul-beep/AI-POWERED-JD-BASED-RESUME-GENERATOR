export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  date_joined: string;
}

export interface AuthResponse {
  user: User;
  access: string;
  refresh: string;
  message?: string;
}

export interface CareerExperience {
  id?: number;
  experience_type: 'PROFESSIONAL' | 'INTERNSHIP' | 'APPRENTICE';
  title: string;
  company: string;
  location?: string;
  start_date: string;
  end_date?: string;
  is_current: boolean;
  technologies: string[];
  bullet_points: string[];
}

export interface CareerProject {
  id?: number;
  title: string;
  role?: string;
  url?: string;
  technologies: string[];
  description: string;
  highlights: string[];
}

export interface CareerSkill {
  id?: number;
  category: 'LANGUAGES' | 'FRAMEWORKS' | 'DATABASES' | 'CLOUD' | 'TOOLS' | 'OTHER';
  name: string;
  proficiency_level: string;
  years_used?: number;
}

export interface CareerEducation {
  id?: number;
  institution: string;
  degree: string;
  field_of_study?: string;
  start_date?: string;
  end_date?: string;
  grade?: string;
  honors?: string;
}

export interface CareerCertification {
  id?: number;
  name: string;
  issuing_organization: string;
  issue_date?: string;
  credential_id?: string;
  credential_url?: string;
}

export interface CareerProfile {
  id: number;
  full_name: string;
  headline: string;
  email: string;
  phone: string;
  location: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  summary: string;
  experiences: CareerExperience[];
  projects: CareerProject[];
  skills: CareerSkill[];
  education: CareerEducation[];
  certifications: CareerCertification[];
}

export interface ChangeDetail {
  section: string;
  change_type: 'ADDED' | 'MODIFIED' | 'REMOVED';
  original_content: string;
  updated_content: string;
  reason: string;
  supporting_evidence: string;
}

export interface ResumeSkills {
  languages: string[];
  frameworks: string[];
  databases: string[];
  cloud_and_devops: string[];
  developer_tools: string[];
}

export interface ResumeWorkExperience {
  title: string;
  company: string;
  location?: string;
  start_date: string;
  end_date: string;
  is_current?: boolean;
  technologies: string[];
  bullet_points: string[];
}

export interface ResumeProject {
  title: string;
  role?: string;
  url?: string;
  technologies: string[];
  description: string;
  highlights: string[];
}

export interface ResumeEducation {
  institution: string;
  degree: string;
  field_of_study?: string;
  start_date?: string;
  end_date?: string;
  grade?: string;
  honors?: string;
}

export interface ResumeCertification {
  name: string;
  issuing_organization: string;
  issue_date?: string;
  credential_id?: string;
}

export interface StructuredResumeData {
  header: {
    full_name: string;
    headline: string;
    email: string;
    phone: string;
    location: string;
    linkedin_url?: string;
    github_url?: string;
    portfolio_url?: string;
  };
  summary: string;
  skills: ResumeSkills;
  work_experience: ResumeWorkExperience[];
  projects: ResumeProject[];
  education: ResumeEducation[];
  certifications: ResumeCertification[];
  changes_applied: ChangeDetail[];
  evidence_gaps: string[];
}

export interface ResumeMatchReport {
  id?: number;
  overall_evidence_score: number;
  keyword_coverage_score: number;
  mandatory_skills_score: number;
  preferred_skills_score: number;
  experience_relevance_score: number;
  matched_mandatory_skills: string[];
  missing_mandatory_skills: string[];
  matched_preferred_skills: string[];
  missing_preferred_skills: string[];
  matched_keywords: string[];
  missing_keywords: string[];
  evidence_gaps: string[];
}

export interface ResumeVersion {
  id: number;
  version_number: number;
  structured_resume_data: StructuredResumeData;
  change_analysis: ChangeDetail[];
  user_instructions?: string;
  created_at: string;
  match_report?: ResumeMatchReport;
}

export interface ResumeGeneration {
  id: number;
  target_role: string;
  target_company: string;
  experience_level: string;
  additional_experience_details?: string;
  status: 'DRAFT' | 'REVISING' | 'APPROVED' | 'CANCELLED';
  current_version_number: number;
  created_at: string;
  updated_at: string;
  versions: ResumeVersion[];
  current_version?: ResumeVersion;
}

export interface FinalizedResumeHistory {
  id: number;
  generation: number;
  target_role: string;
  target_company: string;
  experience_level: string;
  final_resume_data: StructuredResumeData;
  page_format: 'ONE_PAGE' | 'TWO_PAGE';
  filename: string;
  overall_evidence_score: number;
  keyword_coverage_score: number;
  version_number: number;
  pdf_url?: string;
  match_report?: ResumeMatchReport;
  created_at: string;
}

export interface DashboardStats {
  total_resumes_generated: number;
  average_jd_match_score: number;
  recent_resumes: FinalizedResumeHistory[];
}
