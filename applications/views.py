from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from django.shortcuts import get_object_or_404
from .models import Application
from .serializers import ApplicationSerializer, ApplicationCreateSerializer, ApplicationSummarySerializer, ApplicationStatusSerializer
from users.permissions import IsAdminUserRole, IsCompanyManager, IsJobOwnerOrManager
from jobs.models import Job
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

# Create your views here.
@extend_schema(
    tags=['applications'],
    summary='List and create applications',
    description='Users can view their own applications and apply to jobs',
    examples=[
        OpenApiExample(
            'Application Creation',
            value={
                'job': 1,
                'cover_letter': 'I am very interested in this position...',
                'resume': 'path/to/resume.pdf'
            }
        )
    ]
)
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

@extend_schema(
    tags=['applications'],
    summary='Retrieve a specific application',
    description='Authenticated users can retrieve their own applications. Admins can retrieve any application.',
    responses={200: ApplicationSerializer}
)
class ApplicationRetrieveView(generics.RetrieveAPIView):
    serializer_class = ApplicationSerializer 
    permission_classes = [permissions.IsAuthenticated] 
    
    def get_queryset(self):
        queryset = Application.objects.select_related('job', 'applicant', 'job__company')
        
        # Non-admin users only see their own applications
        if not self.request.user.is_admin_user():
            queryset = queryset.filter(applicant=self.request.user)
            
        return queryset

@extend_schema(
    tags=['applications'],
    summary="Get user's applications",
    description='Retrieve all job applications for the currently authenticated user',
    parameters=[
        OpenApiParameter(
            name='status', 
            description='Filter applications by status',
            required=False,
            enum=['applied', 'reviewed', 'interview', 'rejected', 'accepted']
        ),
    ],
    responses={200: ApplicationSummarySerializer(many=True)}
)
class UserApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSummarySerializer 
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Application.objects.filter(
            applicant=self.request.user
        ).select_related('job', 'job__company')

@extend_schema(
    tags=['applications'],
    summary='Get job applications',
    description='Job owners and company managers can view applications for their jobs',
    parameters=[
        OpenApiParameter(name='status', description='Filter by application status', required=False),
    ]
)
class JobApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSummarySerializer 
    permission_classes = [IsJobOwnerOrManager | IsAdminUserRole]
    
    def get_queryset(self):
        job_id = self.kwargs['job_id'] 
        job = get_object_or_404(Job, id=job_id)

        return Application.objects.filter(
            job_id=job_id
        ).select_related('applicant', 'job', 'job__company')

@extend_schema(
    tags=['applications'],
    summary='Get application count for a job',
    description='Returns the total number of applications for the given job ID',
    responses={200: OpenApiExample(
        'Application Count Example',
        value={"job_id": 5, "application_count": 12}
    )}
)
class JobApplicationCountView(APIView):
    """ Returns the total number of applications for a given job. """ 
    permission_classes = [permissions.AllowAny]

    def get(self, request, job_id):
        count = Application.objects.filter(job_id=job_id).count()
        return Response({"job_id": job_id, "application_count": count})

# Admin-only endpoints
@extend_schema(
    tags=['applications', 'admin'],
    summary='Admin: List all applications',
    description='Admins can view all job applications in the system',
    responses={200: ApplicationSerializer}
)
class ApplicationAdminListView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAdminUserRole]
    
    def get_queryset(self):
        return Application.objects.select_related(
            'job', 'applicant', 'job__company'
        )

@extend_schema(
    tags=['applications'],
    summary='Update application status',
    description='Job owners and company managers can update the status of applications',
    request=ApplicationStatusSerializer,
    examples=[
        OpenApiExample(
            'Status Update Example',
            value={
                'status': 'interview',
                'notes': 'Scheduled interview for next Monday at 2 PM'
            }
        )
    ],
    responses={200: ApplicationSerializer}
)
class ApplicationStatusUpdateView(generics.UpdateAPIView):
    serializer_class = ApplicationStatusSerializer
    permission_classes = [IsJobOwnerOrManager | IsAdminUserRole]
    
    def get_queryset(self):
        return Application.objects.select_related('job', 'job__company')
    
# Company manager endpoints
@extend_schema(
    tags=['applications'],
    summary='Get company applications',
    description='Company managers can view all applications for jobs posted by their company',
    parameters=[
        OpenApiParameter(name='company_id', description='Company ID', required=True, type=int),
        OpenApiParameter(
            name='status', 
            description='Filter by application status',
            required=False,
            enum=['applied', 'reviewed', 'interview', 'rejected', 'accepted']
        ),
    ],
    responses={200: ApplicationSummarySerializer(many=True)}
)
class CompanyApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSummarySerializer
    permission_classes = [IsJobOwnerOrManager | IsAdminUserRole]
    
    def get_queryset(self):
        company_id = self.kwargs['company_id']
        return Application.objects.filter(
            job__company_id=company_id
        ).select_related('applicant', 'job', 'job__company')

