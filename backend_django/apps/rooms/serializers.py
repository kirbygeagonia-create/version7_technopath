from rest_framework import serializers
from .models import Room

class RoomSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source='facility.name', read_only=True)
    
    class Meta:
        model = Room
        fields = '__all__'
