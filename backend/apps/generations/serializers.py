from rest_framework import serializers
from .models import ResumeGeneration, ResumeVersion, ResumeRevision, ExperienceLevel, GenerationStatus
from apps.history.models import ResumeMatchReport

class ResumeMatchReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeMatchReport
        fields = '__all__'


class ResumeRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeRevision
        fields = '__all__'


class ResumeVersionSerializer(serializers.ModelSerializer):
    match_report = ResumeMatchReportSerializer(read_only=True)
    revisions = ResumeRevisionSerializer(many=True, read_only=True)

    class Meta:
        model = ResumeVersion
        fields = (
            'id', 'version_number', 'structured_resume_data',
            'change_analysis', 'user_instructions', 'created_at',
            'match_report', 'revisions'
        )


class ResumeGenerationSerializer(serializers.ModelSerializer):
    versions = ResumeVersionSerializer(many=True, read_only=True)
    current_version = serializers.SerializerMethodField()

    class Meta:
        model = ResumeGeneration
        fields = (
            'id', 'target_role', 'target_company', 'experience_level',
            'additional_experience_details', 'status', 'current_version_number',
            'created_at', 'updated_at', 'versions', 'current_version',
            'job_description', 'reference_resume'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_current_version(self, obj):
        ver = obj.versions.filter(version_number=obj.current_version_number).first()
        if ver:
            return ResumeVersionSerializer(ver).data
        return None


class AnalyzeAndGenerateRequestSerializer(serializers.Serializer):
    job_description_id = serializers.IntegerField(required=False)
    job_description_text = serializers.CharField(required=False, allow_blank=True)
    target_role = serializers.CharField(required=False, allow_blank=True)
    target_company = serializers.CharField(required=False, allow_blank=True)
    reference_resume_id = serializers.IntegerField(required=False, allow_null=True)
    experience_level = serializers.ChoiceField(choices=ExperienceLevel.choices, default=ExperienceLevel.FRESHER)
    additional_experience_details = serializers.CharField(required=False, allow_blank=True)


class ReviseRequestSerializer(serializers.Serializer):
    user_comment = serializers.CharField(required=True, min_length=2)


class ApproveRequestSerializer(serializers.Serializer):
    user_comment = serializers.CharField(required=False, allow_blank=True)
    page_format = serializers.ChoiceField(choices=['ONE_PAGE', 'TWO_PAGE'], default='ONE_PAGE')
    custom_filename = serializers.CharField(required=False, allow_blank=True)
