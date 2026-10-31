from rest_framework import serializers
from .models import FinalizedResumeHistory, ResumeMatchReport

class ResumeMatchReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeMatchReport
        fields = '__all__'


class FinalizedResumeHistorySerializer(serializers.ModelSerializer):
    match_report = ResumeMatchReportSerializer(read_only=True)
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = FinalizedResumeHistory
        fields = (
            'id', 'generation', 'approved_version', 'target_role',
            'target_company', 'experience_level', 'final_resume_data',
            'page_format', 'filename', 'overall_evidence_score',
            'keyword_coverage_score', 'version_number', 'pdf_file',
            'pdf_url', 'match_report', 'created_at'
        )

    def get_pdf_url(self, obj):
        if obj.pdf_file:
            return obj.pdf_file.url
        return f"/api/resume-generations/{obj.generation_id}/pdf/"
