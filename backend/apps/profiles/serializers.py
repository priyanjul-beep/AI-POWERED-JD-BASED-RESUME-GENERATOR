from rest_framework import serializers
from .models import CareerProfile, Experience, Project, Skill, Education, Certification

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = '__all__'
        read_only_fields = ('profile', 'created_at', 'updated_at')


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('profile', 'created_at', 'updated_at')


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'
        read_only_fields = ('profile',)


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'
        read_only_fields = ('profile', 'created_at')


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = '__all__'
        read_only_fields = ('profile', 'created_at')


class CareerProfileSerializer(serializers.ModelSerializer):
    experiences = ExperienceSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)

    class Meta:
        model = CareerProfile
        fields = (
            'id', 'full_name', 'headline', 'email', 'phone', 'location',
            'linkedin_url', 'github_url', 'portfolio_url', 'summary',
            'experiences', 'projects', 'skills', 'education', 'certifications',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
