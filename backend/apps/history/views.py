from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import FinalizedResumeHistory, ResumeMatchReport
from .serializers import FinalizedResumeHistorySerializer, ResumeMatchReportSerializer

class ResumeHistoryListView(generics.ListAPIView):
    """Lists all finalized resumes for the current user."""
    serializer_class = FinalizedResumeHistorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return FinalizedResumeHistory.objects.filter(user=self.request.user)


class ResumeHistoryDetailView(generics.RetrieveAPIView):
    """Returns detailed finalized resume snapshot and PDF details."""
    serializer_class = FinalizedResumeHistorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return FinalizedResumeHistory.objects.filter(user=self.request.user)


class ResumeHistoryMatchReportView(APIView):
    """Returns the dedicated JD match report for a historical resume."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        history_item = get_object_or_404(FinalizedResumeHistory, id=pk, user=request.user)
        match_report = history_item.match_report
        if not match_report:
            # Fallback to approved version match report
            match_report = getattr(history_item.approved_version, 'match_report', None)

        if not match_report:
            return Response({'error': 'Match report not found for this resume.'}, status=404)

        return Response(ResumeMatchReportSerializer(match_report).data)


class DashboardStatsView(APIView):
    """Provides high-level dashboard metrics for the user."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        history_qs = FinalizedResumeHistory.objects.filter(user=user)
        total_resumes = history_qs.count()
        avg_score = history_qs.aggregate(Avg('overall_evidence_score'))['overall_evidence_score__avg'] or 0.0

        recent_resumes = FinalizedResumeHistorySerializer(history_qs[:5], many=True).data

        return Response({
            'total_resumes_generated': total_resumes,
            'average_jd_match_score': round(avg_score, 1),
            'recent_resumes': recent_resumes
        })
