from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView, CategoryWithJobsView,
    SkillListView, SkillDetailView, SkillWithJobsView
)

urlpatterns = [
    # Category endpoints
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/with-jobs/', CategoryWithJobsView.as_view(), name='category-with-jobs'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    
    # Skill endpoints
    path('skills/', SkillListView.as_view(), name='skill-list'),
    path('skills/with-jobs/', SkillWithJobsView.as_view(), name='skill-with-jobs'),
    path('skills/<int:pk>/', SkillDetailView.as_view(), name='skill-detail'),
]

