from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView, CategoryWithJobsView,
    SkillListView, SkillDetailView, SkillWithJobsView,
    CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
    SkillCreateView, SkillUpdateView, SkillDeleteView
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
    
    # Admin-only management endpoints
    path('admin/categories/', CategoryCreateView.as_view(), name='admin-category-create'),
    path('admin/categories/<int:pk>/', CategoryUpdateView.as_view(), name='admin-category-update'),
    path('admin/categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='admin-category-delete'),
    
    path('admin/skills/', SkillCreateView.as_view(), name='admin-skill-create'),
    path('admin/skills/<int:pk>/', SkillUpdateView.as_view(), name='admin-skill-update'),
    path('admin/skills/<int:pk>/delete/', SkillDeleteView.as_view(), name='admin-skill-delete'),
]

