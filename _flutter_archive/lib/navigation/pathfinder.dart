import 'dart:math' as math;

/// NavigationNode represents a point on the campus map
/// Used for Dijkstra's shortest path algorithm
class NavigationNode {
  final int id;
  final String name;
  final String nodeType;
  final int? facilityId;
  final int? roomId;
  final double x;
  final double y;
  final int floor;

  NavigationNode({
    required this.id,
    required this.name,
    required this.nodeType,
    this.facilityId,
    this.roomId,
    required this.x,
    required this.y,
    this.floor = 1,
  });

  factory NavigationNode.fromMap(Map<String, dynamic> map) {
    return NavigationNode(
      id: map['id'] as int,
      name: map['name'] as String,
      nodeType: map['node_type'] as String,
      facilityId: map['facility_id'] as int?,
      roomId: map['room_id'] as int?,
      x: map['x_position'] as double,
      y: map['y_position'] as double,
      floor: map['floor'] as int? ?? 1,
    );
  }

  /// Calculate Euclidean distance to another node
  double distanceTo(NavigationNode other) {
    return math.sqrt(math.pow(x - other.x, 2) + math.pow(y - other.y, 2));
  }

  /// Calculate walking distance in meters (approximate scale)
  double distanceInMeters(NavigationNode other) {
    // Assuming map coordinates are normalized (0-1 scale)
    // Campus is approximately 500m x 500m
    final scale = 500.0;
    return distanceTo(other) * scale;
  }
}

/// NavigationEdge represents a path between two nodes
class NavigationEdge {
  final int id;
  final int fromNodeId;
  final int toNodeId;
  final double weight;
  final String edgeType;
  final bool isAccessible;

  NavigationEdge({
    required this.id,
    required this.fromNodeId,
    required this.toNodeId,
    required this.weight,
    this.edgeType = 'walkway',
    this.isAccessible = true,
  });

  factory NavigationEdge.fromMap(Map<String, dynamic> map) {
    return NavigationEdge(
      id: map['id'] as int,
      fromNodeId: map['from_node_id'] as int,
      toNodeId: map['to_node_id'] as int,
      weight: (map['weight'] as num).toDouble(),
      edgeType: map['edge_type'] as String? ?? 'walkway',
      isAccessible: (map['is_accessible'] as int? ?? 1) == 1,
    );
  }
}

/// RouteStep represents a single step in navigation directions
class RouteStep {
  final int stepNumber;
  final String instruction;
  final String? landmark;
  final double? distance;
  final String? turnDirection;
  final NavigationNode? fromNode;
  final NavigationNode? toNode;

  RouteStep({
    required this.stepNumber,
    required this.instruction,
    this.landmark,
    this.distance,
    this.turnDirection,
    this.fromNode,
    this.toNode,
  });
}

/// NavigationRoute represents the complete path from start to destination
class NavigationRoute {
  final List<NavigationNode> nodes;
  final List<NavigationEdge> edges;
  final double totalDistance;
  final Duration estimatedTime;
  final List<RouteStep> steps;
  final NavigationNode start;
  final NavigationNode destination;

  NavigationRoute({
    required this.nodes,
    required this.edges,
    required this.totalDistance,
    required this.estimatedTime,
    required this.steps,
    required this.start,
    required this.destination,
  });

  /// Total distance in meters
  double get distanceInMeters => totalDistance * 500; // Assuming 500m campus scale

  /// Formatted distance string
  String get formattedDistance {
    if (distanceInMeters < 1000) {
      return '${distanceInMeters.toStringAsFixed(0)} m';
    } else {
      return '${(distanceInMeters / 1000).toStringAsFixed(1)} km';
    }
  }

  /// Formatted time string
  String get formattedTime {
    if (estimatedTime.inMinutes < 1) {
      return '${estimatedTime.inSeconds} sec';
    } else if (estimatedTime.inMinutes < 60) {
      return '${estimatedTime.inMinutes} min';
    } else {
      final hours = estimatedTime.inMinutes ~/ 60;
      final mins = estimatedTime.inMinutes % 60;
      return '${hours}h ${mins}m';
    }
  }
}

/// DijkstraPathfinder implements Dijkstra's shortest path algorithm
/// for offline campus navigation
class DijkstraPathfinder {
  final List<NavigationNode> nodes;
  final List<NavigationEdge> edges;
  
  // Adjacency list representation of the graph
  final Map<int, List<MapEntry<int, double>>> _adjacencyList = {};

  DijkstraPathfinder({required this.nodes, required this.edges}) {
    _buildAdjacencyList();
  }

  void _buildAdjacencyList() {
    for (var edge in edges) {
      // Add bidirectional edges
      _adjacencyList.putIfAbsent(edge.fromNodeId, () => []);
      _adjacencyList.putIfAbsent(edge.toNodeId, () => []);
      
      _adjacencyList[edge.fromNodeId]!.add(MapEntry(edge.toNodeId, edge.weight));
      _adjacencyList[edge.toNodeId]!.add(MapEntry(edge.fromNodeId, edge.weight));
    }
  }

