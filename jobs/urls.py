from django.urls import path
from .views import (
    JobListCreateView,
    JobRetrieveUpdateDestroyView,
    JobSearchView,
    CompanyJobsView
)

urlpatterns = [
    # Main jobs endpoints
    path('', JobListCreateView.as_view(), name='job-list-create'),
    path('<int:pk>/', JobRetrieveUpdateDestroyView.as_view(), name='job-detail'),
    path('search/', JobSearchView.as_view(), name='job-search'),
    
    # Company-specific jobs
    path('company/<int:company_id>/', CompanyJobsView.as_view(), name='company-jobs'),
]

