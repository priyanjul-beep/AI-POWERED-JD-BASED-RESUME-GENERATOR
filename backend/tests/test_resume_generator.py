import json
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from apps.profiles.models import CareerProfile, Experience, Project, Skill
from apps.documents.models import JobDescription, ReferenceResume
from apps.generations.models import ResumeGeneration, ResumeVersion, GenerationStatus
from apps.history.models import FinalizedResumeHistory
from apps.pdf_engine.ats_generator import normalize_filename, generate_ats_pdf
from services.matching.score_calculator import calculate_jd_match_scores
from services.diff.resume_differ import compute_structured_diff

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
