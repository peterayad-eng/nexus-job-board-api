from django.urls import path
from .views import (
    CompanyListCreateView,
    CompanyRetrieveView,
    CompanyListView
)

urlpatterns = [
    # Companies endpoints
    path('', CompanyListCreateView.as_view(), name='company-list-create'),
    path('<int:pk>/', CompanyRetrieveView.as_view(), name='company-detail'),
    path('summary/', CompanyListView.as_view(), name='company-summary'),
]

