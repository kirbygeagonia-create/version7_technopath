from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    head_user = models.ForeignKey('users.AdminUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'departments'

    def __str__(self):
        return self.name


class MapMarker(models.Model):
    MARKER_TYPES = [
        ('facility', 'Facility'),
        ('room', 'Room'),
        ('entrance', 'Entrance'),
        ('waypoint', 'Waypoint'),
        ('amenity', 'Amenity'),
    ]
    
    facility = models.ForeignKey('facilities.Facility', on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey('rooms.Room', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    x_position = models.FloatField()
    y_position = models.FloatField()
    marker_type = models.CharField(max_length=20, choices=MARKER_TYPES, default='facility')
    icon_name = models.CharField(max_length=100, default='location_on')
    color_hex = models.CharField(max_length=7, default='#FF9800')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'map_markers'

    def __str__(self):
        return self.name


class MapLabel(models.Model):
    label_text = models.CharField(max_length=200)
    x_position = models.FloatField()
    y_position = models.FloatField()
    font_size = models.IntegerField(default=14)
    color_hex = models.CharField(max_length=7, default='#000000')
    rotation = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'map_labels'

    def __str__(self):
        return self.label_text


class Rating(models.Model):
    CATEGORIES = [
        ('general', 'General'),
        ('facility', 'Facility'),
        ('room', 'Room'),
        ('navigation', 'Navigation'),
        ('app', 'App Experience'),
    ]
    
    user = models.ForeignKey('users.AdminUser', on_delete=models.SET_NULL, null=True, blank=True)
    facility = models.ForeignKey('facilities.Facility', on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey('rooms.Room', on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORIES, default='general')
    is_anonymous = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ratings'

    def __str__(self):
        return f"{self.rating} stars - {self.category}"


class FeedbackFlag(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    user = models.ForeignKey('users.AdminUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='flagged_feedback')
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    resolved_by = models.ForeignKey('users.AdminUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_flags')
    resolved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'feedback_flags'

    def __str__(self):
        return f"Flag on rating {self.rating_id} - {self.status}"


class NotificationType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon_name = models.CharField(max_length=100, default='notifications')
    color_hex = models.CharField(max_length=7, default='#FF9800')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification_types'

    def __str__(self):
        return self.name


class NotificationPreference(models.Model):
    user = models.ForeignKey('users.AdminUser', on_delete=models.CASCADE)
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification_preferences'
        unique_together = ['user', 'notification_type']

    def __str__(self):
        return f"{self.user.username} - {self.notification_type.name}"


class AdminAuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('SOFT_DELETE', 'Soft Delete'),
        ('RESTORE', 'Restore'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
    ]
    
    user = models.ForeignKey('users.AdminUser', on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=50)
    entity_id = models.IntegerField(blank=True, null=True)
    old_values = models.JSONField(blank=True, null=True)
    new_values = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_audit_log'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} {self.entity_type} by {self.user.username}"


class SearchHistory(models.Model):
    user = models.ForeignKey('users.AdminUser', on_delete=models.SET_NULL, null=True, blank=True)
    query = models.CharField(max_length=500)
    results_count = models.IntegerField(default=0)
    was_clicked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'search_history'
        ordering = ['-created_at']

    def __str__(self):
        return f"Search: {self.query}"


class AppUsage(models.Model):
    user = models.ForeignKey('users.AdminUser', on_delete=models.CASCADE, null=True, blank=True)
    session_date = models.DateField()
    session_duration = models.IntegerField(default=0)  # in seconds
    screen_views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'app_usage'

    def __str__(self):
        return f"Usage on {self.session_date}"


class UsageAnalytics(models.Model):
    EVENT_TYPES = [
        ('screen_view', 'Screen View'),
        ('search', 'Search'),
        ('navigation', 'Navigation'),
        ('rating', 'Rating'),
        ('feedback', 'Feedback'),
        ('share', 'Share'),
        ('notification_open', 'Notification Open'),
    ]
    
    user = models.ForeignKey('users.AdminUser', on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    event_data = models.JSONField(blank=True, null=True)
    screen_name = models.CharField(max_length=100, blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'usage_analytics'

    def __str__(self):
        return f"{self.event_type} - {self.screen_name}"


class DevicePreference(models.Model):
    user = models.ForeignKey('users.AdminUser', on_delete=models.SET_NULL, null=True, blank=True)
    device_id = models.CharField(max_length=200)
    dark_mode = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default='en')
    font_scale = models.FloatField(default=1.0)
    high_contrast = models.BooleanField(default=False)
    reduce_animations = models.BooleanField(default=False)
    last_sync = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'device_preferences'

    def __str__(self):
        return f"Preferences for {self.device_id}"


class AppConfig(models.Model):
    config_key = models.CharField(max_length=100, unique=True)
    config_value = models.TextField()
    description = models.TextField(blank=True, null=True)
    updated_by = models.ForeignKey('users.AdminUser', on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'app_config'

    def __str__(self):
        return self.config_key


class ConnectivityLog(models.Model):
    user = models.ForeignKey('users.AdminUser', on_delete=models.SET_NULL, null=True, blank=True)
    is_online = models.BooleanField()
    connection_type = models.CharField(max_length=50, blank=True, null=True)
    latency_ms = models.IntegerField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'connectivity_log'

    def __str__(self):
        return f"Connectivity: {'Online' if self.is_online else 'Offline'}"
