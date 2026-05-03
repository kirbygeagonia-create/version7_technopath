from django.urls import path
from . import views

urlpatterns = [
    # Departments
    path('departments/', views.DepartmentListCreateView.as_view(), name='department-list'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department-detail'),
    
    # Map Markers
    path('map-markers/', views.MapMarkerListCreateView.as_view(), name='map-marker-list'),
    path('map-markers/<int:pk>/', views.MapMarkerDetailView.as_view(), name='map-marker-detail'),
    
    # Map Labels
    path('map-labels/', views.MapLabelListCreateView.as_view(), name='map-label-list'),
    path('map-labels/<int:pk>/', views.MapLabelDetailView.as_view(), name='map-label-detail'),
    

    
    # Notification Types
    path('notification-types/', views.NotificationTypeListCreateView.as_view(), name='notification-type-list'),
    path('notification-types/<int:pk>/', views.NotificationTypeDetailView.as_view(), name='notification-type-detail'),
    
    # Notification Preferences
    path('notification-preferences/', views.NotificationPreferenceListCreateView.as_view(), name='notification-preference-list'),
    path('notification-preferences/<int:pk>/', views.NotificationPreferenceDetailView.as_view(), name='notification-preference-detail'),
    
    # Search History
    path('search-history/', views.SearchHistoryListCreateView.as_view(), name='search-history-list'),
    
    # App Config
    path('app-config/', views.AppConfigListCreateView.as_view(), name='app-config-list'),
    path('app-config/<str:config_key>/', views.AppConfigDetailView.as_view(), name='app-config-detail'),
    
    # Dashboard
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
    
    # App Ratings
    path('ratings/', views.AppRatingView.as_view(), name='app-rating'),
]
