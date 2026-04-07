from rest_framework import serializers
from .models import NavigationNode, NavigationEdge

class NavigationNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NavigationNode
        fields = '__all__'

class NavigationEdgeSerializer(serializers.ModelSerializer):
    from_node_name = serializers.CharField(source='from_node.name', read_only=True)
    to_node_name = serializers.CharField(source='to_node.name', read_only=True)
    
    class Meta:
        model = NavigationEdge
        fields = '__all__'
