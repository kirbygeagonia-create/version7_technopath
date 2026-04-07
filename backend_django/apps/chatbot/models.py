from django.db import models

class FAQEntry(models.Model):
    CATEGORIES = [
        ('location', 'Location'), ('schedule', 'Schedule'),
        ('academic', 'Academic'), ('services', 'Services'), ('general', 'General'),
    ]
    question = models.TextField()
    answer = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORIES, default='general')
    keywords = models.TextField(default='', blank=True, help_text='Comma-separated keywords for offline matching')
    usage_count = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'faq_entries'

    def __str__(self):
        return self.question[:80]

class AIChatLog(models.Model):
    MODES = [('online', 'Online AI'), ('offline', 'Offline FAQ Fallback')]
    user_query = models.TextField()
    ai_response = models.TextField(blank=True, null=True)
    mode = models.CharField(max_length=10, choices=MODES)
    response_time_ms = models.IntegerField(blank=True, null=True)
    is_successful = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    faq_entry = models.ForeignKey(FAQEntry, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_chat_logs'
