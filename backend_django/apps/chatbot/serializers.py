from rest_framework import serializers
from .models import FAQEntry, AIChatLog

class FAQEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQEntry
        fields = '__all__'

class AIChatLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIChatLog
        fields = '__all__'
