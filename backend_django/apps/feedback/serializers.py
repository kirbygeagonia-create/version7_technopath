from rest_framework import serializers
from .models import Feedback

class FeedbackSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        min_value=1,
        max_value=5,
        allow_null=True,
        required=False,
        help_text='Rating must be between 1 and 5.'
    )

    class Meta:
        model = Feedback
        fields = [
            'id', 'rating', 'comment', 'category',
            'facility', 'room', 'is_anonymous', 'location', 'created_at'
        ]
        read_only_fields = ['id', 'is_flagged', 'flag_reason', 'created_at']