  /// Find the shortest path between two nodes using Dijkstra's algorithm
  NavigationRoute? findShortestPath(int startNodeId, int targetNodeId) {
    // Validate nodes exist
    final startNode = nodes.firstWhere((n) => n.id == startNodeId, orElse: () => throw Exception('Start node not found'));
    final targetNode = nodes.firstWhere((n) => n.id == targetNodeId, orElse: () => throw Exception('Target node not found'));

    // Dijkstra's algorithm
    final distances = <int, double>{};
    final previous = <int, int?>{};
    final unvisited = <int>{};

    // Initialize
    for (var node in nodes) {
      distances[node.id] = double.infinity;
      previous[node.id] = null;
      unvisited.add(node.id);
    }
    distances[startNodeId] = 0;

    while (unvisited.isNotEmpty) {
      // Find unvisited node with minimum distance
      int? current;
      double minDistance = double.infinity;
      for (var nodeId in unvisited) {
        if (distances[nodeId]! < minDistance) {
          minDistance = distances[nodeId]!;
          current = nodeId;
        }
      }

      if (current == null || distances[current] == double.infinity) {
        break; // No reachable nodes remain
      }

      if (current == targetNodeId) {
        break; // Found shortest path to target
      }

      unvisited.remove(current);

      // Check neighbors
      final neighbors = _adjacencyList[current] ?? [];
      for (var neighbor in neighbors) {
        if (!unvisited.contains(neighbor.key)) continue;

        final alt = distances[current]! + neighbor.value;
        if (alt < distances[neighbor.key]!) {
          distances[neighbor.key] = alt;
          previous[neighbor.key] = current;
        }
      }
    }

    // Reconstruct path
    if (previous[targetNodeId] == null && startNodeId != targetNodeId) {
      return null; // No path found
    }

    final path = <NavigationNode>[];
    int? current = targetNodeId;
    while (current != null) {
      final node = nodes.firstWhere((n) => n.id == current);
      path.insert(0, node);
      current = previous[current];
    }

    // Get edges in path
    final pathEdges = <NavigationEdge>[];
    for (var i = 0; i < path.length - 1; i++) {
      final edge = edges.firstWhere(
        (e) => (e.fromNodeId == path[i].id && e.toNodeId == path[i + 1].id) ||
               (e.fromNodeId == path[i + 1].id && e.toNodeId == path[i].id),
        orElse: () => NavigationEdge(
          id: -1,
          fromNodeId: path[i].id,
          toNodeId: path[i + 1].id,
          weight: path[i].distanceTo(path[i + 1]),
        ),
      );
      pathEdges.add(edge);
    }

    // Generate step-by-step directions
    final steps = _generateSteps(path, pathEdges);

    // Calculate total distance and time
    final totalDistance = distances[targetNodeId]!;
    final averageWalkingSpeed = 1.4; // meters per second (5 km/h)
    final estimatedSeconds = (totalDistance * 500) / averageWalkingSpeed;

    return NavigationRoute(
      nodes: path,
      edges: pathEdges,
      totalDistance: totalDistance,
      estimatedTime: Duration(seconds: estimatedSeconds.ceil()),
      steps: steps,
      start: startNode,
      destination: targetNode,
    );
  }

  /// Generate human-readable step-by-step directions
  List<RouteStep> _generateSteps(List<NavigationNode> path, List<NavigationEdge> edges) {
    final steps = <RouteStep>[];
    
    if (path.isEmpty) return steps;

    // Starting point
    steps.add(RouteStep(
      stepNumber: 1,
      instruction: 'Start at ${path.first.name}',
      landmark: path.first.name,
      fromNode: path.first,
    ));

    for (var i = 1; i < path.length; i++) {
      final prev = path[i - 1];
      final current = path[i];
      final distance = prev.distanceInMeters(current);
      
      String instruction;
      String? turnDirection;
      String? landmark;

      if (i == path.length - 1) {
        instruction = 'Arrive at ${current.name}';
        landmark = current.name;
      } else {
        final next = path[i + 1];
        turnDirection = _calculateTurnDirection(prev, current, next);
        
        if (current.facilityId != null) {
          landmark = current.name;
          if (turnDirection != null) {
            instruction = 'Walk ${distance.toStringAsFixed(0)}m toward ${current.name}, then $turnDirection';
          } else {
            instruction = 'Continue straight for ${distance.toStringAsFixed(0)}m to ${current.name}';
          }
        } else {
          if (turnDirection != null) {
            instruction = 'Walk ${distance.toStringAsFixed(0)}m, then $turnDirection';
          } else {
            instruction = 'Continue straight for ${distance.toStringAsFixed(0)}m';
          }
        }
      }

      steps.add(RouteStep(
        stepNumber: i + 1,
        instruction: instruction,
        landmark: landmark,
        distance: distance,
        turnDirection: turnDirection,
        fromNode: prev,
        toNode: current,
      ));
    }

    return steps;
  }

