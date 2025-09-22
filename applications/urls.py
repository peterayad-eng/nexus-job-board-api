from django.urls import path
from .views import (
    ApplicationListCreateView,
    ApplicationRetrieveView,
    UserApplicationsView,
    JobApplicationsView,
    JobApplicationCountView,
    ApplicationAdminListView,
    ApplicationStatusUpdateView,
    CompanyApplicationsView
)

urlpatterns = [
    # Main applications endpoints
    path('', ApplicationListCreateView.as_view(), name='application-list-create'),
    path('<int:pk>/', ApplicationRetrieveView.as_view(), name='application-detail'),
    
    # User-specific applications
    path('my-applications/', UserApplicationsView.as_view(), name='user-applications'),
    
    # Job-specific applications
    path('job/<int:job_id>/', JobApplicationsView.as_view(), name='job-applications'),
    path('job/<int:job_id>/count/', JobApplicationCountView.as_view(), name='job-application-count'),
    
    # Company-specific applications
    path('company/<int:company_id>/', CompanyApplicationsView.as_view(), name='company-applications'),
    
    # Application management
    path('<int:pk>/status/', ApplicationStatusUpdateView.as_view(), name='application-status-update'),
    
    # Admin endpoints
    path('admin/all/', ApplicationAdminListView.as_view(), name='admin-application-list'),
]

