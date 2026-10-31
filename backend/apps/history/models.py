from django.db import models
from django.contrib.auth.models import User
from apps.generations.models import ResumeGeneration, ResumeVersion

class ResumeMatchReport(models.Model):
    version = models.OneToOneField(ResumeVersion, on_delete=models.CASCADE, related_name='match_report')
    overall_evidence_score = models.FloatField(default=0.0)
    keyword_coverage_score = models.FloatField(default=0.0)
    mandatory_skills_score = models.FloatField(default=0.0)
    preferred_skills_score = models.FloatField(default=0.0)
    experience_relevance_score = models.FloatField(default=0.0)
    matched_mandatory_skills = models.JSONField(default=list, blank=True)
    missing_mandatory_skills = models.JSONField(default=list, blank=True)
    matched_preferred_skills = models.JSONField(default=list, blank=True)
    missing_preferred_skills = models.JSONField(default=list, blank=True)
    matched_keywords = models.JSONField(default=list, blank=True)
    missing_keywords = models.JSONField(default=list, blank=True)
    evidence_gaps = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"MatchReport for {self.version} ({self.overall_evidence_score}%)"


class FinalizedResumeHistory(models.Model):
    class PageFormat(models.TextChoices):
        ONE_PAGE = 'ONE_PAGE', 'One-Page Resume'
        TWO_PAGE = 'TWO_PAGE', 'Two-Page Resume'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resume_history')
    generation = models.ForeignKey(ResumeGeneration, on_delete=models.CASCADE, related_name='history_entries')
    approved_version = models.ForeignKey(ResumeVersion, on_delete=models.CASCADE, related_name='history_finalizations')
    match_report = models.ForeignKey(ResumeMatchReport, on_delete=models.SET_NULL, null=True, blank=True)
    
    target_role = models.CharField(max_length=255)
    target_company = models.CharField(max_length=255, blank=True)
    experience_level = models.CharField(max_length=50)
    final_resume_data = models.JSONField(default=dict)
    
    page_format = models.CharField(max_length=20, choices=PageFormat.choices, default=PageFormat.ONE_PAGE)
    filename = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to='final_resumes/', blank=True, null=True)
    
    overall_evidence_score = models.FloatField(default=0.0)
    keyword_coverage_score = models.FloatField(default=0.0)
    version_number = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.filename} - {self.target_role} ({self.overall_evidence_score}%)"
