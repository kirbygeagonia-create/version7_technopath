from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import NavigationNode, SvgPath, GridSettings
from .serializers import NavigationNodeSerializer, SvgPathSerializer, GridSettingsSerializer
import heapq


class NavigationNodeViewSet(viewsets.ModelViewSet):
    """API endpoint for navigation nodes (buildings, rooms, etc.)"""
    queryset = NavigationNode.objects.filter(is_active=True)
    serializer_class = NavigationNodeSerializer
    lookup_field = 'id'


class SvgPathViewSet(viewsets.ModelViewSet):
    """API endpoint for SVG paths"""
    queryset = SvgPath.objects.filter(is_active=True)
    serializer_class = SvgPathSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        queryset = SvgPath.objects.filter(is_active=True)
        from_node = self.request.query_params.get('from', None)
        to_node = self.request.query_params.get('to', None)
        
        if from_node:
            queryset = queryset.filter(from_node__id=from_node)
        if to_node:
            queryset = queryset.filter(to_node__id=to_node)
            
        return queryset


@api_view(['GET', 'PUT'])
def grid_settings(request):
    """
    Get or update grid settings
    - GET: Returns current grid settings
    - PUT: Updates grid settings
    """
    settings = GridSettings.get_settings()
    
    if request.method == 'GET':
        serializer = GridSettingsSerializer(settings)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = GridSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def find_route(request):
    """
    Find shortest route between two nodes using Dijkstra's algorithm
    Query params:
    - from: starting node ID
    - to: destination node ID
    """
    from_id = request.query_params.get('from')
    to_id = request.query_params.get('to')
    
    if not from_id or not to_id:
        return Response(
            {'error': 'Please provide both from and to parameters'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if direct path exists
    direct_path = SvgPath.objects.filter(
        from_node__id=from_id,
        to_node__id=to_id,
        is_active=True
    ).first()
    
    if direct_path:
        return Response({
            'path_id': direct_path.id,
            'from': from_id,
            'to': to_id,
            'points': direct_path.points,
            'distance': direct_path.distance,
            'time': f"~{max(1, int(direct_path.distance / 60))} min",
            'steps': len(direct_path.points),
            'direct': True
        })
    
    # Build graph for pathfinding
    nodes = list(NavigationNode.objects.filter(is_active=True).values('id'))
    node_ids = [n['id'] for n in nodes]
    
    if from_id not in node_ids or to_id not in node_ids:
        return Response(
            {'error': 'Invalid node IDs'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Build adjacency list from paths
    edges = {}
    paths = SvgPath.objects.filter(is_active=True)
    
    for path in paths:
        if path.from_node_id and path.to_node_id:
            # Add bidirectional edges
            if path.from_node_id not in edges:
                edges[path.from_node_id] = []
            if path.to_node_id not in edges:
                edges[path.to_node_id] = []
                
            edges[path.from_node_id].append((path.to_node_id, path.distance, path.id))
            edges[path.to_node_id].append((path.from_node_id, path.distance, path.id))
    
    # Dijkstra's algorithm
    distances = {node_id: float('inf') for node_id in node_ids}
    distances[from_id] = 0
    previous = {node_id: None for node_id in node_ids}
    path_used = {}
    
    pq = [(0, from_id)]
    
    while pq:
        current_dist, current_id = heapq.heappop(pq)
        
        if current_id == to_id:
            break
            
        if current_dist > distances[current_id]:
            continue
            
        for neighbor_id, edge_dist, path_id in edges.get(current_id, []):
            distance = current_dist + edge_dist
            
            if distance < distances[neighbor_id]:
                distances[neighbor_id] = distance
                previous[neighbor_id] = current_id
                path_used[neighbor_id] = path_id
                heapq.heappush(pq, (distance, neighbor_id))
    
    if distances[to_id] == float('inf'):
        return Response(
            {'error': 'No route found between these locations'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Reconstruct path
    route_nodes = []
    current = to_id
    while current:
        route_nodes.append(current)
        current = previous[current]
    route_nodes.reverse()
    
    # Collect all points from the paths
    all_points = []
    for i in range(len(route_nodes) - 1):
        path_id = path_used.get(route_nodes[i+1])
        if path_id:
            path = SvgPath.objects.get(id=path_id)
            if i == 0:
                all_points.extend(path.points)
            else:
                all_points.extend(path.points[1:])  # Skip first point (duplicate)
    
    return Response({
        'from': from_id,
        'to': to_id,
        'points': all_points,
        'distance': distances[to_id],
        'time': f"~{max(1, int(distances[to_id] / 60))} min",
        'steps': len(route_nodes),
        'nodes': route_nodes,
        'direct': False
    })
