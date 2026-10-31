import os
import io
import logging
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import HttpResponse, FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.documents.models import JobDescription, ReferenceResume
from apps.profiles.models import CareerProfile
from apps.profiles.serializers import CareerProfileSerializer
from apps.history.models import ResumeMatchReport, FinalizedResumeHistory
from apps.pdf_engine.ats_generator import generate_ats_pdf, normalize_filename

from services.llm.factory import get_llm_provider
from services.matching.score_calculator import calculate_jd_match_scores
from services.diff.resume_differ import compute_structured_diff

from prompts.jd_analysis import get_jd_analysis_system_instruction, build_jd_analysis_prompt
from prompts.resume_generation import get_generation_system_instruction, build_resume_generation_prompt
from prompts.resume_revision import get_revision_system_instruction, build_resume_revision_prompt
from prompts.resume_validation import StructuredResumeSchema, JDAnalysisSchema

from .models import ResumeGeneration, ResumeVersion, ResumeRevision, GenerationStatus
from .serializers import (
    ResumeGenerationSerializer,
    ResumeVersionSerializer,
    AnalyzeAndGenerateRequestSerializer,
    ReviseRequestSerializer,
    ApproveRequestSerializer,
)

logger = logging.getLogger(__name__)


def _serialize_profile_for_llm(user) -> dict:
    """Serializes the user's complete career profile into a clean dictionary for prompt context."""
    profile = CareerProfile.objects.filter(user=user).first()
    if not profile:
        return {
            "full_name": f"{user.first_name} {user.last_name}".strip() or user.username,
            "email": user.email,
            "experiences": [],
            "projects": [],
            "skills": [],
            "education": [],
            "certifications": []
        }
    return CareerProfileSerializer(profile).data


