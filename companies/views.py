from django.shortcuts import render
from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .models import Company
from .serializers import CompanySerializer, CompanyCreateSerializer, CompanySummarySerializer
from users.permissions import IsAdminUserRole, IsCompanyManager, IsOwnerOrAdmin, IsCompanyOwnerOrAdmin

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
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Company.objects.annotate(
            manager_count=Count('managers', distinct=True),
            employee_count=Count('employees', distinct=True),
            job_count=Count('jobs', distinct=True)
        ).select_related('created_by').prefetch_related('managers')

class CompanyUpdateView(generics.UpdateAPIView):
    serializer_class = CompanySerializer
    permission_classes = [IsCompanyManager | IsAdminUserRole]

    def get_queryset(self):
        return Company.objects.annotate(
            manager_count=Count('managers', distinct=True),
            employee_count=Count('employees', distinct=True),
            job_count=Count('jobs', distinct=True)
        ).select_related('created_by').prefetch_related('managers')

class CompanyDeleteView(generics.DestroyAPIView):
    serializer_class = CompanySerializer
    permission_classes = [IsCompanyOwnerOrAdmin]

    def get_queryset(self):
        return Company.objects.all()

class CompanyListView(generics.ListAPIView):
    serializer_class = CompanySummarySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'location'] 
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Company.objects.annotate(
            manager_count=Count('managers', distinct=True),
            employee_count=Count('employees', distinct=True),
            job_count=Count('jobs', distinct=True)
        )

# Admin-only endpoints for company management
class CompanyAdminListView(generics.ListAPIView):
    serializer_class = CompanySerializer
    permission_classes = [IsAdminUserRole]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'location', 'description']

    def get_queryset(self):
        return Company.objects.annotate(
            manager_count=Count('managers', distinct=True),
            employee_count=Count('employees', distinct=True),
            job_count=Count('jobs', distinct=True)
        ).select_related('created_by').prefetch_related('managers')

# Company manager management endpoints
class CompanyAddManagerView(APIView):
    permission_classes = [IsCompanyOwnerOrAdmin | IsAdminUserRole]

    def post(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from users.models import User
            user = User.objects.get(id=user_id)
            
            if company.managers.filter(id=user_id).exists():
                return Response({'error': 'User is already a manager'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not user.is_employer():
                return Response({'error': 'Only employer users can be managers'}, status=status.HTTP_400_BAD_REQUEST)
            
            company.managers.add(user)
            return Response({'message': f'{user.username} added as manager'})
            
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class CompanyRemoveManagerView(APIView):
    permission_classes = [IsCompanyOwnerOrAdmin | IsAdminUserRole]

    def post(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from users.models import User
            user = User.objects.get(id=user_id)
            
            if not company.managers.filter(id=user_id).exists():
                return Response({'error': 'User is not a manager'}, status=status.HTTP_400_BAD_REQUEST)
            
            if user == company.created_by:
                return Response({'error': 'Cannot remove company owner from managers'}, status=status.HTTP_400_BAD_REQUEST)
            
            company.managers.remove(user)
            return Response({'message': f'{user.username} removed from managers'})
            
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

