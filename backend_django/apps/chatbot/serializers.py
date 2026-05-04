from rest_framework import serializers
from .models import FAQEntry, AIChatLog, FAQSuggestion, TrainingData, ChatRating, ChatCorrection

class FAQEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQEntry
        fields = '__all__'

class AIChatLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIChatLog
        fields = '__all__'

class FAQSuggestionSerializer(serializers.ModelSerializer):
    reviewed_by_name = serializers.CharField(source='reviewed_by.display_name', read_only=True)

    class Meta:
        model = FAQSuggestion
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'faq_entry')


class TrainingDataSerializer(serializers.ModelSerializer):
    """Serializer for ML training data"""
    intent_display = serializers.CharField(source='get_intent_label_display', read_only=True)

    class Meta:
        model = TrainingData
        fields = '__all__'
        read_only_fields = ('created_at',)


class ChatRatingSerializer(serializers.ModelSerializer):
    """Serializer for chat ratings (thumbs up/down)"""
    rating_display = serializers.CharField(source='get_rating_display', read_only=True)

    class Meta:
        model = ChatRating
        fields = '__all__'
        read_only_fields = ('created_at',)


class ChatCorrectionSerializer(serializers.ModelSerializer):
    """Serializer for user corrections when chatbot is wrong"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.display_name', read_only=True)

    class Meta:
        model = ChatCorrection
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'reviewed_at', 'faq_entry')
