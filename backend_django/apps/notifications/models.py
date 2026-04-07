from django.db import models

class Notification(models.Model):
    TYPES = [
        ('info', 'Info'), ('success', 'Success'), ('warning', 'Warning'),
        ('error', 'Error'), ('emergency', 'Emergency'),
        ('facility_update', 'Facility Update'), ('navigation_update', 'Navigation Update'),
        ('system_maintenance', 'System Maintenance'), ('app_update', 'App Update'),
    ]
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=30, choices=TYPES, default='info')
    data_json = models.TextField(default='{}')
    priority = models.IntegerField(default=1, choices=[(1,'Low'),(2,'Medium'),(3,'High'),(4,'Urgent')])
    is_read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=500, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