class AnalyzeAndGenerateView(APIView):
    """
    Step 1: Analyzes JD, checks candidate profile & reference resume,
    generates initial role-specific optimized draft (v1), and returns
    structured content, change highlights, and match score.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = AnalyzeAndGenerateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        user = request.user

        # 1. Resolve Job Description
        jd_id = data.get('job_description_id')
        jd_text = data.get('job_description_text', '').strip()
        target_role = data.get('target_role', '').strip()
        target_company = data.get('target_company', '').strip()

        if jd_id:
            jd_obj = get_object_or_404(JobDescription, id=jd_id, user=user)
            if not target_role:
                target_role = jd_obj.target_role
            if not target_company:
                target_company = jd_obj.target_company
        else:
            if not jd_text:
                return Response({'error': 'Job description text or existing ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
            if not target_role:
                target_role = "Software Engineer"
            jd_obj = JobDescription.objects.create(
                user=user,
                target_role=target_role,
                target_company=target_company,
                raw_text=jd_text
            )

        # 2. Resolve Reference Resume
        ref_id = data.get('reference_resume_id')
        ref_obj = None
        ref_text = ""
        if ref_id:
            ref_obj = get_object_or_404(ReferenceResume, id=ref_id, user=user)
            ref_text = ref_obj.raw_text

        experience_level = data.get('experience_level', 'FRESHER')
        additional_details = data.get('additional_experience_details', '')

        # 3. Retrieve Complete Career Profile
        profile_data = _serialize_profile_for_llm(user)

        # 4. LLM Provider
        llm = get_llm_provider()

        # Step A: Analyze JD if not already cached
        jd_analysis = jd_obj.parsed_analysis
        if not jd_analysis or not jd_analysis.get('mandatory_skills'):
            jd_prompt = build_jd_analysis_prompt(target_role, target_company, jd_obj.raw_text)
            try:
                jd_analysis = llm.generate_structured(
                    prompt=jd_prompt,
                    system_instruction=get_jd_analysis_system_instruction(),
                    schema=JDAnalysisSchema
                )
                jd_obj.parsed_analysis = jd_analysis
                jd_obj.save()
            except Exception as e:
                logger.error(f"Error during JD analysis: {str(e)}")
                # Use fallback dictionary
                jd_analysis = {
                    "target_role": target_role,
                    "mandatory_skills": [target_role, "Backend Development", "REST APIs"],
                    "preferred_skills": ["Cloud", "Databases"],
                    "important_ats_keywords": [target_role, "Software Engineering"]
                }

        # Step B: Generate Role-Specific Resume (v1)
        gen_prompt = build_resume_generation_prompt(
            target_role=target_role,
            target_company=target_company,
            experience_level=experience_level,
            additional_experience_details=additional_details,
            jd_analysis=jd_analysis,
            career_profile_data=profile_data,
            reference_resume_text=ref_text
        )

        try:
            resume_data = llm.generate_structured(
                prompt=gen_prompt,
                system_instruction=get_generation_system_instruction(),
                schema=StructuredResumeSchema
            )
        except Exception as e:
            logger.error(f"Resume generation LLM failure: {str(e)}")
            return Response(
                {'error': f"Failed to generate resume with AI service: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Step C: Compute Match Scores and Diffs
        scores = calculate_jd_match_scores(jd_analysis, resume_data)
        raw_changes = resume_data.get('changes_applied', [])
        structured_diffs = compute_structured_diff({}, resume_data, raw_changes)

        # Step D: Save Generation and Version 1
        generation = ResumeGeneration.objects.create(
            user=user,
            job_description=jd_obj,
            reference_resume=ref_obj,
            target_role=target_role,
            target_company=target_company,
            experience_level=experience_level,
            additional_experience_details=additional_details,
            status=GenerationStatus.DRAFT,
            current_version_number=1
        )

        version_1 = ResumeVersion.objects.create(
            generation=generation,
            version_number=1,
            structured_resume_data=resume_data,
            change_analysis=structured_diffs,
            user_instructions="Initial JD-optimized generation."
        )

        ResumeMatchReport.objects.create(
            version=version_1,
            overall_evidence_score=scores['overall_evidence_score'],
            keyword_coverage_score=scores['keyword_coverage_score'],
            mandatory_skills_score=scores['mandatory_skills_score'],
            preferred_skills_score=scores['preferred_skills_score'],
            experience_relevance_score=scores['experience_relevance_score'],
            matched_mandatory_skills=scores['matched_mandatory_skills'],
            missing_mandatory_skills=scores['missing_mandatory_skills'],
            matched_preferred_skills=scores['matched_preferred_skills'],
            missing_preferred_skills=scores['missing_preferred_skills'],
            matched_keywords=scores['matched_keywords'],
            missing_keywords=scores['missing_keywords'],
            evidence_gaps=scores['evidence_gaps']
        )

        serializer_out = ResumeGenerationSerializer(generation)
        return Response(serializer_out.data, status=status.HTTP_201_CREATED)


class ResumeGenerationDetailView(APIView):
    """Retrieves full resume generation session including all versions and current draft."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        generation = get_object_or_404(ResumeGeneration, id=pk, user=request.user)
        serializer = ResumeGenerationSerializer(generation)
        return Response(serializer.data)


