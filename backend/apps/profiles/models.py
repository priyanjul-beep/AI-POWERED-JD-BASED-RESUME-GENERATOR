from django.db import models
from django.contrib.auth.models import User

class CareerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='career_profile')
    full_name = models.CharField(max_length=255, blank=True)
    headline = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=255, blank=True)
    linkedin_url = models.URLField(max_length=500, blank=True)
    github_url = models.URLField(max_length=500, blank=True)
    portfolio_url = models.URLField(max_length=500, blank=True)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CareerProfile for {self.user.username}"


class Experience(models.Model):
    class ExperienceType(models.TextChoices):
        PROFESSIONAL = 'PROFESSIONAL', 'Professional Experience'
        INTERNSHIP = 'INTERNSHIP', 'Internship Experience'
        APPRENTICE = 'APPRENTICE', 'Apprentice Experience'

    profile = models.ForeignKey(CareerProfile, on_delete=models.CASCADE, related_name='experiences')
    experience_type = models.CharField(
        max_length=20,
        choices=ExperienceType.choices,
        default=ExperienceType.PROFESSIONAL
    )
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    start_date = models.CharField(max_length=50) # e.g. "Jun 2023" or "2023-06"
    end_date = models.CharField(max_length=50, blank=True) # e.g. "Present" or "Dec 2023"
    is_current = models.BooleanField(default=False)
    technologies = models.JSONField(default=list, blank=True) # list of tech names
    bullet_points = models.JSONField(default=list, blank=True) # list of responsibilities & quantifiable achievements
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.title} at {self.company} ({self.experience_type})"


class Project(models.Model):
    profile = models.ForeignKey(CareerProfile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=255)
    role = models.CharField(max_length=255, blank=True)
    url = models.URLField(max_length=500, blank=True)
    technologies = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)
    highlights = models.JSONField(default=list, blank=True) # bullet points
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title


class Skill(models.Model):
    class SkillCategory(models.TextChoices):
        LANGUAGES = 'LANGUAGES', 'Programming Languages'
        FRAMEWORKS = 'FRAMEWORKS', 'Frameworks & Libraries'
        DATABASES = 'DATABASES', 'Databases'
        CLOUD = 'CLOUD', 'Cloud & DevOps'
        TOOLS = 'TOOLS', 'Development Tools'
        OTHER = 'OTHER', 'Other / Concepts'

    profile = models.ForeignKey(CareerProfile, on_delete=models.CASCADE, related_name='skills')
    category = models.CharField(
        max_length=30,
        choices=SkillCategory.choices,
        default=SkillCategory.LANGUAGES
    )
    name = models.CharField(max_length=100)
    proficiency_level = models.CharField(max_length=50, blank=True, default='Intermediate') # Beginner, Intermediate, Advanced, Expert
    years_used = models.FloatField(default=1.0, blank=True, null=True)

    class Meta:
        unique_together = ('profile', 'name', 'category')
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.category})"


class Education(models.Model):
    profile = models.ForeignKey(CareerProfile, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255, blank=True)
    start_date = models.CharField(max_length=50, blank=True)
    end_date = models.CharField(max_length=50, blank=True)
    grade = models.CharField(max_length=50, blank=True)
    honors = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class Certification(models.Model):
    profile = models.ForeignKey(CareerProfile, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255)
    issue_date = models.CharField(max_length=50, blank=True)
    credential_id = models.CharField(max_length=255, blank=True)
    credential_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.name} ({self.issuing_organization})"
