from rest_framework import serializers
from .models import Room

class RoomSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source='facility.name', read_only=True)

    class Meta:
        model = Room
        fields = '__all__'  # includes course_code and course_color added in migration 0002


class CourseListView(serializers.Serializer):
    """Used only for the response shape — the actual view is function-based."""
    course_code  = serializers.CharField()
    course_color = serializers.CharField()
    room_count   = serializers.IntegerField()
