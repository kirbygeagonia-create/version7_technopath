from django.urls import path
from . import views

urlpatterns = [
    path('nodes/', views.NavigationNodeListView.as_view(), name='node-list'),
    path('nodes/<int:pk>/', views.NavigationNodeDetailView.as_view(), name='node-detail'),
    path('edges/', views.NavigationEdgeListView.as_view(), name='edge-list'),
    path('edges/<int:pk>/', views.NavigationEdgeDetailView.as_view(), name='edge-detail'),
]
