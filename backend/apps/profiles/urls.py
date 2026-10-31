from django.urls import path
from .views import (
    CareerProfileView,
    ExperienceListCreateView,
    ExperienceDetailView,
    ProjectListCreateView,
    ProjectDetailView,
    SkillListCreateView,
    SkillDetailView,
    EducationListCreateView,
    EducationDetailView,
    CertificationListCreateView,
    CertificationDetailView,
)

urlpatterns = [
    path('', CareerProfileView.as_view(), name='career_profile'),
    path('experiences/', ExperienceListCreateView.as_view(), name='experience_list_create'),
    path('experiences/<int:pk>/', ExperienceDetailView.as_view(), name='experience_detail'),
    path('projects/', ProjectListCreateView.as_view(), name='project_list_create'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
    path('skills/', SkillListCreateView.as_view(), name='skill_list_create'),
    path('skills/<int:pk>/', SkillDetailView.as_view(), name='skill_detail'),
    path('education/', EducationListCreateView.as_view(), name='education_list_create'),
    path('education/<int:pk>/', EducationDetailView.as_view(), name='education_detail'),
    path('certifications/', CertificationListCreateView.as_view(), name='certification_list_create'),
    path('certifications/<int:pk>/', CertificationDetailView.as_view(), name='certification_detail'),
]
