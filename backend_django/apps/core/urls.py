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
    
    # Ratings
    path('ratings/', views.RatingListCreateView.as_view(), name='rating-list'),
    path('ratings/<int:pk>/', views.RatingDetailView.as_view(), name='rating-detail'),
    
    # Feedback Flags
    path('feedback-flags/', views.FeedbackFlagListCreateView.as_view(), name='feedback-flag-list'),
    path('feedback-flags/<int:pk>/', views.FeedbackFlagDetailView.as_view(), name='feedback-flag-detail'),
    
    # Notification Types
    path('notification-types/', views.NotificationTypeListCreateView.as_view(), name='notification-type-list'),
    path('notification-types/<int:pk>/', views.NotificationTypeDetailView.as_view(), name='notification-type-detail'),
    
    # Notification Preferences
    path('notification-preferences/', views.NotificationPreferenceListCreateView.as_view(), name='notification-preference-list'),
    path('notification-preferences/<int:pk>/', views.NotificationPreferenceDetailView.as_view(), name='notification-preference-detail'),
    
    # Admin Audit Log
    path('admin-audit-logs/', views.AdminAuditLogListView.as_view(), name='admin-audit-log-list'),
    
    # Search History
    path('search-history/', views.SearchHistoryListCreateView.as_view(), name='search-history-list'),
    
    # App Usage
    path('app-usage/', views.AppUsageListCreateView.as_view(), name='app-usage-list'),
    
    # Usage Analytics
    path('usage-analytics/', views.UsageAnalyticsListCreateView.as_view(), name='usage-analytics-list'),
    
    # Device Preferences
    path('device-preferences/', views.DevicePreferenceListCreateView.as_view(), name='device-preference-list'),
    path('device-preferences/<int:pk>/', views.DevicePreferenceDetailView.as_view(), name='device-preference-detail'),
    
    # App Config
    path('app-config/', views.AppConfigListCreateView.as_view(), name='app-config-list'),
    path('app-config/<str:config_key>/', views.AppConfigDetailView.as_view(), name='app-config-detail'),
    
    # Connectivity Log
    path('connectivity-logs/', views.ConnectivityLogListCreateView.as_view(), name='connectivity-log-list'),
    
    # Dashboard
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
]
