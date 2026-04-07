from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Department, MapMarker, MapLabel, Rating, FeedbackFlag,
    NotificationType, NotificationPreference, AdminAuditLog,
    SearchHistory, AppUsage, UsageAnalytics, DevicePreference,
    AppConfig, ConnectivityLog
)
from .serializers import (
    DepartmentSerializer, MapMarkerSerializer, MapLabelSerializer,
    RatingSerializer, FeedbackFlagSerializer, NotificationTypeSerializer,
    NotificationPreferenceSerializer, AdminAuditLogSerializer,
    SearchHistorySerializer, AppUsageSerializer, UsageAnalyticsSerializer,
    DevicePreferenceSerializer, AppConfigSerializer, ConnectivityLogSerializer
)


# Department Views
class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# Map Marker Views
class MapMarkerListCreateView(generics.ListCreateAPIView):
    queryset = MapMarker.objects.filter(is_active=True)
    serializer_class = MapMarkerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['marker_type', 'facility']
    search_fields = ['name']


class MapMarkerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MapMarker.objects.all()
    serializer_class = MapMarkerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# Map Label Views
class MapLabelListCreateView(generics.ListCreateAPIView):
    queryset = MapLabel.objects.filter(is_active=True)
    serializer_class = MapLabelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class MapLabelDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MapLabel.objects.all()
    serializer_class = MapLabelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# Rating Views
class RatingListCreateView(generics.ListCreateAPIView):
    queryset = Rating.objects.filter(is_active=True)
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'facility', 'room']


class RatingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# Feedback Flag Views
class FeedbackFlagListCreateView(generics.ListCreateAPIView):
    queryset = FeedbackFlag.objects.all()
    serializer_class = FeedbackFlagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']


class FeedbackFlagDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FeedbackFlag.objects.all()
    serializer_class = FeedbackFlagSerializer
    permission_classes = [IsAuthenticated]


# Notification Type Views
class NotificationTypeListCreateView(generics.ListCreateAPIView):
    queryset = NotificationType.objects.filter(is_active=True)
    serializer_class = NotificationTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class NotificationTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NotificationType.objects.all()
    serializer_class = NotificationTypeSerializer
    permission_classes = [IsAuthenticated]


# Notification Preference Views
class NotificationPreferenceListCreateView(generics.ListCreateAPIView):
    queryset = NotificationPreference.objects.all()
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)


class NotificationPreferenceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NotificationPreference.objects.all()
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]


# Admin Audit Log Views
class AdminAuditLogListView(generics.ListAPIView):
    queryset = AdminAuditLog.objects.all()
    serializer_class = AdminAuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['action', 'entity_type', 'user']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


# Search History Views
class SearchHistoryListCreateView(generics.ListCreateAPIView):
    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()


# App Usage Views
class AppUsageListCreateView(generics.ListCreateAPIView):
    queryset = AppUsage.objects.all()
    serializer_class = AppUsageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AppUsage.objects.filter(user=self.request.user)


# Usage Analytics Views
class UsageAnalyticsListCreateView(generics.ListCreateAPIView):
    queryset = UsageAnalytics.objects.all()
    serializer_class = UsageAnalyticsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event_type', 'screen_name']

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()


# Device Preference Views
class DevicePreferenceListCreateView(generics.ListCreateAPIView):
    queryset = DevicePreference.objects.all()
    serializer_class = DevicePreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DevicePreference.objects.filter(user=self.request.user)


class DevicePreferenceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DevicePreference.objects.all()
    serializer_class = DevicePreferenceSerializer
    permission_classes = [IsAuthenticated]


# App Config Views
class AppConfigListCreateView(generics.ListCreateAPIView):
    queryset = AppConfig.objects.all()
    serializer_class = AppConfigSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class AppConfigDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AppConfig.objects.all()
    serializer_class = AppConfigSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'config_key'


# Connectivity Log Views
class ConnectivityLogListCreateView(generics.ListCreateAPIView):
    queryset = ConnectivityLog.objects.all()
    serializer_class = ConnectivityLogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()


# Dashboard Stats
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Return dashboard statistics for admin panel"""
    from apps.facilities.models import Facility
    from apps.rooms.models import Room
    from apps.users.models import AdminUser
    from apps.notifications.models import Notification
    from apps.feedback.models import Feedback
    
    stats = {
        'total_facilities': Facility.objects.filter(is_deleted=False).count(),
        'total_rooms': Room.objects.filter(is_deleted=False).count(),
        'total_users': AdminUser.objects.filter(is_active=True).count(),
        'total_notifications': Notification.objects.count(),
        'unread_notifications': Notification.objects.filter(is_read=False).count(),
        'total_feedback': Feedback.objects.count(),
        'recent_ratings': Rating.objects.filter(is_active=True).count(),
        'audit_logs_count': AdminAuditLog.objects.count(),
    }
    return Response(stats)
