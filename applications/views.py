from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from django.shortcuts import get_object_or_404
from .models import Application
from .serializers import ApplicationSerializer, ApplicationCreateSerializer, ApplicationSummarySerializer
from users.permissions import IsAdminUserRole, IsCompanyManager, IsJobOwnerOrManager
from jobs.models import Job

# Create your views here.
class ApplicationListCreateView(generics.ListCreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Application.objects.select_related(
            'job', 'applicant', 'job__company'
        ) 
        
        # Non-admin users only see their own applications
        if not self.request.user.is_admin_user():
            queryset = queryset.filter(applicant=self.request.user)
            
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ApplicationCreateSerializer
        return ApplicationSerializer 
    
    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

class ApplicationRetrieveView(generics.RetrieveAPIView):
    serializer_class = ApplicationSerializer 
    permission_classes = [permissions.IsAuthenticated] 
    
    def get_queryset(self):
        queryset = Application.objects.select_related('job', 'applicant', 'job__company')
        
        # Non-admin users only see their own applications
        if not self.request.user.is_admin_user():
            queryset = queryset.filter(applicant=self.request.user)
            
        return queryset

class UserApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSummarySerializer 
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Application.objects.filter(
            applicant=self.request.user
        ).select_related('job', 'job__company')

class JobApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSummarySerializer 
    permission_classes = [IsJobOwnerOrManager | IsAdminUserRole]
    
    def get_queryset(self):
        job_id = self.kwargs['job_id'] 
        job = get_object_or_404(Job, id=job_id)

        return Application.objects.filter(
            job_id=job_id
        ).select_related('applicant', 'job', 'job__company')

class JobApplicationCountView(APIView):
    """ Returns the total number of applications for a given job. """ 
    permission_classes = [permissions.AllowAny]

    def get(self, request, job_id):
        count = Application.objects.filter(job_id=job_id).count()
        return Response({"job_id": job_id, "application_count": count})

# Admin-only endpoints
class ApplicationAdminListView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAdminUserRole]
    
    def get_queryset(self):
        return Application.objects.select_related(
            'job', 'applicant', 'job__company'
        )

class ApplicationStatusUpdateView(generics.UpdateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsJobOwnerOrManager | IsAdminUserRole]
    
    def get_queryset(self):
        return Application.objects.select_related('job', 'job__company')
    
# Company manager endpoints
class CompanyApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSummarySerializer
    permission_classes = [IsJobOwnerOrManager | IsAdminUserRole]
    
    def get_queryset(self):
        company_id = self.kwargs['company_id']
        return Application.objects.filter(
            job__company_id=company_id
        ).select_related('applicant', 'job', 'job__company')

