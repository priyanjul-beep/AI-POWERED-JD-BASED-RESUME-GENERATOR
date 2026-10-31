from django.urls import path
from .views import (
    JobDescriptionListCreateView,
    JobDescriptionDetailView,
    ReferenceResumeListCreateView,
    ReferenceResumeDetailView,
)

urlpatterns = [
    path('jds/', JobDescriptionListCreateView.as_view(), name='jd_list_create'),
    path('jds/<int:pk>/', JobDescriptionDetailView.as_view(), name='jd_detail'),
    path('reference-resumes/', ReferenceResumeListCreateView.as_view(), name='reference_resume_list_create'),
    path('reference-resumes/<int:pk>/', ReferenceResumeDetailView.as_view(), name='reference_resume_detail'),
]
