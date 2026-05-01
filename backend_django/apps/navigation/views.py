from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import transaction
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os

from django.conf import settings

from .models import NavigationNode, NavigationEdge, Path, PathPoint
from .serializers import NavigationNodeSerializer, NavigationEdgeSerializer, PathSerializer
from apps.users.permissions import ReadOnlyOrSuperAdmin


class MapGalleryView(APIView):
    """
    List all uploaded SVG map files.
    GET /navigation/maps/
    """
    permission_classes = [ReadOnlyOrSuperAdmin]

    def get(self, request):
        maps_dir = os.path.join(settings.MEDIA_ROOT, 'maps')
        maps = []
        
        if os.path.exists(maps_dir):
            for filename in os.listdir(maps_dir):
                if filename.lower().endswith('.svg'):
                    file_path = os.path.join(maps_dir, filename)
                    file_stat = os.stat(file_path)
                    maps.append({
                        'filename': filename,
                        'url': f"{settings.MEDIA_URL}maps/{filename}",
                        'size': file_stat.st_size,
                        'uploaded_at': file_stat.st_mtime,
                        'is_active': self._is_active_map(filename)
                    })
        
        # Sort by upload time (newest first)
        maps.sort(key=lambda x: x['uploaded_at'], reverse=True)
        
        return Response({
            'maps': maps,
            'count': len(maps),
            'media_url': settings.MEDIA_URL
        })

    def _is_active_map(self, filename):
        """Check if this map is currently being used."""
        # For now, check if any node references this map
        return NavigationNode.objects.filter(
            map_svg_id__icontains=filename.replace('.svg', '')
        ).exists()

    def delete(self, request, filename=None):
        """Delete a specific map file."""
        if not filename:
            return Response(
                {'error': 'Filename required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Security: prevent directory traversal
        filename = os.path.basename(filename)
        file_path = os.path.join(settings.MEDIA_ROOT, 'maps', filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return Response({'message': f'Map {filename} deleted'})
        
        return Response(
            {'error': 'File not found'},
            status=status.HTTP_404_NOT_FOUND
        )


class ImportMapView(APIView):
    """
    Import navigation graph data from JSON or upload a new SVG map file.
    POST /navigation/import/
    """
    permission_classes = [ReadOnlyOrSuperAdmin]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        # Handle JSON data import (nodes and edges)
        if 'file' in request.FILES:
            file = request.FILES['file']
            file_name = file.name.lower()
            
            # Handle SVG map upload
            if file_name.endswith('.svg'):
                return self._import_svg_map(file)
            
            # Handle JSON graph data import
            elif file_name.endswith('.json'):
                return self._import_json_graph(file)
            else:
                return Response(
                    {'error': 'Unsupported file format. Only .svg and .json files are allowed.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Handle JSON body import
        elif request.content_type == 'application/json':
            return self._import_graph_data(request.data)
        
        return Response(
            {'error': 'No file or JSON data provided'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def _import_svg_map(self, file):
        """Upload and store a new SVG map file."""
        try:
            # Save to assets directory
            file_path = f'maps/{file.name}'
            saved_path = default_storage.save(file_path, ContentFile(file.read()))
            
            return Response({
                'message': 'SVG map uploaded successfully',
                'file_name': file.name,
                'file_path': saved_path,
                'file_size': file.size
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': f'Failed to upload SVG: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _import_json_graph(self, file):
        """Import navigation graph from JSON file."""
        try:
            data = json.loads(file.read().decode('utf-8'))
            return self._import_graph_data(data)
        except json.JSONDecodeError as e:
            return Response(
                {'error': f'Invalid JSON format: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _import_graph_data(self, data):
        """Import nodes and edges from JSON data."""
        try:
            with transaction.atomic():
                nodes_created = 0
                edges_created = 0
                nodes_map = {}  # Map external IDs to created node IDs
                
                # Import nodes
                if 'nodes' in data:
                    for node_data in data['nodes']:
                        external_id = node_data.pop('id', None)
                        
                        # Check for existing node by map_svg_id
                        map_svg_id = node_data.get('map_svg_id')
                        if map_svg_id:
                            existing = NavigationNode.objects.filter(
                                map_svg_id=map_svg_id, 
                                is_deleted=False
                            ).first()
                            if existing:
                                nodes_map[external_id] = existing
                                continue
                        
                        node = NavigationNode.objects.create(**node_data)
                        nodes_created += 1
                        if external_id:
                            nodes_map[external_id] = node
                
                # Import edges
                if 'edges' in data:
                    for edge_data in data['edges']:
                        from_node_id = edge_data.get('from_node')
                        to_node_id = edge_data.get('to_node')
                        
                        # Resolve node references
                        if isinstance(from_node_id, int) and from_node_id in nodes_map:
                            from_node = nodes_map[from_node_id]
                        else:
                            from_node = NavigationNode.objects.get(id=from_node_id)
                        
                        if isinstance(to_node_id, int) and to_node_id in nodes_map:
                            to_node = nodes_map[to_node_id]
                        else:
                            to_node = NavigationNode.objects.get(id=to_node_id)
                        
                        # Check for existing edge
                        existing_edge = NavigationEdge.objects.filter(
                            from_node=from_node,
                            to_node=to_node,
                            is_deleted=False
                        ).first()
                        
                        if not existing_edge:
                            NavigationEdge.objects.create(
                                from_node=from_node,
                                to_node=to_node,
                                distance=edge_data.get('distance', 0),
                                is_bidirectional=edge_data.get('is_bidirectional', True)
                            )
                            edges_created += 1
                
                return Response({
                    'message': 'Navigation graph imported successfully',
                    'nodes_created': nodes_created,
                    'edges_created': edges_created
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {'error': f'Import failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request):
        """Get import template/example."""
        example_data = {
            'nodes': [
                {
                    'id': 1,
                    'name': 'Main Entrance',
                    'node_type': 'entrance',
                    'map_svg_id': 'entrance_main',
                    'x': 0.5,
                    'y': 0.9,
                    'floor': 1
                },
                {
                    'id': 2,
                    'name': 'MST Building Lobby',
                    'node_type': 'facility',
                    'map_svg_id': 'mst_lobby',
                    'x': 0.3,
                    'y': 0.4,
                    'floor': 1
                }
            ],
            'edges': [
                {
                    'from_node': 1,
                    'to_node': 2,
                    'distance': 150,
                    'is_bidirectional': True
                }
            ]
        }
        return Response({
            'description': 'Import navigation graph by posting JSON with nodes and edges',
            'example': example_data,
            'file_upload': 'POST with multipart/form-data and "file" field (JSON or SVG)',
            'json_upload': 'POST with application/json body containing nodes/edges'
        })


class NavigationNodeListView(generics.ListCreateAPIView):
    queryset = NavigationNode.objects.filter(is_deleted=False)
    serializer_class = NavigationNodeSerializer
    permission_classes = [ReadOnlyOrSuperAdmin]


class NavigationNodeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NavigationNode.objects.filter(is_deleted=False)
    serializer_class = NavigationNodeSerializer
    permission_classes = [ReadOnlyOrSuperAdmin]

    def perform_destroy(self, instance):
        """Soft delete — set is_deleted flag instead of removing the record."""
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


class NavigationEdgeListView(generics.ListCreateAPIView):
    queryset = NavigationEdge.objects.filter(is_deleted=False)
    serializer_class = NavigationEdgeSerializer
    permission_classes = [ReadOnlyOrSuperAdmin]


class NavigationEdgeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NavigationEdge.objects.filter(is_deleted=False)
    serializer_class = NavigationEdgeSerializer
    permission_classes = [ReadOnlyOrSuperAdmin]

    def perform_destroy(self, instance):
        """Soft delete — set is_deleted flag instead of removing the record."""
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


class FindRouteView(APIView):
    """
    Find shortest route between two navigation nodes.
    GET /navigation/route/?from=<node_name>&to=<node_name>
    """
    permission_classes = [ReadOnlyOrSuperAdmin]

    def get(self, request):
        from_name = request.query_params.get('from')
        to_name = request.query_params.get('to')

        if not from_name or not to_name:
            return Response(
                {'error': 'Both "from" and "to" parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from_node = NavigationNode.objects.filter(
                name__iexact=from_name, is_deleted=False
            ).first()
            to_node = NavigationNode.objects.filter(
                name__iexact=to_name, is_deleted=False
            ).first()

            if not from_node:
                return Response(
                    {'error': f'Start location "{from_name}" not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            if not to_node:
                return Response(
                    {'error': f'Destination "{to_name}" not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Find shortest path using Dijkstra's algorithm
            path = self._find_shortest_path(from_node, to_node)

            if not path:
                return Response(
                    {'error': 'No route found between these locations'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Calculate total distance and build response
            total_distance = 0
            route_points = []
            route_steps = []

            for i, node in enumerate(path):
                route_points.append({
                    'x': node.x,  # Return normalized 0-1 coordinates
                    'y': node.y,
                    'name': node.name,
                    'type': node.node_type
                })

                if i > 0:
                    # Find edge between previous and current node
                    edge = NavigationEdge.objects.filter(
                        from_node=path[i-1], to_node=node, is_deleted=False
                    ).first() or NavigationEdge.objects.filter(
                        from_node=node, to_node=path[i-1], is_deleted=False,
                        is_bidirectional=True
                    ).first()
                    if edge:
                        total_distance += edge.distance

            # Generate turn-by-turn directions
            route_steps = self._generate_directions(path, total_distance)

            return Response({
                'from': from_name,
                'to': to_name,
                'points': route_points,
                'distance': f'~{total_distance}m',
                'distance_meters': total_distance,
                'time': f'~{max(1, round(total_distance / 60))} min',
                'steps': len(route_steps),
                'directions': route_steps
            })

        except Exception as e:
            return Response(
                {'error': f'Route calculation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _find_shortest_path(self, start_node, end_node):
        """Dijkstra's algorithm implementation."""
        import heapq

        # Build adjacency list
        nodes = NavigationNode.objects.filter(is_deleted=False)
        edges = NavigationEdge.objects.filter(is_deleted=False)

        graph = {node.id: [] for node in nodes}

        for edge in edges:
            graph[edge.from_node_id].append((edge.to_node_id, edge.distance))
            if edge.is_bidirectional:
                graph[edge.to_node_id].append((edge.from_node_id, edge.distance))

        # Dijkstra's algorithm
        distances = {node_id: float('inf') for node_id in graph}
        distances[start_node.id] = 0
        previous = {node_id: None for node_id in graph}
        visited = set()

        heap = [(0, start_node.id)]

        while heap:
            current_dist, current_id = heapq.heappop(heap)

            if current_id in visited:
                continue
            visited.add(current_id)

            if current_id == end_node.id:
                # Reconstruct path
                path = []
                node_id = end_node.id
                while node_id is not None:
                    node = NavigationNode.objects.get(id=node_id)
                    path.append(node)
                    node_id = previous[node_id]
                return path[::-1]

            for neighbor_id, weight in graph.get(current_id, []):
                if neighbor_id not in visited:
                    new_dist = current_dist + weight
                    if new_dist < distances[neighbor_id]:
                        distances[neighbor_id] = new_dist
                        previous[neighbor_id] = current_id
                        heapq.heappush(heap, (new_dist, neighbor_id))

        return None  # No path found

    def _generate_directions(self, path, total_distance):
        """Generate turn-by-turn directions."""
        steps = []
        steps.append({
            'instruction': f'Start at {path[0].name}',
            'distance': ''
        })

        for i in range(1, len(path)):
            prev_node = path[i-1]
            curr_node = path[i]

            # Calculate segment distance
            edge = NavigationEdge.objects.filter(
                from_node=prev_node, to_node=curr_node, is_deleted=False
            ).first() or NavigationEdge.objects.filter(
                from_node=curr_node, to_node=prev_node, is_deleted=False,
                is_bidirectional=True
            ).first()

            segment_distance = edge.distance if edge else 0

            if i < len(path) - 1:
                next_node = path[i+1]
                # Calculate turn direction
                dx1 = curr_node.x - prev_node.x
                dy1 = curr_node.y - prev_node.y
                dx2 = next_node.x - curr_node.x
                dy2 = next_node.y - curr_node.y

                angle = self._calculate_turn_angle(dx1, dy1, dx2, dy2)
                turn = self._angle_to_direction(angle)

                steps.append({
                    'instruction': f'Walk toward {curr_node.name}, then {turn} to {next_node.name}',
                    'distance': f'~{segment_distance}m'
                })
            else:
                steps.append({
                    'instruction': f'Arrive at {curr_node.name}',
                    'distance': ''
                })

        return steps

    def _calculate_turn_angle(self, dx1, dy1, dx2, dy2):
        """Calculate turn angle between two vectors."""
        import math
        angle1 = math.atan2(dy1, dx1)
        angle2 = math.atan2(dy2, dx2)
        angle = math.degrees(angle2 - angle1)
        return (angle + 360) % 360

    def _angle_to_direction(self, angle):
        """Convert angle to turn direction."""
        if angle < 30 or angle > 330:
            return 'continue straight'
        elif 30 <= angle < 150:
            return 'turn right'
        elif 150 <= angle < 210:
            return 'make a U-turn'
        elif 210 <= angle < 330:
            return 'turn left'
        return 'continue'


class GridSettingsView(APIView):
    """Stub endpoint for grid settings - frontend uses localStorage."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        # Return defaults - frontend will use localStorage
        return Response({'show_grid': True, 'grid_size': 20})

    def put(self, request):
        # Accept but don't store - frontend uses localStorage
        return Response({'show_grid': True, 'grid_size': 20})


class NavigationPathsView(APIView):
    """API endpoint for navigation paths with database storage."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        """List all non-deleted paths."""
        paths = Path.objects.filter(is_deleted=False).prefetch_related('points')
        serializer = PathSerializer(paths, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a new path."""
        try:
            data = request.data.copy()
            
            # Remove null facility/room if they don't exist
            if 'facility' in data and data['facility'] is None:
                del data['facility']
            if 'room' in data and data['room'] is None:
                del data['room']
            
            serializer = PathSerializer(data=data)
            if serializer.is_valid():
                # Set created_by from request user
                created_by = request.user if request.user.is_authenticated else None
                serializer.save(created_by=created_by)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            print(f"[Path Create Error] {str(e)}\n{traceback.format_exc()}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NavigationPathDetailView(APIView):
    """API endpoint for single path operations."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Path.objects.get(pk=pk, is_deleted=False)
        except Path.DoesNotExist:
            return None

    def get(self, request, pk):
        """Get a single path."""
        path = self.get_object(pk)
        if not path:
            return Response({'error': 'Path not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PathSerializer(path)
        return Response(serializer.data)

    def put(self, request, pk):
        """Update a path."""
        path = self.get_object(pk)
        if not path:
            return Response({'error': 'Path not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PathSerializer(path, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Soft delete a path."""
        path = self.get_object(pk)
        if not path:
            return Response({'error': 'Path not found'}, status=status.HTTP_404_NOT_FOUND)
        
        path.is_deleted = True
        path.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
