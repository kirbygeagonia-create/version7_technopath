from rest_framework import serializers
from .models import FAQEntry, AIChatLog, FAQSuggestion

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
