# backend_django/apps/notifications/urls.py
# FIX: Add per-notification /read/ endpoint for single-click read sync

from django.urls import path
from . import views

urlpatterns = [
    path('',               views.NotificationListView.as_view(),    name='notification-list'),
    path('<int:pk>/',      views.NotificationDetailView.as_view(),  name='notification-detail'),
    path('read-all/',      views.MarkAllReadView.as_view(),         name='notification-read-all'),

    # FIX: Per-notification mark-as-read — called when user taps a single notification
    path('<int:pk>/read/', views.MarkOneReadView.as_view(),         name='notification-read-one'),
]