class ResumeReviseView(APIView):
    """
    Human-in-the-Loop Step: User clicks NO.
    Receives user comment, re-runs revision with LLM, creates version N+1,
    recalculates JD score and diffs, and preserves revision history.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        generation = get_object_or_404(ResumeGeneration, id=pk, user=request.user)

        if generation.status == GenerationStatus.CANCELLED:
            return Response({'error': 'Cannot revise a cancelled generation session.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ReviseRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_comment = serializer.validated_data['user_comment']

        # Get current version
        current_version = generation.versions.filter(version_number=generation.current_version_number).first()
        if not current_version:
            return Response({'error': 'Current version not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Record revision attempt
        ResumeRevision.objects.create(
            version=current_version,
            user_action=ResumeRevision.ActionType.NO,
            user_comment=user_comment
        )

        # Prepare context for revision
        profile_data = _serialize_profile_for_llm(request.user)
        jd_analysis = generation.job_description.parsed_analysis or {}
        llm = get_llm_provider()

        rev_prompt = build_resume_revision_prompt(
            previous_resume_data=current_version.structured_resume_data,
            user_comment=user_comment,
            target_role=generation.target_role,
            jd_analysis=jd_analysis,
            career_profile_data=profile_data
        )

        try:
            revised_data = llm.generate_structured(
                prompt=rev_prompt,
                system_instruction=get_revision_system_instruction(),
                schema=StructuredResumeSchema
            )
        except Exception as e:
            logger.error(f"Error during revision LLM call: {str(e)}")
            return Response({'error': f"Revision failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Compute updated match scores & diffs against previous version
        scores = calculate_jd_match_scores(jd_analysis, revised_data)
        raw_changes = revised_data.get('changes_applied', [])
        structured_diffs = compute_structured_diff(current_version.structured_resume_data, revised_data, raw_changes)

        new_version_num = generation.current_version_number + 1

        new_version = ResumeVersion.objects.create(
            generation=generation,
            version_number=new_version_num,
            structured_resume_data=revised_data,
            change_analysis=structured_diffs,
            user_instructions=user_comment
        )

        ResumeMatchReport.objects.create(
            version=new_version,
            overall_evidence_score=scores['overall_evidence_score'],
            keyword_coverage_score=scores['keyword_coverage_score'],
            mandatory_skills_score=scores['mandatory_skills_score'],
            preferred_skills_score=scores['preferred_skills_score'],
            experience_relevance_score=scores['experience_relevance_score'],
            matched_mandatory_skills=scores['matched_mandatory_skills'],
            missing_mandatory_skills=scores['missing_mandatory_skills'],
            matched_preferred_skills=scores['matched_preferred_skills'],
            missing_preferred_skills=scores['missing_preferred_skills'],
            matched_keywords=scores['matched_keywords'],
            missing_keywords=scores['missing_keywords'],
            evidence_gaps=scores['evidence_gaps']
        )

        generation.current_version_number = new_version_num
        generation.status = GenerationStatus.REVISING
        generation.save()

        return Response(ResumeGenerationSerializer(generation).data, status=status.HTTP_200_OK)


class ResumeApproveView(APIView):
    """
    Human-in-the-Loop Step: User clicks YES.
    Applies any final user comments, marks generation APPROVED,
    generates backend ATS PDF, and records in FinalizedResumeHistory.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        generation = get_object_or_404(ResumeGeneration, id=pk, user=request.user)

        if generation.status == GenerationStatus.CANCELLED:
            return Response({'error': 'Cannot approve a cancelled generation session.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ApproveRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_comment = serializer.validated_data.get('user_comment', '').strip()
        page_format = serializer.validated_data.get('page_format', 'ONE_PAGE')
        custom_filename = serializer.validated_data.get('custom_filename', '').strip()

        current_version = generation.versions.filter(version_number=generation.current_version_number).first()
        if not current_version:
            return Response({'error': 'Current version not found.'}, status=status.HTTP_404_NOT_FOUND)

        final_resume_data = current_version.structured_resume_data

        # If user supplied a final instruction with YES, apply it before finalizing
        if user_comment:
            ResumeRevision.objects.create(
                version=current_version,
                user_action=ResumeRevision.ActionType.YES,
                user_comment=f"Approved with note: {user_comment}"
            )
            llm = get_llm_provider()
            profile_data = _serialize_profile_for_llm(request.user)
            jd_analysis = generation.job_description.parsed_analysis or {}
            rev_prompt = build_resume_revision_prompt(
                previous_resume_data=final_resume_data,
                user_comment=user_comment,
                target_role=generation.target_role,
                jd_analysis=jd_analysis,
                career_profile_data=profile_data
            )
            try:
                final_resume_data = llm.generate_structured(
                    prompt=rev_prompt,
                    system_instruction=get_revision_system_instruction(),
                    schema=StructuredResumeSchema
                )
                current_version.structured_resume_data = final_resume_data
                current_version.save()
            except Exception as e:
                logger.warning(f"Could not apply final note before approval: {e}")
        else:
            ResumeRevision.objects.create(
                version=current_version,
                user_action=ResumeRevision.ActionType.YES,
                user_comment="Approved without extra comments."
            )

        # Mark status APPROVED
        generation.status = GenerationStatus.APPROVED
        generation.save()

        # Candidate name for file normalization
        candidate_name = final_resume_data.get('header', {}).get('full_name') or request.user.get_full_name() or request.user.username

        if custom_filename:
            filename = custom_filename if custom_filename.endswith('.pdf') else f"{custom_filename}.pdf"
        else:
            filename = normalize_filename(
                candidate_name=candidate_name,
                company_name=generation.target_company or 'company',
                target_role=generation.target_role,
                version_number=generation.current_version_number
            )

        # Generate ATS PDF
        try:
            pdf_bytes = generate_ats_pdf(final_resume_data, page_format=page_format)
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            return Response({'error': f"PDF generation error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Match report
        match_report = getattr(current_version, 'match_report', None)
        overall_score = match_report.overall_evidence_score if match_report else 80.0
        keyword_score = match_report.keyword_coverage_score if match_report else 85.0

        # Save to Resume History
        history_entry = FinalizedResumeHistory.objects.create(
            user=request.user,
            generation=generation,
            approved_version=current_version,
            match_report=match_report,
            target_role=generation.target_role,
            target_company=generation.target_company,
            experience_level=generation.experience_level,
            final_resume_data=final_resume_data,
            page_format=page_format,
            filename=filename,
            overall_evidence_score=overall_score,
            keyword_coverage_score=keyword_score,
            version_number=generation.current_version_number
        )

        history_entry.pdf_file.save(filename, ContentFile(pdf_bytes), save=True)

        return Response({
            'message': 'Resume approved and finalized successfully!',
            'generation_id': generation.id,
            'history_id': history_entry.id,
            'filename': filename,
            'pdf_url': f"/api/resume-generations/{generation.id}/pdf/",
            'download_url': f"/api/resume-generations/{generation.id}/download/",
            'final_resume': final_resume_data
        }, status=status.HTTP_200_OK)


class ResumeCancelView(APIView):
    """
    Cancels the resume generation session.
    Preserves drafts in database, does not generate a finalized PDF,
    and allows user to safely return to dashboard.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        generation = get_object_or_404(ResumeGeneration, id=pk, user=request.user)
        generation.status = GenerationStatus.CANCELLED
        generation.save()

        # Log revision cancel event
        current_version = generation.versions.filter(version_number=generation.current_version_number).first()
        if current_version:
            ResumeRevision.objects.create(
                version=current_version,
                user_action=ResumeRevision.ActionType.CANCEL,
                user_comment="User terminated review process via CANCEL button."
            )

        return Response({
            'message': 'Resume generation session has been cancelled.',
            'generation_id': generation.id,
            'status': generation.status
        }, status=status.HTTP_200_OK)


class ResumePdfView(APIView):
    """Streams the generated PDF for browser view / preview."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        generation = get_object_or_404(ResumeGeneration, id=pk, user=request.user)
        history_entry = FinalizedResumeHistory.objects.filter(generation=generation).order_by('-id').first()

        if not history_entry or not history_entry.pdf_file:
            # If not yet approved or finalized, generate preview from current version on the fly!
            current_version = generation.versions.filter(version_number=generation.current_version_number).first()
            if not current_version:
                raise Http404("No resume content found.")
            pdf_bytes = generate_ats_pdf(current_version.structured_resume_data, page_format='ONE_PAGE')
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="resume_preview.pdf"'
            return response

        try:
            return FileResponse(history_entry.pdf_file.open('rb'), content_type='application/pdf')
        except Exception:
            raise Http404("PDF file not found on storage.")


class ResumeDownloadView(APIView):
    """Downloads the finalized PDF file with user-specified or normalized filename."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        generation = get_object_or_404(ResumeGeneration, id=pk, user=request.user)
        history_entry = FinalizedResumeHistory.objects.filter(generation=generation).order_by('-id').first()

        if not history_entry or not history_entry.pdf_file:
            return Response({'error': 'PDF not yet finalized. Please approve resume first.'}, status=status.HTTP_400_BAD_REQUEST)

        response = FileResponse(history_entry.pdf_file.open('rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{history_entry.filename}"'
        return response
