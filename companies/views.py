from django.shortcuts import render
from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .models import Company
from .serializers import (
    CompanySerializer, CompanyCreateSerializer, CompanySummarySerializer,
    DeleteResponseSerializer, AddManagerSerializer, RemoveManagerSerializer,
    ManagerResponseSerializer
)
from users.permissions import IsAdminUserRole, IsCompanyManager, IsOwnerOrAdmin, IsCompanyOwnerOrAdmin
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

# Create your views here.
@extend_schema(
    tags=['companies'],
    summary='List and create companies',
    description='Get a list of all companies or create a new company profile',
    parameters=[
        OpenApiParameter(name='search', description='Search company names and descriptions', required=False),
    ]
)
class CompanyListCreateView(generics.ListCreateAPIView):
    serializer_class = CompanySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'location', 'description']

    def get_queryset(self):
        return Company.objects.annotate(
            manager_count=Count('managers', distinct=True),
            employee_count=Count('employees', distinct=True),
            job_count=Count('jobs', filter=Q(jobs__is_active=True), distinct=True)
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

@extend_schema(
    tags=["companies"],
    summary="Retrieve a single company",
    description="Fetch company details including managers, employees, and jobs count."
)
class CompanyRetrieveView(generics.RetrieveAPIView):
    serializer_class = CompanySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Company.objects.annotate(
            manager_count=Count('managers', distinct=True),
            employee_count=Count('employees', distinct=True),
            job_count=Count('jobs', filter=Q(jobs__is_active=True), distinct=True)
        ).select_related('created_by').prefetch_related('managers')

@extend_schema(
    tags=['companies'],
    summary='Update company profile',
    description='Company managers or admins can update company information',
    examples=[
        OpenApiExample(
            'Company Update',
            value={
                'name': 'Updated Company Name',
                'description': 'Updated company description...',
                'location': 'New York, NY',
                'website': 'https://updated-website.com',
                'contact_email': 'updated@company.com'
            }
        )
    ]
)
class CompanyUpdateView(generics.UpdateAPIView):
    serializer_class = CompanySerializer
    permission_classes = [IsCompanyManager | IsAdminUserRole]

    def get_queryset(self):
        return Company.objects.annotate(
            manager_count=Count('managers', distinct=True),
            employee_count=Count('employees', distinct=True),
            job_count=Count('jobs', filter=Q(jobs__is_active=True), distinct=True)
        ).select_related('created_by').prefetch_related('managers')

@extend_schema(
    tags=['companies'],
    summary='Delete company',
    description='Only company owners or admins can delete a company profile',
    responses={
        204: None,
        200: DeleteResponseSerializer,  
        403: DeleteResponseSerializer,
        404: DeleteResponseSerializer,
    }
)
class CompanyDeleteView(generics.DestroyAPIView):
    serializer_class = CompanySerializer
    permission_classes = [IsCompanyOwnerOrAdmin]

    def get_queryset(self):
        return Company.objects.all()

@extend_schema(
    tags=['companies'],
    summary='List companies (summary)',
    description='Get a lightweight list of companies with basic information',
    parameters=[
        OpenApiParameter(name='search', description='Search company names and locations', required=False),
    ],
    responses={200: CompanySummarySerializer(many=True)}
)
class CompanyListView(generics.ListAPIView):
    serializer_class = CompanySummarySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'location'] 
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Company.objects.annotate(
            manager_count=Count('managers', distinct=True),
            employee_count=Count('employees', distinct=True),
            job_count=Count('jobs', filter=Q(jobs__is_active=True), distinct=True)
        )

# Admin-only endpoints for company management
@extend_schema(
    tags=['companies', 'admin'],
    summary='Admin: List all companies',
    description='Admins can view all companies with full details',
    parameters=[
        OpenApiParameter(name='search', description='Search company names, locations, and descriptions', required=False),
    ]
)
class CompanyAdminListView(generics.ListAPIView):
    serializer_class = CompanySerializer
    permission_classes = [IsAdminUserRole]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'location', 'description']

    def get_queryset(self):
        return Company.objects.annotate(
            manager_count=Count('managers', distinct=True),
            employee_count=Count('employees', distinct=True),
            job_count=Count('jobs', filter=Q(jobs__is_active=True), distinct=True)
        ).select_related('created_by').prefetch_related('managers')

# Company manager management endpoints
@extend_schema(
    tags=['companies'],
    summary='Add manager to company',
    description='Company owners can add other users as managers',
    request=AddManagerSerializer,
    responses={
        200: ManagerResponseSerializer,
        400: ManagerResponseSerializer,
        403: ManagerResponseSerializer,
        404: ManagerResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Add Manager',
            value={'user_id': 5}
        )
    ]
)
class CompanyAddManagerView(APIView):
    permission_classes = [IsCompanyOwnerOrAdmin | IsAdminUserRole]

    def post(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        user_id = request.data.get('user_id')

        if not (company.created_by == request.user or
                company.managers.filter(id=request.user.id).exists() or
                request.user.is_admin_user()):
            return Response(
                {'error': 'You do not have permission to add managers to this company'},
                status=status.HTTP_403_FORBIDDEN
            )

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

@extend_schema(
    tags=['companies'],
    summary='Remove manager from company',
    description='Company owners can remove managers from their company',
    request=RemoveManagerSerializer,
    responses={
        200: ManagerResponseSerializer,
        400: ManagerResponseSerializer,
        403: ManagerResponseSerializer,
        404: ManagerResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Remove Manager',
            value={'user_id': 5}
        )
    ]
)
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

