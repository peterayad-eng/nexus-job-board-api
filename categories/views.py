from django.shortcuts import render
from rest_framework import generics, permissions
from django.db.models import Count
from .models import Category, Skill
from .serializers import (
    CategorySerializer, CategoryDetailSerializer,
    SkillSerializer, SkillDetailSerializer
)
from users.permissions import IsAdminUserRole

# Create your views here.
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.annotate(job_count=Count('jobs'))
    serializer_class = CategoryDetailSerializer
    permission_classes = [permissions.AllowAny]

class CategoryWithJobsView(generics.ListAPIView):
    queryset = Category.objects.annotate(job_count=Count('jobs')).filter(job_count__gt=0)
    serializer_class = CategoryDetailSerializer
    permission_classes = [permissions.AllowAny]

class SkillListView(generics.ListAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]

class SkillDetailView(generics.RetrieveAPIView):
    queryset = Skill.objects.annotate(job_count=Count('jobs'))
    serializer_class = SkillDetailSerializer
    permission_classes = [permissions.AllowAny]

class SkillWithJobsView(generics.ListAPIView):
    queryset = Skill.objects.annotate(job_count=Count('jobs')).filter(job_count__gt=0)
    serializer_class = SkillDetailSerializer
    permission_classes = [permissions.AllowAny]

# Admin-only endpoints - for managing categories and skills
class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserRole]

class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserRole]

class CategoryDeleteView(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserRole]

class SkillCreateView(generics.CreateAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAdminUserRole]

class SkillUpdateView(generics.UpdateAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAdminUserRole]

class SkillDeleteView(generics.DestroyAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAdminUserRole]

