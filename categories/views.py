from django.shortcuts import render
from rest_framework import generics
from django.db.models import Count
from .models import Category, Skill
from .serializers import (
    CategorySerializer, CategoryDetailSerializer,
    SkillSerializer, SkillDetailSerializer
)

# Create your views here.
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.annotate(job_count=Count('jobs'))
    serializer_class = CategoryDetailSerializer

class CategoryWithJobsView(generics.ListAPIView):
    queryset = Category.objects.annotate(job_count=Count('jobs')).filter(job_count__gt=0)
    serializer_class = CategoryDetailSerializer

class SkillListView(generics.ListAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

class SkillDetailView(generics.RetrieveAPIView):
    queryset = Skill.objects.annotate(job_count=Count('jobs'))
    serializer_class = SkillDetailSerializer

class SkillWithJobsView(generics.ListAPIView):
    queryset = Skill.objects.annotate(job_count=Count('jobs')).filter(job_count__gt=0)
    serializer_class = SkillDetailSerializer

