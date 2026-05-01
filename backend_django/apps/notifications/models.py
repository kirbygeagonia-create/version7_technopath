from django.db import models


class Notification(models.Model):

    TYPE_CHOICES = [
        ('announcement',        'Department Announcement'),
        ('info',                'General Info'),
        ('emergency',           'Emergency'),
        ('facility_update',     'Facility Update'),
        ('room_update',         'Room/Classroom Update'),
        ('system_maintenance',  'System Maintenance'),
        ('app_update',          'App Update'),
    ]

    title        = models.CharField(max_length=200)
    message      = models.TextField()
    type         = models.CharField(max_length=30, choices=TYPE_CHOICES, default='info')

    # Department label and color shown on mobile notification card
    source_label = models.CharField(
        max_length=200, blank=True, default='',
        help_text='Department or office name shown on the mobile card'
    )
    source_color = models.CharField(
        max_length=20, default='orange',
        help_text='Color key: red, dark_blue, green, charcoal, purple, teal, amber, blue, dark_green, indigo, brown, orange'
    )

    # Optional link back to the announcement that generated this notification
    announcement = models.ForeignKey(
        'announcements.Announcement', on_delete=models.SET_NULL,
        null=True, blank=True
    )

    priority   = models.IntegerField(
        default=1,
        choices=[(1,'Normal'), (2,'Important'), (3,'Urgent'), (4,'Emergency')]
    )
    is_read = models.BooleanField(default=False)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(
        'users.AdminUser', on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.type}] {self.title}'


class NotificationReadStatus(models.Model):
    """
    Tracks which authenticated admin users have read which notifications.
    Guest users track read status locally in IndexedDB.
    """
    user = models.ForeignKey('users.AdminUser', on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification_read_status'
        unique_together = ['user', 'notification']

    def __str__(self):
        return f"{self.user.username} read {self.notification_id}"
