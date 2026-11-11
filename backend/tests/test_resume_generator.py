import json
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from apps.profiles.models import CareerProfile, Experience, Project, Skill, Education, Certification
from apps.documents.models import JobDescription, ReferenceResume
from apps.generations.models import ResumeGeneration, ResumeVersion, GenerationStatus
from apps.history.models import FinalizedResumeHistory
from apps.pdf_engine.ats_generator import normalize_filename, generate_ats_pdf
from services.matching.score_calculator import calculate_jd_match_scores
from services.matching.requirement_mapper import build_requirement_evidence_mapping
from prompts.industry_patterns import get_role_industry_patterns
from services.diff.resume_differ import compute_structured_diff
from services.validation.structural_preserver import (
    enforce_structural_identity,
    validate_structural_identity,
    build_baseline_from_profile_and_resume
)

class ResumeGeneratorSystemTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='Password123!',
            first_name='Priyanjul',
            last_name='Sonkar'
        )
        self.client.force_authenticate(user=self.user)

        # Populate baseline Career Profile
        self.profile, _ = CareerProfile.objects.get_or_create(
            user=self.user,
            defaults={
                'full_name': 'Priyanjul Sonkar',
                'headline': 'Full Stack & Backend Developer',
                'email': 'testuser@example.com',
                'phone': '+1 (555) 123-4567',
                'location': 'New York, NY',
                'summary': 'Passionate engineer with experience in distributed systems and cloud services.'
            }
        )

        Experience.objects.create(
            profile=self.profile,
            experience_type=Experience.ExperienceType.INTERNSHIP,
            title='Software Engineering Intern',
            company='Tech Corp',
            location='San Francisco, CA',
            start_date='Jan 2023',
            end_date='Jun 2023',
            is_current=False,
            technologies=['Java', 'Spring Boot', 'REST APIs', 'PostgreSQL'],
            bullet_points=[
                'Developed RESTful endpoints using Java and Spring Boot for financial reporting.',
                'Optimized PostgreSQL queries reducing latency by 30%.'
            ]
        )

        Project.objects.create(
            profile=self.profile,
            title='Real-time Payment Gateway',
            role='Backend Lead',
            url='https://github.com/test/gateway',
            technologies=['Java', 'Spring Boot', 'PostgreSQL', 'Docker'],
            description='Microservices payment processor with distributed ACID transactions.',
            highlights=['Handled 5,000 requests per minute with 99.9% uptime.']
        )

        Skill.objects.create(
            profile=self.profile,
            category=Skill.SkillCategory.LANGUAGES,
            name='Java',
            proficiency_level='Advanced',
            years_used=2.0
        )
        Skill.objects.create(
            profile=self.profile,
            category=Skill.SkillCategory.FRAMEWORKS,
            name='Spring Boot',
            proficiency_level='Advanced',
            years_used=2.0
        )

    def test_normalize_filename(self):
        filename = normalize_filename(
            candidate_name="Priyanjul Sonkar",
            company_name="Mastercard Inc.",
            target_role="Java Developer",
            version_number=1
        )
        self.assertEqual(filename, "priyanjul_sonkar_mastercard_inc_java_developer_1.pdf")

    def test_pdf_generation_budget(self):
        sample_resume = {
            "header": {
                "full_name": "Priyanjul Sonkar",
                "headline": "Java Backend Engineer",
                "email": "priyanjul@example.com",
                "phone": "+1 555-0199",
                "location": "New York, NY"
            },
            "summary": "Experienced backend engineer specializing in Java and Spring Boot microservices.",
            "skills": {
                "languages": ["Java", "SQL"],
                "frameworks": ["Spring Boot", "Hibernate"],
                "databases": ["PostgreSQL"],
                "cloud_and_devops": ["Docker", "AWS"],
                "developer_tools": ["Git", "Maven"]
            },
            "work_experience": [
                {
                    "title": "Backend Developer",
                    "company": "Tech Corp",
                    "location": "Remote",
                    "start_date": "2023",
                    "end_date": "Present",
                    "technologies": ["Java", "Spring Boot"],
                    "bullet_points": ["Engineered high-throughput REST APIs."]
                }
            ],
            "projects": [
                {
                    "title": "Cloud Ledger",
                    "role": "Developer",
                    "technologies": ["Java", "Spring Boot"],
                    "description": "Ledger service",
                    "highlights": ["Zero transaction drop rate."]
                }
            ],
            "education": [
                {
                    "institution": "University",
                    "degree": "B.S. in CS",
                    "grade": "3.8 GPA"
                }
            ]
        }
        pdf_bytes = generate_ats_pdf(sample_resume, page_format="ONE_PAGE")
        self.assertTrue(len(pdf_bytes) > 1000)
        self.assertTrue(pdf_bytes.startswith(b'%PDF-'))

    def test_score_calculator(self):
        jd_analysis = {
            "target_role": "Java Developer",
            "mandatory_skills": ["Java", "Spring Boot", "SQL"],
            "preferred_skills": ["Docker", "Kubernetes"],
            "important_ats_keywords": ["Microservices", "REST APIs", "Java 17"]
        }
        resume_data = {
            "header": {"headline": "Java Developer"},
            "summary": "Building REST APIs and Microservices in Java 17.",
            "skills": {
                "languages": ["Java", "SQL"],
                "frameworks": ["Spring Boot"]
            },
            "work_experience": [
                {
                    "title": "Java Developer",
                    "technologies": ["Java", "Spring Boot", "Docker"],
                    "bullet_points": ["Engineered REST APIs using Microservices architecture."]
                }
            ]
        }
        scores = calculate_jd_match_scores(jd_analysis, resume_data)
        self.assertGreater(scores['overall_evidence_score'], 70.0)
        self.assertIn("Java", scores['matched_mandatory_skills'])
        self.assertIn("Spring Boot", scores['matched_mandatory_skills'])

    def test_structured_diff(self):
        prev = {
            "summary": "Junior web developer with JavaScript skills.",
            "skills": {"languages": ["JavaScript"]}
        }
        updated = {
            "summary": "Backend Java engineer specializing in Spring Boot.",
            "skills": {"languages": ["Java", "JavaScript"]}
        }
        diffs = compute_structured_diff(prev, updated)
        self.assertTrue(len(diffs) > 0)
        change_types = [d['change_type'] for d in diffs]
        self.assertTrue('MODIFIED' in change_types or 'ADDED' in change_types)

    def test_complete_human_in_the_loop_workflow(self):
        # 1. Analyze and generate v1
        response = self.client.post('/api/resume-generations/analyze/', {
            'job_description_text': 'Looking for a Java Developer with Spring Boot, REST APIs, and SQL experience.',
            'target_role': 'Java Developer',
            'target_company': 'Mastercard',
            'experience_level': 'INTERNSHIP',
            'additional_experience_details': 'Six months backend internship working with Spring Boot.'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        gen_data = response.data
        gen_id = gen_data['id']
        self.assertEqual(gen_data['current_version_number'], 1)
        self.assertEqual(gen_data['status'], GenerationStatus.DRAFT)

        # 2. User clicks NO with specific revision comment
        rev_response = self.client.post(f'/api/resume-generations/{gen_id}/revise/', {
            'user_comment': 'Please emphasize my SQL and transaction optimization in the work experience bullets.'
        }, format='json')

        self.assertEqual(rev_response.status_code, status.HTTP_200_OK)
        rev_data = rev_response.data
        self.assertEqual(rev_data['current_version_number'], 2)
        self.assertEqual(len(rev_data['versions']), 2)

        # 3. User clicks YES to approve
        approve_response = self.client.post(f'/api/resume-generations/{gen_id}/approve/', {
            'user_comment': '',
            'page_format': 'ONE_PAGE',
            'custom_filename': 'priyanjul_mastercard_java_dev.pdf'
        }, format='json')

        self.assertEqual(approve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(approve_response.data['filename'], 'priyanjul_mastercard_java_dev.pdf')

        # 4. Verify History Entry Created
        history_response = self.client.get('/api/resume-history/')
        self.assertEqual(history_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(history_response.data), 1)

        # 5. Check PDF download
        pdf_response = self.client.get(f'/api/resume-generations/{gen_id}/download/')
        self.assertEqual(pdf_response.status_code, status.HTTP_200_OK)
        self.assertEqual(pdf_response['Content-Type'], 'application/pdf')

    def test_user_data_isolation(self):
        # Create second user
        other_user = User.objects.create_user(
            username='intruder',
            email='intruder@example.com',
            password='Password123!'
        )

        # Generate resume as primary user
        gen_response = self.client.post('/api/resume-generations/analyze/', {
            'job_description_text': 'Java Developer needed with Spring Boot and SQL.',
            'target_role': 'Java Developer',
            'experience_level': '1_YEAR'
        }, format='json')
        gen_id = gen_response.data['id']

        # Switch client authentication to other user
        other_client = APIClient()
        other_client.force_authenticate(user=other_user)

        # Other user cannot access User A's generation
        detail_res = other_client.get(f'/api/resume-generations/{gen_id}/')
        self.assertEqual(detail_res.status_code, status.HTTP_404_NOT_FOUND)

        # Other user cannot revise User A's generation
        revise_res = other_client.post(f'/api/resume-generations/{gen_id}/revise/', {
            'user_comment': 'Unauthorized revision'
        }, format='json')
        self.assertEqual(revise_res.status_code, status.HTTP_404_NOT_FOUND)

        # Other user cannot approve User A's generation
        approve_res = other_client.post(f'/api/resume-generations/{gen_id}/approve/', {
            'page_format': 'ONE_PAGE'
        }, format='json')
        self.assertEqual(approve_res.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_workflow(self):
        gen_response = self.client.post('/api/resume-generations/analyze/', {
            'job_description_text': 'Looking for Python and Django backend developer.',
            'target_role': 'Python Developer',
            'experience_level': 'FRESHER'
        }, format='json')
        gen_id = gen_response.data['id']

        cancel_res = self.client.post(f'/api/resume-generations/{gen_id}/cancel/')
        self.assertEqual(cancel_res.status_code, status.HTTP_200_OK)
        self.assertEqual(cancel_res.data['status'], GenerationStatus.CANCELLED)

        # Verify that revising or approving a cancelled generation is rejected
        try_rev = self.client.post(f'/api/resume-generations/{gen_id}/revise/', {
            'user_comment': 'Should fail on cancelled session'
        }, format='json')
        self.assertEqual(try_rev.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify no finalized history entry was created
        history_entries = FinalizedResumeHistory.objects.filter(generation_id=gen_id)
        self.assertEqual(history_entries.count(), 0)

    def test_scenario_a_fresher_with_java_project(self):
        """Scenario A: Fresher applying for Java Developer role with verified Java project evidence."""
        # Fresher candidate has Java project in profile
        profile_data = {
            "experiences": [],
            "projects": [
                {
                    "title": "Java Spring Boot E-Commerce",
                    "technologies": ["Java", "Spring Boot", "MySQL", "REST APIs"],
                    "description": "Academic capstone e-commerce API service."
                }
            ],
            "skills": [{"name": "Java"}, {"name": "SQL"}]
        }
        jd_analysis = {
            "target_role": "Java Developer",
            "mandatory_skills": ["Java", "Spring Boot", "REST APIs", "Unit Testing"],
            "preferred_skills": ["Docker"],
            "important_ats_keywords": ["Microservices", "SDLC"]
        }
        mappings = build_requirement_evidence_mapping(
            jd_analysis=jd_analysis,
            career_profile_data=profile_data,
            reference_resume_text="",
            experience_level="FRESHER"
        )
        # Java must be VERIFIED from projects/skills
        java_map = next((m for m in mappings if m['requirement_name'] == 'Java'), None)
        self.assertIsNotNone(java_map)
        self.assertEqual(java_map['status'], 'VERIFIED')
        self.assertIn("Project", java_map['recommended_action'])

    def test_scenario_b_mern_developer_transferable_backend(self):
        """Scenario B: MERN developer applying for Java Developer role with transferable backend experience."""
        profile_data = {
            "experiences": [
                {
                    "title": "Full Stack Developer",
                    "company": "Node Tech",
                    "technologies": ["JavaScript", "Node.js", "Express", "MongoDB", "REST APIs"],
                    "bullet_points": ["Engineered RESTful APIs with token authentication.", "Collaborated in Agile SDLC sprints."]
                }
            ],
            "projects": [],
            "skills": [{"name": "JavaScript"}, {"name": "REST APIs"}, {"name": "Git"}]
        }
        jd_analysis = {
            "target_role": "Java Developer",
            "mandatory_skills": ["Java", "REST APIs", "Software Development Lifecycle"],
            "preferred_skills": ["PostgreSQL"],
            "important_ats_keywords": ["SDLC", "Agile"]
        }
        mappings = build_requirement_evidence_mapping(
            jd_analysis=jd_analysis,
            career_profile_data=profile_data,
            reference_resume_text="MERN Stack Developer with React and Node.js expertise.",
            experience_level="1_YEAR"
        )
        # REST APIs must be VERIFIED
        api_map = next((m for m in mappings if m['requirement_name'] == 'REST APIs'), None)
        self.assertIsNotNone(api_map)
        self.assertEqual(api_map['status'], 'VERIFIED')

        # SDLC must be VERIFIED or TRANSFERABLE from Agile/Git/experience
        sdlc_map = next((m for m in mappings if 'Lifecycle' in m['requirement_name'] or 'SDLC' in m['requirement_name']), None)
        self.assertIsNotNone(sdlc_map)
        self.assertIn(sdlc_map['status'], ['VERIFIED', 'TRANSFERABLE'])

        # Java has no commercial evidence; must be PROPOSED or UNSUPPORTED, NOT falsely VERIFIED
        java_map = next((m for m in mappings if m['requirement_name'] == 'Java'), None)
        self.assertIsNotNone(java_map)
        self.assertNotEqual(java_map['status'], 'VERIFIED')

    def test_scenario_c_java_internship_harvested_from_profile(self):
        """Scenario C: Candidate with actual Java internship experience missing from reference resume."""
        # Baseline profile in setUp has Java internship at Tech Corp
        # Send reference resume that only lists React / Node
        ref_text = "Frontend Developer. Skills: React, CSS, HTML. Built responsive web pages."
        response = self.client.post('/api/resume-generations/analyze/', {
            'job_description_text': 'Java Backend Developer needed with Spring Boot, REST APIs, and PostgreSQL.',
            'target_role': 'Java Developer',
            'target_company': 'Financial Enterprise',
            'experience_level': 'INTERNSHIP',
            'reference_resume_text': ref_text
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        resume_data = response.data['versions'][0]['structured_resume_data']
        # Must surface Java in technical skills from the master Career Profile
        skills = resume_data.get('skills', {})
        languages = skills.get('languages', [])
        frameworks = skills.get('frameworks', [])
        self.assertTrue(any('Java' in s for s in languages or frameworks))

    def test_scenario_d_ai_engineer_role(self):
        """Scenario D: Candidate applying for an AI Engineer role with relevant AI projects in master profile."""
        patterns = get_role_industry_patterns(
            target_role="AI Engineer",
            experience_level="1_YEAR",
            primary_tech="Python, PyTorch",
            database="Vector DBs & SQL"
        )
        self.assertTrue(len(patterns) > 0)
        # Verify AI-specific domain terminology is produced
        combined_patterns = " ".join(patterns).lower()
        self.assertTrue('machine learning' in combined_patterns or 'deep learning' in combined_patterns or 'pipeline' in combined_patterns)

    def test_scenario_e_mandatory_skills_no_evidence_unsupported(self):
        """Scenario E: Candidate applying for a role with mandatory skills for which no supporting evidence exists."""
        profile_data = {
            "experiences": [],
            "projects": [],
            "skills": [{"name": "HTML"}, {"name": "CSS"}]
        }
        jd_analysis = {
            "target_role": "Blockchain Developer",
            "mandatory_skills": ["Solidity", "Rust", "Smart Contracts"],
            "preferred_skills": ["EVM"],
            "important_ats_keywords": ["Cryptography"]
        }
        mappings = build_requirement_evidence_mapping(
            jd_analysis=jd_analysis,
            career_profile_data=profile_data,
            reference_resume_text="",
            experience_level="FRESHER"
        )
        for m in mappings:
            # None of these specialized skills should be marked VERIFIED
            self.assertNotEqual(m['status'], 'VERIFIED')

    def test_scenario_f_user_clicks_no_requests_revision(self):
        """Scenario F: User clicks NO and requests additional skills."""
        gen_res = self.client.post('/api/resume-generations/analyze/', {
            'job_description_text': 'Java Engineer with Spring Boot and PostgreSQL.',
            'target_role': 'Java Engineer',
            'experience_level': 'INTERNSHIP'
        }, format='json')
        gen_id = gen_res.data['id']

        rev_res = self.client.post(f'/api/resume-generations/{gen_id}/revise/', {
            'user_comment': 'Please emphasize my SQL performance tuning and unit testing experience.'
        }, format='json')
        self.assertEqual(rev_res.status_code, status.HTTP_200_OK)
        self.assertEqual(rev_res.data['current_version_number'], 2)
        self.assertEqual(rev_res.data['status'], GenerationStatus.REVISING)

    def test_scenario_g_user_clicks_yes_with_final_comment(self):
        """Scenario G: User clicks YES with a final comment."""
        gen_res = self.client.post('/api/resume-generations/analyze/', {
            'job_description_text': 'Java Engineer with Spring Boot.',
            'target_role': 'Java Engineer',
            'experience_level': 'INTERNSHIP'
        }, format='json')
        gen_id = gen_res.data['id']

        approve_res = self.client.post(f'/api/resume-generations/{gen_id}/approve/', {
            'user_comment': 'Approved! Highlight JUnit automated testing in summary.',
            'page_format': 'ONE_PAGE',
            'custom_filename': 'priyanjul_approved.pdf'
        }, format='json')
        self.assertEqual(approve_res.status_code, status.HTTP_200_OK)
        self.assertEqual(approve_res.data['filename'], 'priyanjul_approved.pdf')

        # Verify only a single finalized history record exists
        history_count = FinalizedResumeHistory.objects.filter(generation_id=gen_id).count()
        self.assertEqual(history_count, 1)

    def test_scenario_h_cancel_workflow(self):
        """Scenario H: User cancels the generation workflow."""
        gen_res = self.client.post('/api/resume-generations/analyze/', {
            'job_description_text': 'Python Flask Developer needed.',
            'target_role': 'Python Developer',
            'experience_level': 'FRESHER'
        }, format='json')
        gen_id = gen_res.data['id']

        cancel_res = self.client.post(f'/api/resume-generations/{gen_id}/cancel/')
        self.assertEqual(cancel_res.status_code, status.HTTP_200_OK)
        self.assertEqual(cancel_res.data['status'], GenerationStatus.CANCELLED)

        # Confirm that revising or approving a cancelled generation is rejected with 400
        bad_rev = self.client.post(f'/api/resume-generations/{gen_id}/revise/', {
            'user_comment': 'Try revise cancelled'
        }, format='json')
        self.assertEqual(bad_rev.status_code, status.HTTP_400_BAD_REQUEST)

        bad_app = self.client.post(f'/api/resume-generations/{gen_id}/approve/', {
            'page_format': 'ONE_PAGE'
        }, format='json')
        self.assertEqual(bad_app.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_requested_exact_structural_preservation(self):
        """
        User Test Case:
        Original resume:
        - Existing company: Company A.
        - Existing designation: Software Development Intern.
        - Existing project: E-Commerce Platform.
        - Existing degree: Bachelor of Technology.
        - Existing certification: Original Certification.
        JD: Java Backend Developer.
        """
        # Create fresh candidate profile matching user test specification
        user_spec = User.objects.create_user(
            username='specuser',
            email='specuser@example.com',
            password='Password123!',
            first_name='Candidate',
            last_name='Spec'
        )
        self.client.force_authenticate(user=user_spec)

        spec_profile = CareerProfile.objects.create(
            user=user_spec,
            full_name='Candidate Spec',
            headline='Software Development Intern',
            email='specuser@example.com',
            phone='+1 555-9876',
            location='Austin, TX',
            summary='Enthusiastic junior developer with foundational skills in web development and databases.'
        )

        Experience.objects.create(
            profile=spec_profile,
            experience_type=Experience.ExperienceType.INTERNSHIP,
            title='Software Development Intern',
            company='Company A',
            location='Austin, TX',
            start_date='Jan 2023',
            end_date='Jun 2023',
            is_current=False,
            technologies=['Java', 'SQL', 'Git'],
            bullet_points=['Assisted senior engineers with bug fixes and database maintenance.']
        )

        Project.objects.create(
            profile=spec_profile,
            title='E-Commerce Platform',
            role='Developer',
            url='https://github.com/spec/ecommerce',
            technologies=['Java', 'MySQL'],
            description='Online shopping cart application with order management.',
            highlights=['Implemented user authentication and cart storage.']
        )

        Education.objects.create(
            profile=spec_profile,
            institution='State University of Science',
            degree='Bachelor of Technology',
            field_of_study='Computer Science and Engineering',
            start_date='2019',
            end_date='2023',
            grade='First Class'
        )

        Certification.objects.create(
            profile=spec_profile,
            name='Original Certification',
            issuing_organization='Global Tech Board',
            issue_date='2022'
        )

        Skill.objects.create(
            profile=spec_profile,
            category=Skill.SkillCategory.LANGUAGES,
            name='Java',
            proficiency_level='Intermediate',
            years_used=1.5
        )

        # Trigger generation for target role: Java Backend Developer
        gen_res = self.client.post('/api/resume-generations/analyze/', {
            'job_description_text': 'Java Backend Developer needed with Spring Boot, Hibernate, REST APIs, and SQL.',
            'target_role': 'Java Backend Developer',
            'target_company': 'Target Corp',
            'experience_level': 'INTERNSHIP'
        }, format='json')

        self.assertEqual(gen_res.status_code, status.HTTP_201_CREATED)
        gen_id = gen_res.data['id']
        current_v = gen_res.data['current_version']
        resume = current_v['structured_resume_data']

        # 1. Company A must remain Company A
        self.assertEqual(resume['work_experience'][0]['company'], 'Company A')

        # 2. Software Development Intern must remain Software Development Intern (NOT upgraded)
        self.assertEqual(resume['work_experience'][0]['title'], 'Software Development Intern')

        # 3. E-Commerce Platform must retain its original project name
        self.assertEqual(resume['projects'][0]['title'], 'E-Commerce Platform')

        # 4. Degree must remain unchanged
        self.assertEqual(resume['education'][0]['degree'], 'Bachelor of Technology')
        self.assertEqual(resume['education'][0]['institution'], 'State University of Science')

        # 5. Certification must remain unchanged
        self.assertEqual(resume['certifications'][0]['name'], 'Original Certification')
        self.assertEqual(resume['certifications'][0]['issuing_organization'], 'Global Tech Board')

        # 6. Existing work experience bullet points optimized based on JD
        self.assertTrue(len(resume['work_experience'][0]['bullet_points']) > 0)

        # 7. Existing project descriptions / highlights optimized
        self.assertTrue(len(resume['projects'][0]['highlights']) > 0 or len(resume['projects'][0]['description']) > 0)

        # 8. Verified Java-related experience incorporated
        self.assertIn('Java', str(resume['skills']) + str(resume['work_experience']))

        # 9. Unsupported Java/Spring Boot experience can suggest project or experience bullet points in proposed_content
        self.assertIsNotNone(resume.get('proposed_content'))

        # 10. Technical skills reorganized according to JD relevance
        self.assertIn('Java', resume['skills']['languages'])

        # 11. Professional summary rewritten without changing candidate's actual background
        self.assertTrue(len(resume['summary']) > 20)

        # 12. All changes highlighted and no modifications to immutable fields
        changes = current_v['change_analysis']
        for ch in changes:
            # Audit trail must not report changing company name or job title
            self.assertNotIn('change company', ch.get('reason', '').lower())
            self.assertNotIn('rename company', ch.get('reason', '').lower())

    def test_python_validator_restores_hallucinated_fields(self):
        """
        Validates that enforce_structural_identity deterministically restores
        any hallucinated protected fields generated by LLMs.
        """
        baseline = {
            "header": {
                "full_name": "Priyanjul Sonkar",
                "email": "priyanjul@test.com",
                "phone": "+1 555-1234",
                "location": "New York, NY"
            },
            "work_experience": [
                {
                    "company": "Company A",
                    "title": "Software Development Intern",
                    "start_date": "Jan 2023",
                    "end_date": "Jun 2023",
                    "location": "Austin, TX",
                    "is_current": False,
                    "technologies": ["Java"],
                    "bullet_points": ["Original intern bullet."]
                }
            ],
            "projects": [
                {
                    "title": "E-Commerce Platform",
                    "role": "Developer",
                    "url": "https://github.com/project",
                    "technologies": ["Java"],
                    "description": "Original description.",
                    "highlights": ["Original highlight."]
                }
            ],
            "education": [
                {
                    "institution": "State University",
                    "degree": "Bachelor of Technology",
                    "end_date": "2023"
                }
            ],
            "certifications": [
                {
                    "name": "Original Certification",
                    "issuing_organization": "Tech Board",
                    "issue_date": "2022"
                }
            ]
        }

        # Simulated corrupted / hallucinated LLM generation
        hallucinated_resume = {
            "header": {
                "full_name": "John Doe Senior Architect",
                "email": "hacked@example.com",
                "phone": "+1 999-9999",
                "location": "Silicon Valley, CA",
                "headline": "Staff Distributed Systems Engineer"
            },
            "summary": "15+ years leading Fortune 500 engineering teams.",
            "skills": {
                "languages": ["Java", "Rust"],
                "frameworks": ["Spring Boot"]
            },
            "work_experience": [
                {
                    "company": "Google Enterprise Cloud",
                    "title": "Senior Staff Backend Engineer",
                    "start_date": "2018",
                    "end_date": "Present",
                    "is_current": True,
                    "technologies": ["Java 21", "Kubernetes"],
                    "bullet_points": ["Engineered distributed payment gateway at Google processing 50M ops/sec."]
                }
            ],
            "projects": [
                {
                    "title": "Fictional Autonomous Cloud Orchestrator",
                    "role": "Chief Architect",
                    "technologies": ["Go", "Kubernetes"],
                    "description": "Fictional project description.",
                    "highlights": ["Zero latency cluster orchestration."]
                }
            ],
            "education": [
                {
                    "institution": "Stanford University",
                    "degree": "Ph.D. in Distributed Systems",
                    "end_date": "2015"
                }
            ],
            "certifications": [
                {
                    "name": "AWS Certified Solutions Architect Professional",
                    "issuing_organization": "Amazon Web Services",
                    "issue_date": "2024"
                }
            ],
            "changes_applied": [
                {
                    "section": "Header",
                    "change_type": "MODIFIED",
                    "reason": "Upgrade candidate name to Senior Architect",
                    "original_content": "Priyanjul",
                    "updated_content": "John Doe Senior Architect"
                }
            ]
        }

        # Enforce structural preservation
        restored = enforce_structural_identity(baseline, hallucinated_resume)

        # Assertions
        self.assertEqual(restored['header']['full_name'], 'Priyanjul Sonkar')
        self.assertEqual(restored['header']['email'], 'priyanjul@test.com')
        self.assertEqual(restored['header']['phone'], '+1 555-1234')
        self.assertEqual(restored['header']['location'], 'New York, NY')

        self.assertEqual(restored['work_experience'][0]['company'], 'Company A')
        self.assertEqual(restored['work_experience'][0]['title'], 'Software Development Intern')
        self.assertEqual(restored['work_experience'][0]['start_date'], 'Jan 2023')
        self.assertEqual(restored['work_experience'][0]['end_date'], 'Jun 2023')

        self.assertEqual(restored['projects'][0]['title'], 'E-Commerce Platform')

        self.assertEqual(restored['education'][0]['degree'], 'Bachelor of Technology')
        self.assertEqual(restored['education'][0]['institution'], 'State University')

        self.assertEqual(restored['certifications'][0]['name'], 'Original Certification')
        self.assertEqual(restored['certifications'][0]['issuing_organization'], 'Tech Board')

        # Assert changes_applied does not contain illegal header/immutable modification
        self.assertEqual(len(restored['changes_applied']), 0)

        # Validate that the validator accepts the restored resume
        is_valid, violations = validate_structural_identity(baseline, restored)
        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)


