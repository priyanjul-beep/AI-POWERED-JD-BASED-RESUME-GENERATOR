from django.urls import path
from .views import (
    AnalyzeAndGenerateView,
    ResumeGenerationDetailView,
    ResumeReviseView,
    ResumeApproveView,
    ResumeCancelView,
    ResumePdfView,
    ResumeDownloadView,
)

urlpatterns = [
    path('analyze/', AnalyzeAndGenerateView.as_view(), name='generation_analyze'),
    path('<int:pk>/', ResumeGenerationDetailView.as_view(), name='generation_detail'),
    path('<int:pk>/revise/', ResumeReviseView.as_view(), name='generation_revise'),
    path('<int:pk>/approve/', ResumeApproveView.as_view(), name='generation_approve'),
    path('<int:pk>/cancel/', ResumeCancelView.as_view(), name='generation_cancel'),
    path('<int:pk>/pdf/', ResumePdfView.as_view(), name='generation_pdf_preview'),
    path('<int:pk>/download/', ResumeDownloadView.as_view(), name='generation_download'),
]
