from django.shortcuts import render
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import Job
from .serializers import JobSerializer, JobCreateSerializer, JobUpdateSerializer, JobSummarySerializer
from .filters import JobFilter
from users.permissions import IsAdminUserRole, IsCompanyManager
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

# Create your views here.
@extend_schema(
    tags=['jobs'],
    summary='List and create jobs',
    description='Get a paginated list of active jobs or create a new job posting',
    parameters=[
        OpenApiParameter(name='search', description='Search in title, description, company name', required=False),
        OpenApiParameter(name='location', description='Filter by location', required=False),
        OpenApiParameter(name='job_type', description='Filter by job type', required=False),
        OpenApiParameter(name='company', description='Filter by company ID', required=False),
    ]
)
class JobListCreateView(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = JobFilter
    search_fields = ['title', 'description', 'location', 'company__name']
    ordering_fields = ['created_at', 'salary_range', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Job.objects.filter(is_active=True).select_related(
            'company', 'posted_by'
        ).prefetch_related(
            'categories', 'required_skills'
        ).annotate(application_count=Count('applications'))

        # Add owner annotation for authenticated users
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_owner=Q(posted_by=self.request.user)
            )

        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobCreateSerializer
        return JobSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

@extend_schema(
    tags=['jobs'],
    summary='Retrieve, update or delete job',
    description='Job owners, company managers and admins can update/delete jobs'
)
class JobRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobSerializer

    def get_queryset(self):
        queryset = Job.objects.select_related(
            'company', 'posted_by'
        ).prefetch_related(
            'categories', 'required_skills'
        ).annotate(application_count=Count('applications'))

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_owner=Q(posted_by=self.request.user)
            )

        return queryset

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return JobUpdateSerializer
        return JobSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        
        # Additional permission checks for write operations
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            # Allow job owner
            if obj.posted_by == request.user:
                return
                
            # Allow company managers
            if obj.company.managers.filter(id=request.user.id).exists():
                return
                
            # Allow admins
            if request.user.is_admin_user():
                return
                
            # Deny everyone else
            self.permission_denied(request, message="You do not have permission to perform this action.")

@extend_schema(
    tags=['jobs'],
    summary='Search jobs',
    description='Advanced job search with multiple filter criteria',
    parameters=[
        OpenApiParameter(name='title', description='Job title contains', required=False),
        OpenApiParameter(name='categories', description='Category names', required=False),
        OpenApiParameter(name='skills', description='Skill names', required=False),
    ]
)
class JobSearchView(generics.ListAPIView):
    serializer_class = JobSummarySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = JobFilter
    search_fields = ['title', 'description', 'location', 'company__name', 'categories__name']
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Job.objects.filter(is_active=True).select_related(
            'company'
        ).prefetch_related(
            'categories'
        ).annotate(application_count=Count('applications'))

@extend_schema(
    tags=['jobs'],
    summary='List jobs for a specific company',
    description='Retrieve active job postings for a given company',
    parameters=[
        OpenApiParameter(name='company_id', description='ID of the company', required=True, type=int),
    ]
)
class CompanyJobsView(generics.ListAPIView):
    serializer_class = JobSummarySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        return Job.objects.filter(company_id=company_id, is_active=True).select_related(
            'company'
        ).annotate(application_count=Count('applications'))

# Admin-only endpoints
@extend_schema(
    tags=['jobs', 'admin'],
    summary='Admin: List all jobs',
    description='Admins can list all jobs, regardless of status',
)
class JobAdminListView(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAdminUserRole]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = JobFilter
    search_fields = ['title', 'description', 'location', 'company__name']

    def get_queryset(self):
        return Job.objects.select_related(
            'company', 'posted_by'
        ).prefetch_related(
            'categories', 'required_skills'
        ).annotate(application_count=Count('applications'))

@extend_schema(
    tags=['jobs', 'admin'],
    summary='Activate/deactivate job',
    description='Toggle job activation status. Only admins or company managers can perform this action.',
    responses={
        200: OpenApiExample(
            'Job Activation Example',
            value={
                'message': 'Job "Backend Developer" has been activated',
                'is_active': True
            }
        )
    }
)
class JobActivationView(generics.UpdateAPIView):
    serializer_class = JobUpdateSerializer
    permission_classes = [IsCompanyManager | IsAdminUserRole]
    http_method_names = ['patch']

    def get_queryset(self):
        return Job.objects.select_related('company')

    def patch(self, request, *args, **kwargs):
        job = self.get_object()
        job.is_active = not job.is_active
        job.save()
        action = "activated" if job.is_active else "deactivated"
        return Response({
            'message': f'Job "{job.title}" has been {action}',
            'is_active': job.is_active
        })

