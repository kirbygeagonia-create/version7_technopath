from rest_framework import serializers
from .models import (
    Department, MapMarker, MapLabel, Rating, FeedbackFlag,
    NotificationType, NotificationPreference, AdminAuditLog,
    SearchHistory, AppUsage, UsageAnalytics, DevicePreference,
    AppConfig, ConnectivityLog
)


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class MapMarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapMarker
        fields = '__all__'


class MapLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapLabel
        fields = '__all__'


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'


class FeedbackFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackFlag
        fields = '__all__'


class NotificationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationType
        fields = '__all__'


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = '__all__'


class AdminAuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AdminAuditLog
        fields = '__all__'


class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = '__all__'


class AppUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUsage
        fields = '__all__'


class UsageAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageAnalytics
        fields = '__all__'


class DevicePreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DevicePreference
        fields = '__all__'


class AppConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppConfig
        fields = '__all__'


class ConnectivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectivityLog
        fields = '__all__'
