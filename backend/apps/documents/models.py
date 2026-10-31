from django.db import models
from django.contrib.auth.models import User

class JobDescription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_descriptions')
    target_role = models.CharField(max_length=255)
    target_company = models.CharField(max_length=255, blank=True)
    raw_text = models.TextField()
    uploaded_file = models.FileField(upload_to='jds/', blank=True, null=True)
    parsed_analysis = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.target_role} at {self.target_company or 'Unknown Company'}"


class ReferenceResume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reference_resumes')
    file_name = models.CharField(max_length=255, blank=True)
    uploaded_file = models.FileField(upload_to='reference_resumes/', blank=True, null=True)
    raw_text = models.TextField(blank=True)
    parsed_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"Reference Resume ({self.file_name or self.id}) for {self.user.username}"
