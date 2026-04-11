from django.db import models
from apps.facilities.models import Facility
from apps.rooms.models import Room

class Feedback(models.Model):
    CATEGORIES = [
        ('map_accuracy', 'Map Accuracy'), ('ai_chatbot', 'AI Chatbot'),
        ('navigation', 'Navigation'), ('general', 'General'),
        ('bug_report', 'Bug Report'), ('facility', 'Facility'), ('room', 'Room'),
    ]
    rating      = models.IntegerField(blank=True, null=True)
    comment     = models.TextField(blank=True, null=True)
    category    = models.CharField(max_length=30, choices=CATEGORIES, default='general')
    facility    = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True)
    room        = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    # Fields sent by FeedbackView
    is_anonymous = models.BooleanField(default=False)
    location     = models.CharField(max_length=200, blank=True, null=True,
                                    help_text='Optional campus location name this feedback relates to')
    is_flagged  = models.BooleanField(default=False)
    flag_reason = models.TextField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'feedback'

    def __str__(self):
        anon = ' (anon)' if self.is_anonymous else ''
        return f'{self.rating}★ [{self.category}]{anon}'
