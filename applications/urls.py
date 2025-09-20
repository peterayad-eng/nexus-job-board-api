from django.urls import path
from .views import (
    ApplicationListCreateView,
    ApplicationRetrieveView,
    UserApplicationsView,
    JobApplicationsView,
    JobApplicationCountView
)

urlpatterns = [
    # Main applications endpoint - list all applications and create new ones
    path('', ApplicationListCreateView.as_view(), name='application-list-create'),
    
    # Individual application details
    path('<int:pk>/', ApplicationRetrieveView.as_view(), name='application-detail'),
    
    # User's personal applications
    path('my-applications/', UserApplicationsView.as_view(), name='user-applications'),
    
    # Applications for a specific job
    path('job/<int:job_id>/', JobApplicationsView.as_view(), name='job-applications'),
    
    # Application count for a specific job
    path('job/<int:job_id>/count/', JobApplicationCountView.as_view(), name='job-application-count'),
]

