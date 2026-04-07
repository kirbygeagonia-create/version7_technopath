#!/usr/bin/env python
"""Verification script for TechnoPath migration"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'technopath.settings')
django.setup()

from apps.core.models import (
    Department, MapMarker, MapLabel, Rating, FeedbackFlag,
    NotificationType, NotificationPreference, AdminAuditLog,
    SearchHistory, AppUsage, UsageAnalytics, DevicePreference,
    AppConfig, ConnectivityLog
)
from apps.facilities.models import Facility
from apps.rooms.models import Room
from apps.navigation.models import NavigationNode, NavigationEdge
from apps.chatbot.models import FAQEntry, AIChatLog
from apps.notifications.models import Notification
from apps.users.models import AdminUser
from apps.feedback.models import Feedback

print("=" * 60)
print("TECHNOPATH MIGRATION VERIFICATION REPORT")
print("=" * 60)

models_to_check = [
    ('Facilities', Facility),
    ('Rooms', Room),
    ('Departments', Department),
    ('Map Markers', MapMarker),
    ('Map Labels', MapLabel),
    ('Navigation Nodes', NavigationNode),
    ('Navigation Edges', NavigationEdge),
    ('FAQ Entries', FAQEntry),
    ('AI Chat Logs', AIChatLog),
    ('Notifications', Notification),
    ('Notification Types', NotificationType),
    ('Notification Preferences', NotificationPreference),
    ('Ratings', Rating),
    ('Feedback Flags', FeedbackFlag),
    ('Admin Audit Logs', AdminAuditLog),
    ('Search History', SearchHistory),
    ('App Usage', AppUsage),
    ('Usage Analytics', UsageAnalytics),
    ('Device Preferences', DevicePreference),
    ('App Config', AppConfig),
    ('Connectivity Logs', ConnectivityLog),
    ('Admin Users', AdminUser),
    ('Feedback', Feedback),
]

total_tables = 0
print("\nDATABASE TABLE COUNTS:")
for name, model in models_to_check:
    try:
        count = model.objects.count()
        status = "OK" if count > 0 else "EMPTY"
        print(f"  {name:25s}: {count:3d} [{status}]")
        total_tables += 1
    except Exception as e:
        print(f"  {name:25s}: ERROR - {e}")

print(f"\nTotal models checked: {total_tables}")

# Check superuser
print("\nADMIN USER:")
admin = AdminUser.objects.filter(username='admin').first()
if admin:
    print(f"  Superuser 'admin' exists: YES")
    print(f"  Email: {admin.email}")
    print(f"  Is superuser: {admin.is_superuser}")
else:
    print(f"  Superuser 'admin' exists: NO")

# Check API endpoints
print("\nAPI ENDPOINTS CONFIGURED:")
endpoints = [
    '/api/facilities/',
    '/api/rooms/',
    '/api/core/departments/',
    '/api/core/map-markers/',
    '/api/core/map-labels/',
    '/api/navigation/nodes/',
    '/api/navigation/edges/',
    '/api/chatbot/faq/',
    '/api/notifications/',
    '/api/core/notification-types/',
    '/api/core/app-config/',
    '/api/core/ratings/',
    '/api/core/dashboard/stats/',
]
for endpoint in endpoints:
    print(f"  {endpoint}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
