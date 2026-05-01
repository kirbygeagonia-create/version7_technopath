# backend_django/apps/notifications/urls.py
# FIX: Add per-notification /read/ endpoint for single-click read sync

from django.urls import path
from .views import (NotificationListView, NotificationDetailView, MarkAllReadView, 
                    MarkOneReadView, SendNotificationView, UnreadCountView)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('send/', SendNotificationView.as_view(), name='notification-send'),
    path('unread-count/', UnreadCountView.as_view(), name='notification-unread-count'),
    path('read-all/', MarkAllReadView.as_view(), name='notification-read-all'),
    # FIX: Per-notification mark-as-read — called when user taps a single notification
    path('<int:pk>/read/', MarkOneReadView.as_view(), name='notification-read-one'),
]
