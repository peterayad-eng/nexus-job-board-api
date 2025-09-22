from django.urls import path
from .views import (
    JobListCreateView, JobRetrieveUpdateDestroyView, 
    JobSearchView, CompanyJobsView, JobAdminListView,
    JobActivationView
)

urlpatterns = [
    # Main jobs endpoint - list all jobs and create new ones
    path('', JobListCreateView.as_view(), name='job-list-create'),
    
    # Individual job management - retrieve, update, delete
    path('<int:pk>/', JobRetrieveUpdateDestroyView.as_view(), name='job-detail'),
    
    # Advanced job search with filtering
    path('search/', JobSearchView.as_view(), name='job-search'),
    
    # Company-specific jobs
    path('company/<int:company_id>/', CompanyJobsView.as_view(), name='company-jobs'),
    
    # Admin-only endpoints
    path('admin/all/', JobAdminListView.as_view(), name='admin-job-list'),
    path('<int:pk>/activation/', JobActivationView.as_view(), name='job-activation'),
]

