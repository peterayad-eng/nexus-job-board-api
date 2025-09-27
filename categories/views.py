from django.shortcuts import render
from rest_framework import generics, permissions
from django.db.models import Count
from .models import Category, Skill
from .serializers import (
    CategorySerializer, CategoryDetailSerializer,
    SkillSerializer, SkillDetailSerializer
)
from users.permissions import IsAdminUserRole
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

# Create your views here.
@extend_schema(
    tags=['categories'],
    summary='List categories',
    description='Get a list of all job categories'
)
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

@extend_schema(
    tags=['categories'],
    summary='Get category details',
    description='Retrieve detailed information about a specific category including job count'
)
class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.annotate(job_count=Count('jobs'))
    serializer_class = CategoryDetailSerializer
    permission_classes = [permissions.AllowAny]

@extend_schema(
    tags=['categories'],
    summary='List categories with jobs',
    description='Get only categories that have active job postings'
)
class CategoryWithJobsView(generics.ListAPIView):
    queryset = Category.objects.annotate(job_count=Count('jobs')).filter(job_count__gt=0)
    serializer_class = CategoryDetailSerializer
    permission_classes = [permissions.AllowAny]

@extend_schema(
    tags=['skills'],
    summary='List skills',
    description='Get a list of all job-related skills'
)
class SkillListView(generics.ListAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]

@extend_schema(
    tags=['skills'],
    summary='Get skill details',
    description='Retrieve detailed information about a specific skill including job count'
)
class SkillDetailView(generics.RetrieveAPIView):
    queryset = Skill.objects.annotate(job_count=Count('jobs'))
    serializer_class = SkillDetailSerializer
    permission_classes = [permissions.AllowAny]

@extend_schema(
    tags=['skills'],
    summary='List skills with jobs',
    description='Get only skills that are required by active job postings'
)
class SkillWithJobsView(generics.ListAPIView):
    queryset = Skill.objects.annotate(job_count=Count('jobs')).filter(job_count__gt=0)
    serializer_class = SkillDetailSerializer
    permission_classes = [permissions.AllowAny]

# Admin-only endpoints - for managing categories and skills
@extend_schema(
    tags=['categories', 'admin'],
    summary='Admin: Create category',
    description='Admins can create new job categories'
)
class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserRole]

@extend_schema(
    tags=['categories', 'admin'],
    summary='Admin: Update category',
    description='Admins can update category information',
    examples=[
        {"name": "Updated Category", "description": "Updated description..."}
    ]
)
class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserRole]

@extend_schema(
    tags=['categories', 'admin'],
    summary='Admin: Delete category',
    description='Admins can delete a category',
    responses={
        204: OpenApiExample(
            'Delete Success',
            value=None,
            description='Category deleted successfully (no content)'
        )
    }
)
class CategoryDeleteView(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserRole]

@extend_schema(
    tags=['skills', 'admin'],
    summary='Admin: Create skill',
    description='Admins can create new job skills'
)
class SkillCreateView(generics.CreateAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAdminUserRole]

@extend_schema(
    tags=['skills', 'admin'],
    summary='Admin: Update skill',
    description='Admins can update skill information'
)
class SkillUpdateView(generics.UpdateAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAdminUserRole]

@extend_schema(
    tags=['skills', 'admin'],
    summary='Admin: Delete skill',
    description='Admins can delete a skill',
    responses={
        200: OpenApiExample(
            'Delete Success',
            value={'message': 'Skill deleted successfully'}
        )
    }
)
class SkillDeleteView(generics.DestroyAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAdminUserRole]

