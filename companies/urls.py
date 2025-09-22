from django.urls import path
from .views import (
    CompanyListCreateView, CompanyRetrieveView, CompanyListView,
    CompanyUpdateView, CompanyDeleteView, CompanyAdminListView,
    CompanyAddManagerView, CompanyRemoveManagerView
)

urlpatterns = [
    # Public endpoints
    path('', CompanyListCreateView.as_view(), name='company-list-create'),
    path('<int:pk>/', CompanyRetrieveView.as_view(), name='company-detail'),
    path('summary/', CompanyListView.as_view(), name='company-summary'),
    
    # Management endpoints
    path('<int:pk>/update/', CompanyUpdateView.as_view(), name='company-update'),
    path('<int:pk>/delete/', CompanyDeleteView.as_view(), name='company-delete'),
    
    # Manager management
    path('<int:pk>/managers/add/', CompanyAddManagerView.as_view(), name='company-add-manager'),
    path('<int:pk>/managers/remove/', CompanyRemoveManagerView.as_view(), name='company-remove-manager'),
    
    # Admin-only endpoints
    path('admin/all/', CompanyAdminListView.as_view(), name='admin-company-list'),
]

