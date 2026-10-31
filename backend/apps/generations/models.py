from django.db import models
from django.contrib.auth.models import User
from apps.documents.models import JobDescription, ReferenceResume

class ExperienceLevel(models.TextChoices):
    FRESHER = 'FRESHER', 'Fresher (No professional experience)'
    NO_INTERNSHIP = 'NO_INTERNSHIP', 'No Internship Experience'
    INTERNSHIP = 'INTERNSHIP', 'Internship Experience'
    APPRENTICE = 'APPRENTICE', 'Apprentice Experience'
    ONE_YEAR = '1_YEAR', '1 Year of Experience'
    TWO_YEARS = '2_YEARS', '2 Years of Experience'
    THREE_YEARS = '3_YEARS', '3 Years of Experience'
    FOUR_YEARS = '4_YEARS', '4 Years of Experience'
    FIVE_PLUS_YEARS = '5_PLUS_YEARS', '5+ Years of Experience'


class GenerationStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft - Awaiting Review'
    REVISING = 'REVISING', 'Revising from Feedback'
    APPROVED = 'APPROVED', 'Approved by User'
    CANCELLED = 'CANCELLED', 'Cancelled by User'


class ResumeGeneration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resume_generations')
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name='generations')
    reference_resume = models.ForeignKey(ReferenceResume, on_delete=models.SET_NULL, null=True, blank=True, related_name='generations')
    target_role = models.CharField(max_length=255)
    target_company = models.CharField(max_length=255, blank=True)
    experience_level = models.CharField(
        max_length=30,
        choices=ExperienceLevel.choices,
        default=ExperienceLevel.FRESHER
    )
    additional_experience_details = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=GenerationStatus.choices,
        default=GenerationStatus.DRAFT
    )
    current_version_number = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"ResumeGen #{self.id} - {self.target_role} ({self.status})"


class ResumeVersion(models.Model):
    generation = models.ForeignKey(ResumeGeneration, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    structured_resume_data = models.JSONField(default=dict)
    change_analysis = models.JSONField(default=list, blank=True)
    user_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['version_number']
        unique_together = ('generation', 'version_number')

    def __str__(self):
        return f"Gen #{self.generation_id} - v{self.version_number}"


class ResumeRevision(models.Model):
    class ActionType(models.TextChoices):
        YES = 'YES', 'Approved'
        NO = 'NO', 'Needs Revision'
        CANCEL = 'CANCEL', 'Cancelled'

    version = models.ForeignKey(ResumeVersion, on_delete=models.CASCADE, related_name='revisions')
    user_action = models.CharField(max_length=10, choices=ActionType.choices)
    user_comment = models.TextField(blank=True)
    prompt_snapshot = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Revision on {self.version} ({self.user_action})"
