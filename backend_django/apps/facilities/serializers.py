import re
from rest_framework import serializers
from .models import Facility

class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = '__all__'
    
    def validate_code(self, value):
        """Auto-generate code from name if not provided or empty"""
        if not value or not str(value).strip():
            name = self.initial_data.get('name', '')
            if name:
                # Generate code from name: lowercase, alphanumeric only, underscore for spaces
                code = re.sub(r'[^a-zA-Z0-9\s]', '', name).lower().strip().replace(' ', '_')[:20]
                # Ensure uniqueness by adding suffix if needed
                base_code = code
                counter = 1
                while Facility.objects.filter(code=code).exists():
                    code = f"{base_code}_{counter}"
                    counter += 1
                return code
            else:
                raise serializers.ValidationError("Either 'name' or 'code' must be provided")
        return value.strip().lower()
    
    def validate(self, data):
        """Ensure code is set before saving"""
        if 'code' not in data or not data.get('code'):
            name = data.get('name', '')
            if name:
                # Generate code from name
                code = re.sub(r'[^a-zA-Z0-9\s]', '', name).lower().strip().replace(' ', '_')[:20]
                # Ensure uniqueness
                base_code = code
                counter = 1
                while Facility.objects.filter(code=code).exists():
                    code = f"{base_code}_{counter}"
                    counter += 1
                data['code'] = code
            else:
                raise serializers.ValidationError({"code": "Code is required when name is not provided"})
        return data
