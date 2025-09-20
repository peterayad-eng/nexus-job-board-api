from django.shortcuts import render
from rest_framework import generics, permissions, filters
from django.db.models import Count
from .models import Company
from .serializers import CompanySerializer, CompanyCreateSerializer, CompanySummarySerializer

# Create your views here.
class CompanyListCreateView(generics.ListCreateAPIView):
    serializer_class = CompanySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'location', 'description']

    def get_queryset(self):
        return Company.objects.annotate(
            manager_count=Count('managers', distinct=True),
            employee_count=Count('employees', distinct=True),
            job_count=Count('jobs', distinct=True)
        ).select_related('created_by').prefetch_related('managers')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CompanyCreateSerializer
        return CompanySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        company = serializer.save(created_by=self.request.user)
        # Add the creator as a manager by default
        company.managers.add(self.request.user)

class CompanyRetrieveView(generics.RetrieveAPIView):
    serializer_class = CompanySerializer

    def get_queryset(self):
        return Company.objects.annotate(
            manager_count=Count('managers', distinct=True),
            employee_count=Count('employees', distinct=True),
            job_count=Count('jobs', distinct=True)
        ).select_related('created_by').prefetch_related('managers')

class CompanyListView(generics.ListAPIView):
    serializer_class = CompanySummarySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'location']

    def get_queryset(self):
        return Company.objects.annotate(
            manager_count=Count('managers', distinct=True),
            employee_count=Count('employees', distinct=True),
            job_count=Count('jobs', distinct=True)
        )

