from rest_framework import serializers
from .models import NavigationNode, NavigationEdge, Path, PathPoint

class NavigationNodeSerializer(serializers.ModelSerializer):
    x_position = serializers.FloatField(source='x', read_only=True)
    y_position = serializers.FloatField(source='y', read_only=True)
    
    class Meta:
        model = NavigationNode
        fields = ['id', 'name', 'node_type', 'facility', 'room', 'map_svg_id', 
                  'x', 'y', 'x_position', 'y_position', 'floor', 'is_deleted', 
                  'created_at', 'updated_at']

class NavigationEdgeSerializer(serializers.ModelSerializer):
    from_node_name = serializers.CharField(source='from_node.name', read_only=True)
    to_node_name = serializers.CharField(source='to_node.name', read_only=True)
    from_node_id = serializers.IntegerField(source='from_node.id', read_only=True)
    to_node_id = serializers.IntegerField(source='to_node.id', read_only=True)
    
    class Meta:
        model = NavigationEdge
        fields = ['id', 'from_node', 'to_node', 'from_node_id', 'to_node_id', 
                  'from_node_name', 'to_node_name', 'distance', 'is_bidirectional', 
                  'is_deleted', 'created_at', 'updated_at']


class PathPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = PathPoint
        fields = ['id', 'sequence', 'element_id', 'x', 'y', 'is_deleted', 'created_at', 'updated_at']


class PathSerializer(serializers.ModelSerializer):
    points = PathPointSerializer(many=True, read_only=True)
    element_ids = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    points_input = serializers.ListField(child=serializers.ListField(child=serializers.FloatField()), write_only=True, required=False)
    facility_name = serializers.CharField(source='facility.name', read_only=True, allow_null=True)
    room_name = serializers.CharField(source='room.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Path
        fields = ['id', 'name', 'description', 'facility', 'facility_name', 'room', 'room_name',
                  'floor', 'created_by', 'from_location', 'to_location', 'points', 'element_ids',
                  'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['created_by']
    
    def create(self, validated_data):
        element_ids = validated_data.pop('element_ids', [])
        points_data = validated_data.pop('points_input', validated_data.pop('points', []))
        path = Path.objects.create(**validated_data)
        
        # Create path points with actual coordinates
        for i, element_id in enumerate(element_ids):
            # Get coordinates from points array if available
            if i < len(points_data) and isinstance(points_data[i], (list, tuple)) and len(points_data[i]) >= 2:
                x_coord = points_data[i][0]
                y_coord = points_data[i][1]
            else:
                x_coord = 0
                y_coord = 0
            
            PathPoint.objects.create(
                path=path,
                sequence=i,
                element_id=element_id,
                x=x_coord,
                y=y_coord
            )
        return path
    
    def update(self, instance, validated_data):
        element_ids = validated_data.pop('element_ids', None)
        points_data = validated_data.pop('points_input', validated_data.pop('points', None))
        
        # Update path fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update points if element_ids provided
        if element_ids is not None:
            # Mark existing points as deleted
            instance.points.filter(is_deleted=False).update(is_deleted=True)
            # Create new points with actual coordinates
            for i, element_id in enumerate(element_ids):
                # Get coordinates from points array if available
                if points_data and i < len(points_data) and isinstance(points_data[i], (list, tuple)) and len(points_data[i]) >= 2:
                    x_coord = points_data[i][0]
                    y_coord = points_data[i][1]
                else:
                    x_coord = 0
                    y_coord = 0
                
                PathPoint.objects.create(
                    path=instance,
                    sequence=i,
                    element_id=element_id,
                    x=x_coord,
                    y=y_coord
                )
        return instance
