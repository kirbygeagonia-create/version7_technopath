from rest_framework import serializers
from .models import NavigationNode, SvgPath, GridSettings

class NavigationNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NavigationNode
        fields = ['id', 'name', 'node_type', 'x', 'y', 'building', 
                  'floor', 'description', 'is_active', 'created_at', 'updated_at']


class SvgPathSerializer(serializers.ModelSerializer):
    from_name = serializers.CharField(source='from_node.name', read_only=True)
    to_name = serializers.CharField(source='to_node.name', read_only=True)
    
    class Meta:
        model = SvgPath
        fields = ['id', 'name', 'description', 'from_node', 'to_node',
                  'from_name', 'to_name', 'points', 'element_ids', 
                  'distance', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['distance']

    def create(self, validated_data):
        path = SvgPath.objects.create(**validated_data)
        path.calculate_distance()
        path.save()
        return path

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.calculate_distance()
        instance.save()
        return instance


class GridSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GridSettings
        fields = ['id', 'show_grid', 'grid_size', 'grid_opacity', 
                  'snap_to_grid', 'show_labels', 'label_interval', 'updated_at']
