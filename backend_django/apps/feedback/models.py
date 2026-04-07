from django.db import models
from apps.facilities.models import Facility
from apps.rooms.models import Room

class Feedback(models.Model):
    CATEGORIES = [
        ('map_accuracy', 'Map Accuracy'), ('ai_chatbot', 'AI Chatbot'),
        ('navigation', 'Navigation'), ('general', 'General'),
        ('bug_report', 'Bug Report'), ('facility', 'Facility'), ('room', 'Room'),
    ]
    rating = models.IntegerField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=30, choices=CATEGORIES, default='general')
    facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'feedback'
