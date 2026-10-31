from django.urls import path
from .views import (
    ResumeHistoryListView,
    ResumeHistoryDetailView,
    ResumeHistoryMatchReportView,
    DashboardStatsView,
)

urlpatterns = [
    path('', ResumeHistoryListView.as_view(), name='resume_history_list'),
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('<int:pk>/', ResumeHistoryDetailView.as_view(), name='resume_history_detail'),
    path('<int:pk>/match-report/', ResumeHistoryMatchReportView.as_view(), name='resume_history_match_report'),
]