  /// Calculate turn direction based on angle between three points
  String? _calculateTurnDirection(NavigationNode prev, NavigationNode current, NavigationNode next) {
    // Calculate vectors
    final v1x = current.x - prev.x;
    final v1y = current.y - prev.y;
    final v2x = next.x - current.x;
    final v2y = next.y - current.y;

    // Calculate angle using dot product
    final dot = v1x * v2x + v1y * v2y;
    final det = v1x * v2y - v1y * v2x;
    final angle = math.atan2(det, dot) * (180 / math.pi);

    if (angle > 30 && angle < 150) {
      return 'turn right';
    } else if (angle < -30 && angle > -150) {
      return 'turn left';
    } else if (angle.abs() >= 150) {
      return 'make a U-turn';
    }
    return null; // Continue straight
  }

  /// Find the nearest node to a given position
  NavigationNode? findNearestNode(double x, double y, {int? floor}) {
    NavigationNode? nearest;
    double minDistance = double.infinity;

    for (var node in nodes) {
      if (floor != null && node.floor != floor) continue;
      
      final distance = math.sqrt(math.pow(node.x - x, 2) + math.pow(node.y - y, 2));
      if (distance < minDistance) {
        minDistance = distance;
        nearest = node;
      }
    }

    return nearest;
  }

  /// Find path from current position to destination
  NavigationRoute? navigateFromPosition(double currentX, double currentY, int targetNodeId, {int? currentFloor}) {
    final nearestNode = findNearestNode(currentX, currentY, floor: currentFloor);
    if (nearestNode == null) return null;
    
    return findShortestPath(nearestNode.id, targetNodeId);
  }

  /// Find all reachable nodes from a starting point within max distance
  List<NavigationNode> findReachableNodes(int startNodeId, double maxDistance) {
    final reachable = <NavigationNode>[];
    
    for (var node in nodes) {
      if (node.id == startNodeId) continue;
      
      final route = findShortestPath(startNodeId, node.id);
      if (route != null && route.totalDistance <= maxDistance) {
        reachable.add(node);
      }
    }
    
    return reachable;
  }

  /// Get accessibility-friendly routes (avoiding stairs, etc.)
  NavigationRoute? findAccessibleRoute(int startNodeId, int targetNodeId) {
    // Filter to only accessible edges
    final accessibleEdges = edges.where((e) => e.isAccessible).toList();
    final accessiblePathfinder = DijkstraPathfinder(nodes: nodes, edges: accessibleEdges);
    return accessiblePathfinder.findShortestPath(startNodeId, targetNodeId);
  }

  /// Batch route calculation for multiple destinations
  Map<int, NavigationRoute> calculateRoutesToMultipleDestinations(
    int startNodeId,
    List<int> destinationIds,
  ) {
    final routes = <int, NavigationRoute>{};
    
    for (var destId in destinationIds) {
      final route = findShortestPath(startNodeId, destId);
      if (route != null) {
        routes[destId] = route;
      }
    }
    
    return routes;
  }

  /// Get nodes by facility ID
  List<NavigationNode> getNodesByFacility(int facilityId) {
    return nodes.where((n) => n.facilityId == facilityId).toList();
  }

  /// Get nodes by type
  List<NavigationNode> getNodesByType(String nodeType) {
    return nodes.where((n) => n.nodeType == nodeType).toList();
  }

  /// Get the main entrance node
  NavigationNode? getMainEntrance() {
    try {
      return nodes.firstWhere((n) => n.nodeType == 'entrance');
    } catch (e) {
      return nodes.isNotEmpty ? nodes.first : null;
    }
  }
}

/// Utility class for route display and formatting
class RouteFormatter {
  /// Format a list of steps into readable text
  static String formatRouteText(NavigationRoute route) {
    final buffer = StringBuffer();
    buffer.writeln('📍 From: ${route.start.name}');
    buffer.writeln('🏁 To: ${route.destination.name}');
    buffer.writeln('📏 Distance: ${route.formattedDistance}');
    buffer.writeln('⏱️ Time: ${route.formattedTime}');
    buffer.writeln();
    buffer.writeln('Directions:');
    
    for (var step in route.steps) {
      buffer.writeln('${step.stepNumber}. ${step.instruction}');
    }
    
    return buffer.toString();
  }

  /// Get quick summary of the route
  static String getRouteSummary(NavigationRoute route) {
    return '${route.formattedDistance} • ${route.formattedTime} • ${route.steps.length - 1} steps';
  }

  /// Estimate calories burned (rough approximation)
  static double estimateCaloriesBurned(double distanceInMeters) {
    // Average person burns ~50 calories per km walked
    return (distanceInMeters / 1000) * 50;
  }

  /// Get difficulty level based on distance
  static String getDifficultyLevel(double distanceInMeters) {
    if (distanceInMeters < 100) return 'Very Easy';
    if (distanceInMeters < 300) return 'Easy';
    if (distanceInMeters < 500) return 'Moderate';
    if (distanceInMeters < 1000) return 'Long Walk';
    return 'Very Long Walk';
  }
}
