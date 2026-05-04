from django.db import models
import json

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


class FAQSuggestion(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    suggested_question = models.TextField()
    suggested_answer = models.TextField()
    category = models.CharField(max_length=50, choices=FAQEntry.CATEGORIES, default='general')
    keywords = models.TextField(default='', blank=True)
    
    # Analysis metadata
    source_queries = models.JSONField(default=list, help_text='Original queries that triggered this suggestion')
    query_count = models.IntegerField(default=1, help_text='Number of times similar queries were asked')
    confidence_score = models.FloatField(default=0.0, help_text='AI confidence score (0-1)')
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey('users.AdminUser', on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True, null=True)
    
    # Converted FAQ (if approved)
    faq_entry = models.ForeignKey(FAQEntry, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'faq_suggestions'
        ordering = ['-query_count', '-created_at']

    def __str__(self):
        return f"{self.suggested_question[:60]}... ({self.status})"


class TrainingData(models.Model):
    """Stores training examples for the ML intent classifier."""
    INTENT_CHOICES = [
        ('library_hours', 'Library Hours'),
        ('registrar', 'Registrar Office'),
        ('dean_office', 'Dean Office'),
        ('room_location', 'Room/Location'),
        ('schedule', 'Schedule/Time'),
        ('admission', 'Admission/Enrollment'),
        ('scholarship', 'Scholarship/Financial'),
        ('it_support', 'IT Support'),
        ('safety_security', 'Safety/Security'),
        ('general', 'General'),
    ]

    query_text = models.TextField(help_text="Example user query")
    intent_label = models.CharField(max_length=50, choices=INTENT_CHOICES)
    source = models.CharField(max_length=50, default='manual', choices=[
        ('manual', 'Manual'),
        ('faq', 'From FAQ'),
        ('rating', 'From User Rating'),
    ])
    used_for_training = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'training_data'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.intent_label}] {self.query_text[:50]}"


class ChatRating(models.Model):
    """Stores user thumbs up/down feedback on chatbot responses."""
    RATING_CHOICES = [
        ('thumbs_up', 'Thumbs Up'),
        ('thumbs_down', 'Thumbs Down'),
    ]

    query_text = models.TextField()
    response_text = models.TextField()
    intent_detected = models.CharField(max_length=50, blank=True, null=True)
    rating = models.CharField(max_length=20, choices=RATING_CHOICES)
    rating_note = models.TextField(blank=True, null=True, help_text="Optional user feedback")
    session_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_ratings'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rating} on [{self.intent_detected}]"


class ChatCorrection(models.Model):
    """Stores user corrections when chatbot gives wrong answers.
    Admin can review and approve to create new FAQ entries."""

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # Original chatbot interaction
    query_text = models.TextField(help_text="User's original question")
    wrong_response = models.TextField(help_text="Chatbot's wrong answer")
    intent_detected = models.CharField(max_length=50, blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)

    # User's correction
    correct_answer = models.TextField(help_text="User-provided correct answer")
    user_note = models.TextField(blank=True, null=True, help_text="Optional explanation")

    # Review status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True, null=True)

    # Converted to FAQ (if approved)
    faq_entry = models.ForeignKey(FAQEntry, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chat_corrections'
        ordering = ['-created_at']

    def __str__(self):
        return f"Correction: {self.query_text[:50]}... ({self.status})"
