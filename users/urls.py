from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView
from .views import (
    RegisterView, LoginView, UserProfileView,
    UserPasswordUpdateView, RefreshTokenView,
    UserListView, UserDetailView, UserSearchView,
    UserStatsView, UserActivationView
)

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token-refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
    
    # User profile endpoints
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/password/', UserPasswordUpdateView.as_view(), name='user-password-update'),
    
    # Admin-only endpoints
    path('admin/users/', UserListView.as_view(), name='admin-user-list'),
    path('admin/users/<int:pk>/', UserDetailView.as_view(), name='admin-user-detail'),
    path('admin/users/search/', UserSearchView.as_view(), name='admin-user-search'),
    path('admin/stats/', UserStatsView.as_view(), name='admin-user-stats'),
    path('admin/users/<int:pk>/activation/', UserActivationView.as_view(), name='admin-user-activation'),
]

