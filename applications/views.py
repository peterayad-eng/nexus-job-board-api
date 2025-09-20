from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from .models import Application
from .serializers import ApplicationSerializer, ApplicationCreateSerializer, ApplicationSummarySerializer

# Create your views here.
class ApplicationListCreateView(generics.ListCreateAPIView):
    serializer_class = ApplicationSerializer
    
    def get_queryset(self):
        return Application.objects.select_related(
            'job', 'applicant', 'job__company'
        )
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ApplicationCreateSerializer
        return ApplicationSerializer
    
    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

class ApplicationRetrieveView(generics.RetrieveAPIView):
    serializer_class = ApplicationSerializer
    queryset = Application.objects.select_related('job', 'applicant', 'job__company')

class UserApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSummarySerializer
    
    def get_queryset(self):
        return Application.objects.filter(
            applicant=self.request.user
        ).select_related('job', 'job__company')

class JobApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSummarySerializer
    
    def get_queryset(self):
        job_id = self.kwargs['job_id']
        return Application.objects.filter(
            job_id=job_id
        ).select_related('applicant', 'job', 'job__company')

class JobApplicationCountView(APIView):
    """
    Returns the total number of applications for a given job.
    """
    def get(self, request, job_id):
        count = Application.objects.filter(job_id=job_id).count()
        return Response({"job_id": job_id, "application_count": count})

