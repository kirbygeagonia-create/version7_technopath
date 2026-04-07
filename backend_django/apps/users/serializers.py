from rest_framework import serializers
from .models import AdminUser

class AdminUserSerializer(serializers.ModelSerializer):
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    
    class Meta:
        model = AdminUser
        fields = ['id', 'username', 'email', 'user_type', 'user_type_display', 'department', 
                  'is_active', 'is_staff', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}

class UserMeSerializer(serializers.ModelSerializer):
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    
    class Meta:
        model = AdminUser
        fields = ['id', 'username', 'email', 'user_type', 'user_type_display', 'department', 'is_staff']
