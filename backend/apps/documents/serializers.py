from rest_framework import serializers
from .models import JobDescription, ReferenceResume
from .parsers import parse_uploaded_document, parse_resume_document_full, DocumentParserError

class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = ('id', 'target_role', 'target_company', 'raw_text', 'uploaded_file', 'parsed_analysis', 'created_at')
        read_only_fields = ('id', 'parsed_analysis', 'created_at')
        extra_kwargs = {
            'raw_text': {'required': False, 'allow_blank': True}
        }

    def validate(self, data):
        raw_text = data.get('raw_text', '').strip()
        uploaded_file = data.get('uploaded_file')

        if not raw_text and not uploaded_file:
            raise serializers.ValidationError('Please provide job description text or upload a document (PDF/DOCX).')

        if uploaded_file and not raw_text:
            try:
                extracted = parse_uploaded_document(uploaded_file, uploaded_file.name)
                if not extracted.strip():
                    raise serializers.ValidationError('Could not extract text from the uploaded JD file.')
                data['raw_text'] = extracted
            except DocumentParserError as e:
                raise serializers.ValidationError(str(e))

        return data


class ReferenceResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferenceResume
        fields = ('id', 'file_name', 'uploaded_file', 'raw_text', 'parsed_data', 'created_at')
        read_only_fields = ('id', 'raw_text', 'parsed_data', 'created_at')

    def create(self, validated_data):
        uploaded_file = validated_data.get('uploaded_file')
        raw_text = ""
        extracted_projects = []
        file_name = validated_data.get('file_name', '')
        if uploaded_file:
            if not file_name:
                file_name = uploaded_file.name
                validated_data['file_name'] = file_name
            try:
                raw_text, extracted_projects = parse_resume_document_full(uploaded_file, uploaded_file.name)
            except DocumentParserError as e:
                raise serializers.ValidationError(str(e))

        validated_data['raw_text'] = raw_text
        if extracted_projects:
            validated_data['parsed_data'] = {'projects': extracted_projects}
        return super().create(validated_data)
