from django.shortcuts import render
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import Job
from .serializers import JobSerializer, JobCreateSerializer, JobUpdateSerializer, JobSummarySerializer
from .filters import JobFilter
from users.permissions import IsAdminUserRole, IsCompanyManager

# Create your views here.
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

class CompanyJobsView(generics.ListAPIView):
    serializer_class = JobSummarySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        return Job.objects.filter(company_id=company_id, is_active=True).select_related(
            'company'
        ).annotate(application_count=Count('applications'))

# Admin-only endpoints
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

