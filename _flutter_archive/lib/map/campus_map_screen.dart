import 'package:flutter/material.dart';
import 'package:version4_technopath/database_helper_v2.dart';
import 'package:version4_technopath/navigation/pathfinder.dart';

/// Interactive 2D Campus Map with navigation capabilities
/// Features: Zoom, pan, building selection, route display, floor switching
class CampusMapScreen extends StatefulWidget {
  final String? entryPoint;
  final int? destinationFacilityId;
  final int? destinationRoomId;

  const CampusMapScreen({
    super.key,
    this.entryPoint,
    this.destinationFacilityId,
    this.destinationRoomId,
  });

  @override
  State<CampusMapScreen> createState() => _CampusMapScreenState();
}

class _CampusMapScreenState extends State<CampusMapScreen> with TickerProviderStateMixin {
  final TransformationController _transformationController = TransformationController();
  final DatabaseHelper _db = DatabaseHelper.instance;
  
  List<Map<String, dynamic>> _facilities = [];
  List<Map<String, dynamic>> _mapMarkers = [];
  List<NavigationNode> _navigationNodes = [];
  List<NavigationEdge> _navigationEdges = [];
  
  NavigationRoute? _currentRoute;
  Map<String, dynamic>? _selectedFacility;
  int _selectedFloor = 1;
  List<int> _availableFloors = [];
  List<Map<String, dynamic>> _roomsOnFloor = [];
  
  bool _isLoading = true;
  bool _showRoute = false;
  bool _showLabels = true;
  String _mapViewMode = 'campus'; // 'campus' or 'building'
  
  // Animation controllers for route visualization
  late AnimationController _routeAnimationController;
  Animation<double>? _routeProgressAnimation;

  @override
  void initState() {
    super.initState();
    _routeAnimationController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    _loadData();
  }

  @override
  void dispose() {
    _transformationController.dispose();
    _routeAnimationController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    
    try {
      final facilities = await _db.getAllFacilities();
      final markers = await _db.getAllMapMarkers();
      final nodes = await _db.getAllNavigationNodes();
      final edges = await _db.getAllNavigationEdges();
      
      setState(() {
        _facilities = facilities;
        _mapMarkers = markers;
        _navigationNodes = nodes.map((n) => NavigationNode.fromMap(n)).toList();
        _navigationEdges = edges.map((e) => NavigationEdge.fromMap(e)).toList();
        _isLoading = false;
      });

      // If destination provided, calculate route
      if (widget.destinationFacilityId != null) {
        _calculateRouteToDestination();
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading map data: $e')),
        );
      }
    }
  }

  void _calculateRouteToDestination() {
    final pathfinder = DijkstraPathfinder(nodes: _navigationNodes, edges: _navigationEdges);
    
    // Find start node (main gate or entry point)
    final startNode = pathfinder.getMainEntrance();
    if (startNode == null) return;

    // Find destination node
    NavigationNode? destNode;
    if (widget.destinationRoomId != null) {
      destNode = _navigationNodes.firstWhere(
        (n) => n.roomId != null && n.roomId == widget.destinationRoomId,
        orElse: () => _navigationNodes.firstWhere(
          (n) => n.facilityId != null && n.facilityId == widget.destinationFacilityId,
          orElse: () => _navigationNodes.first,
        ),
      );
    } else if (widget.destinationFacilityId != null) {
      destNode = _navigationNodes.firstWhere(
        (n) => n.facilityId != null && n.facilityId == widget.destinationFacilityId,
        orElse: () => _navigationNodes.first,
      );
    }

    if (destNode != null) {
      final route = pathfinder.findShortestPath(startNode.id, destNode.id);
      if (route != null) {
        setState(() {
          _currentRoute = route;
          _showRoute = true;
        });
        _animateRoute();
      }
    }
  }

  void _animateRoute() {
    _routeProgressAnimation?.removeListener(_onRouteAnimationUpdate);
    _routeProgressAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _routeAnimationController,
        curve: Curves.easeInOut,
      ),
    );
    _routeProgressAnimation!.addListener(_onRouteAnimationUpdate);
    _routeAnimationController.forward(from: 0.0);
  }

  void _onRouteAnimationUpdate() {
    if (mounted) {
      setState(() {});
    }
  }

  void _onFacilityTap(Map<String, dynamic> facility) async {
    setState(() {
      _selectedFacility = facility;
      _mapViewMode = 'building';
      _selectedFloor = 1;
    });

    // Load floors and rooms for this facility
    final floors = await _db.getAvailableFloors(facility['id'] as int);
    final rooms = await _db.getRoomsByFacility(facility['id'] as int);
    
    setState(() {
      _availableFloors = floors;
      _roomsOnFloor = rooms;
    });

    _showFacilityDetails(facility);
  }

  void _showFacilityDetails(Map<String, dynamic> facility) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.4,
        minChildSize: 0.2,
        maxChildSize: 0.8,
        builder: (context, scrollController) {
          return Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
            ),
            child: Column(
              children: [
                // Drag handle
                Container(
                  margin: EdgeInsets.only(top: 8),
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                
                // Facility header
                Padding(
                  padding: EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Container(
                        padding: EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Color(0xFFFF9800).withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Icon(Icons.business, color: Color(0xFFFF9800), size: 28),
                      ),
                      SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              facility['name'] as String,
                              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                            ),
                            Text(
                              facility['building_code'] as String? ?? '',
                              style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                            ),
                          ],
                        ),
                      ),
                      IconButton(
                        icon: Icon(Icons.navigation, color: Color(0xFFFF9800)),
                        onPressed: () => _navigateToFacility(facility),
                      ),
                    ],
                  ),
                ),
                
                // Floor selector
                if (_availableFloors.length > 1)
                  Container(
                    height: 50,
                    padding: EdgeInsets.symmetric(horizontal: 16),
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      itemCount: _availableFloors.length,
                      itemBuilder: (context, index) {
                        final floor = _availableFloors[index];
                        final isSelected = floor == _selectedFloor;
                        return Padding(
                          padding: EdgeInsets.only(right: 8),
                          child: ChoiceChip(
                            label: Text(
                              floor == 1 ? 'Ground Floor' : 
                              floor == 2 ? '2nd Floor' :
                              floor == 3 ? '3rd Floor' : 'Floor $floor',
                            ),
                            selected: isSelected,
                            selectedColor: Color(0xFFFF9800),
                            labelStyle: TextStyle(
                              color: isSelected ? Colors.white : Colors.black,
                            ),
                            onSelected: (selected) {
                              if (selected) {
                                setState(() => _selectedFloor = floor);
                                Navigator.pop(context);
                                _showFacilityDetails(facility);
                              }
                            },
                          ),
                        );
                      },
                    ),
                  ),
                
                Divider(),
                
                // Rooms list
                Expanded(
                  child: ListView.builder(
                    controller: scrollController,
                    padding: EdgeInsets.all(16),
                    itemCount: _roomsOnFloor.where((r) => r['floor'] == _selectedFloor).length,
                    itemBuilder: (context, index) {
                      final rooms = _roomsOnFloor.where((r) => r['floor'] == _selectedFloor).toList();
                      final room = rooms[index];
                      return _buildRoomCard(room);
                    },
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildRoomCard(Map<String, dynamic> room) {
    final isOffice = (room['is_office'] as int? ?? 0) == 1;
    
    return Card(
      margin: EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Container(
          padding: EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: isOffice ? Colors.blue.withValues(alpha: 0.1) : Colors.green.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            isOffice ? Icons.work : Icons.meeting_room,
            color: isOffice ? Colors.blue : Colors.green,
          ),
        ),
        title: Text(room['name'] as String),
        subtitle: Text('${room['room_number'] ?? ''} • Capacity: ${room['capacity'] ?? 'N/A'}'),
        trailing: IconButton(
          icon: Icon(Icons.navigation, color: Color(0xFFFF9800)),
          onPressed: () => _navigateToRoom(room),
        ),
      ),
    );
  }

  void _navigateToFacility(Map<String, dynamic> facility) {
    final pathfinder = DijkstraPathfinder(nodes: _navigationNodes, edges: _navigationEdges);
    final startNode = pathfinder.getMainEntrance();
    final destNode = _navigationNodes.firstWhere(
      (n) => n.facilityId != null && n.facilityId == facility['id'],
      orElse: () => _navigationNodes.first,
    );

    if (startNode != null) {
      final route = pathfinder.findShortestPath(startNode.id, destNode.id);
      if (route != null) {
        setState(() {
          _currentRoute = route;
          _showRoute = true;
        });
        _animateRoute();
        Navigator.pop(context);
      }
    }
  }

  void _navigateToRoom(Map<String, dynamic> room) {
    final pathfinder = DijkstraPathfinder(nodes: _navigationNodes, edges: _navigationEdges);
    final startNode = pathfinder.getMainEntrance();
    final destNode = _navigationNodes.firstWhere(
      (n) => n.roomId != null && n.roomId == room['id'],
      orElse: () => _navigationNodes.firstWhere(
        (n) => n.facilityId != null && n.facilityId == room['facility_id'],
        orElse: () => _navigationNodes.first,
      ),
    );

    if (startNode != null) {
      final route = pathfinder.findShortestPath(startNode.id, destNode.id);
      if (route != null) {
        setState(() {
          _currentRoute = route;
          _showRoute = true;
        });
        _animateRoute();
        Navigator.pop(context);
      }
    }
  }

  void _zoomIn() {
    final currentScale = _transformationController.value.getMaxScaleOnAxis();
    _animateZoom(currentScale * 1.5);
  }

  void _zoomOut() {
    final currentScale = _transformationController.value.getMaxScaleOnAxis();
    _animateZoom(currentScale / 1.5);
  }

  void _animateZoom(double targetScale) {
    // Clamp scale between 0.5 and 4.0
    targetScale = targetScale.clamp(0.5, 4.0);
    
    final currentMatrix = _transformationController.value;
    final currentScale = currentMatrix.getMaxScaleOnAxis();
    
    final animation = Tween<double>(begin: currentScale, end: targetScale).animate(
      CurvedAnimation(
        parent: AnimationController(
          duration: Duration(milliseconds: 300),
          vsync: this,
        )..forward(),
        curve: Curves.easeOut,
      ),
    );

    animation.addListener(() {
      final scale = animation.value;
      final newMatrix = Matrix4.identity()..scaleByDouble(scale, scale, scale, 1.0);
      _transformationController.value = newMatrix;
    });
  }

  void _centerOnMyLocation() {
    // For demo, center on main gate
    final mainGate = _navigationNodes.firstWhere(
      (n) => n.nodeType == 'entrance',
      orElse: () => _navigationNodes.first,
    );
    
    // Calculate translation to center the node
    final scale = _transformationController.value.getMaxScaleOnAxis();
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;
    
    final translateX = screenWidth / 2 - mainGate.x * 400 * scale;
    final translateY = screenHeight / 2 - mainGate.y * 600 * scale;
    
    final newMatrix = Matrix4.identity()
      ..scaleByDouble(scale, scale, scale, 1.0)
      ..translateByDouble(translateX, translateY, 0.0, 0.0);
    
    _transformationController.value = newMatrix;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_mapViewMode == 'campus' ? 'Campus Map' : _selectedFacility?['name'] ?? 'Building Map'),
        backgroundColor: Color(0xFFFF9800),
        actions: [
          IconButton(
            icon: Icon(_showLabels ? Icons.label : Icons.label_off),
            onPressed: () => setState(() => _showLabels = !_showLabels),
            tooltip: 'Toggle Labels',
          ),
          IconButton(
            icon: Icon(Icons.layers),
            onPressed: () => _showMapLayersDialog(),
            tooltip: 'Map Layers',
          ),
          if (_mapViewMode == 'building')
            IconButton(
              icon: Icon(Icons.arrow_back),
              onPressed: () => setState(() {
                _mapViewMode = 'campus';
                _selectedFacility = null;
                _showRoute = false;
              }),
              tooltip: 'Back to Campus',
            ),
        ],
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator())
          : Stack(
              children: [
                // Interactive Map
                InteractiveViewer(
                  transformationController: _transformationController,
                  minScale: 0.5,
                  maxScale: 4.0,
                  boundaryMargin: EdgeInsets.all(100),
                  child: SizedBox(
                    width: 400,
                    height: 600,
                    child: CustomPaint(
                      size: Size(400, 600),
                      painter: CampusMapPainter(
                        facilities: _facilities,
                        markers: _mapMarkers,
                        navigationNodes: _navigationNodes,
                        navigationEdges: _navigationEdges,
                        currentRoute: _showRoute ? _currentRoute : null,
                        routeProgress: _routeProgressAnimation?.value ?? 0.0,
                        selectedFacility: _selectedFacility,
                        showLabels: _showLabels,
                        viewMode: _mapViewMode,
                        selectedFloor: _selectedFloor,
                        onFacilityTap: _onFacilityTap,
                      ),
                    ),
                  ),
                ),

                // Zoom Controls
                Positioned(
                  right: 16,
                  bottom: 120,
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withValues(alpha: 0.1),
                          blurRadius: 10,
                          offset: Offset(0, 4),
                        ),
                      ],
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconButton(
                          icon: Icon(Icons.add),
                          onPressed: _zoomIn,
                          tooltip: 'Zoom In',
                        ),
                        Divider(height: 1),
                        IconButton(
                          icon: Icon(Icons.remove),
                          onPressed: _zoomOut,
                          tooltip: 'Zoom Out',
                        ),
                      ],
                    ),
                  ),
                ),

                // GPS / Center Button
                Positioned(
                  right: 16,
                  bottom: 70,
                  child: FloatingActionButton.small(
                    heroTag: 'center',
                    backgroundColor: Colors.white,
                    foregroundColor: Color(0xFFFF9800),
                    onPressed: _centerOnMyLocation,
                    child: Icon(Icons.my_location),
                  ),
                ),

                // Route Info Panel
                if (_showRoute && _currentRoute != null)
                  Positioned(
                    left: 16,
                    right: 80,
                    bottom: 16,
                    child: Card(
                      elevation: 8,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      child: Padding(
                        padding: EdgeInsets.all(16),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(Icons.navigation, color: Color(0xFFFF9800)),
                                SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    'To: ${_currentRoute!.destination.name}',
                                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                                IconButton(
                                  icon: Icon(Icons.close, size: 20),
                                  onPressed: () => setState(() => _showRoute = false),
                                  padding: EdgeInsets.zero,
                                  constraints: BoxConstraints(),
                                ),
                              ],
                            ),
                            SizedBox(height: 8),
                            Row(
                              children: [
                                _buildRouteStat(Icons.straighten, _currentRoute!.formattedDistance),
                                SizedBox(width: 16),
                                _buildRouteStat(Icons.schedule, _currentRoute!.formattedTime),
                                SizedBox(width: 16),
                                _buildRouteStat(Icons.directions_walk, '${_currentRoute!.steps.length - 1} steps'),
                              ],
                            ),
                            if (_currentRoute!.steps.length > 1) ...[
                              SizedBox(height: 12),
                              Text(
                                'Next: ${_currentRoute!.steps[1].instruction}',
                                style: TextStyle(fontSize: 14, color: Colors.grey[700]),
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                  ),

                // Legend
                if (!_showRoute)
                  Positioned(
                    left: 16,
                    bottom: 16,
                    child: Card(
                      elevation: 4,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      child: Padding(
                        padding: EdgeInsets.all(12),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text('Legend', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                            SizedBox(height: 8),
                            _buildLegendItem(Icons.business, 'Building', Colors.blue),
                            _buildLegendItem(Icons.computer, 'Computer Lab', Colors.green),
                            _buildLegendItem(Icons.work, 'Office', Colors.orange),
                            _buildLegendItem(Icons.restaurant, 'Facility', Colors.purple),
                          ],
                        ),
                      ),
                    ),
                  ),
              ],
            ),
      floatingActionButton: _showRoute
          ? FloatingActionButton.extended(
              backgroundColor: Color(0xFFFF9800),
              onPressed: () => _showTurnByTurnDirections(),
              icon: Icon(Icons.directions),
              label: Text('Directions'),
            )
          : null,
    );
  }

  Widget _buildRouteStat(IconData icon, String value) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 16, color: Colors.grey[600]),
        SizedBox(width: 4),
        Text(value, style: TextStyle(fontSize: 14, color: Colors.grey[800])),
      ],
    );
  }

  Widget _buildLegendItem(IconData icon, String label, Color color) {
    return Padding(
      padding: EdgeInsets.only(bottom: 4),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: color),
          SizedBox(width: 6),
          Text(label, style: TextStyle(fontSize: 11)),
        ],
      ),
    );
  }

  void _showMapLayersDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Map Layers'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            SwitchListTile(
              title: Text('Show Buildings'),
              value: true,
              onChanged: (v) {},
            ),
            SwitchListTile(
              title: Text('Show Walkways'),
              value: true,
              onChanged: (v) {},
            ),
            SwitchListTile(
              title: Text('Show Labels'),
              value: _showLabels,
              onChanged: (v) {
                setState(() => _showLabels = v);
                Navigator.pop(context);
              },
            ),
            SwitchListTile(
              title: Text('Accessibility Mode'),
              value: false,
              onChanged: (v) {},
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showTurnByTurnDirections() {
    if (_currentRoute == null) return;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        minChildSize: 0.5,
        maxChildSize: 0.9,
        builder: (context, scrollController) {
          return Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
            ),
            child: Column(
              children: [
                Container(
                  margin: EdgeInsets.only(top: 8),
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                Padding(
                  padding: EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Icon(Icons.navigation, color: Color(0xFFFF9800), size: 32),
                      SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Directions to ${_currentRoute!.destination.name}',
                              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                            ),
                            Text(
                              '${_currentRoute!.formattedDistance} • ${_currentRoute!.formattedTime}',
                              style: TextStyle(color: Colors.grey[600]),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                Divider(),
                Expanded(
                  child: ListView.builder(
                    controller: scrollController,
                    itemCount: _currentRoute!.steps.length,
                    itemBuilder: (context, index) {
                      final step = _currentRoute!.steps[index];
                      return ListTile(
                        leading: CircleAvatar(
                          backgroundColor: index == 0 
                              ? Colors.green 
                              : index == _currentRoute!.steps.length - 1 
                                  ? Colors.red 
                                  : Color(0xFFFF9800),
                          child: Text(
                            '${step.stepNumber}',
                            style: TextStyle(color: Colors.white, fontSize: 12),
                          ),
                        ),
                        title: Text(step.instruction),
                        subtitle: step.distance != null 
                            ? Text('${step.distance!.toStringAsFixed(0)}m')
                            : null,
                      );
                    },
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}

/// Custom painter for the campus map
class CampusMapPainter extends CustomPainter {
  final List<Map<String, dynamic>> facilities;
  final List<Map<String, dynamic>> markers;
  final List<NavigationNode> navigationNodes;
  final List<NavigationEdge> navigationEdges;
  final NavigationRoute? currentRoute;
  final double routeProgress;
  final Map<String, dynamic>? selectedFacility;
  final bool showLabels;
  final String viewMode;
  final int selectedFloor;
  final Function(Map<String, dynamic>)? onFacilityTap;

  CampusMapPainter({
    required this.facilities,
    required this.markers,
    required this.navigationNodes,
    required this.navigationEdges,
    this.currentRoute,
    this.routeProgress = 0.0,
    this.selectedFacility,
    this.showLabels = true,
    this.viewMode = 'campus',
    this.selectedFloor = 1,
    this.onFacilityTap,
  });

  @override
  void paint(Canvas canvas, Size size) {
    // Draw background
    final bgPaint = Paint()..color = Color(0xFFF5F5F5);
    canvas.drawRect(Offset.zero & size, bgPaint);

    // Draw walkways/pathways
    _drawWalkways(canvas, size);

    // Draw route if active
    if (currentRoute != null && currentRoute!.nodes.length > 1) {
      _drawRoute(canvas, size);
    }

    // Draw buildings
    _drawBuildings(canvas, size);

    // Draw markers
    _drawMarkers(canvas, size);

    // Draw nodes
    _drawNodes(canvas, size);
  }

  void _drawWalkways(Canvas canvas, Size size) {
    final walkwayPaint = Paint()
      ..color = Colors.grey[400]!
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke;

    for (var edge in navigationEdges) {
      final fromNode = navigationNodes.firstWhere((n) => n.id == edge.fromNodeId);
      final toNode = navigationNodes.firstWhere((n) => n.id == edge.toNodeId);

      final fromOffset = Offset(fromNode.x * size.width, fromNode.y * size.height);
      final toOffset = Offset(toNode.x * size.width, toNode.y * size.height);

      canvas.drawLine(fromOffset, toOffset, walkwayPaint);
    }
  }

  void _drawRoute(Canvas canvas, Size size) {
    if (currentRoute == null || currentRoute!.nodes.length < 2) return;

    // Draw completed portion of route
    final completedPaint = Paint()
      ..color = Color(0xFFFF9800)
      ..strokeWidth = 6
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final remainingPaint = Paint()
      ..color = Color(0xFFFF9800).withValues(alpha: 0.3)
      ..strokeWidth = 6
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    // Calculate how many segments to show as completed
    final totalSegments = currentRoute!.nodes.length - 1;
    final completedSegments = (totalSegments * routeProgress).floor();

    for (var i = 0; i < totalSegments; i++) {
      final fromNode = currentRoute!.nodes[i];
      final toNode = currentRoute!.nodes[i + 1];

      final fromOffset = Offset(fromNode.x * size.width, fromNode.y * size.height);
      final toOffset = Offset(toNode.x * size.width, toNode.y * size.height);

      final paint = i < completedSegments ? completedPaint : remainingPaint;
      canvas.drawLine(fromOffset, toOffset, paint);
    }

    // Draw start marker
    final startPaint = Paint()..color = Colors.green;
    final startOffset = Offset(
      currentRoute!.nodes.first.x * size.width,
      currentRoute!.nodes.first.y * size.height,
    );
    canvas.drawCircle(startOffset, 10, startPaint);

    // Draw destination marker
    final destPaint = Paint()..color = Colors.red;
    final destOffset = Offset(
      currentRoute!.nodes.last.x * size.width,
      currentRoute!.nodes.last.y * size.height,
    );
    canvas.drawCircle(destOffset, 10, destPaint);
  }

  void _drawBuildings(Canvas canvas, Size size) {
    final buildingPaint = Paint()
      ..color = Colors.blue.withValues(alpha: 0.3)
      ..style = PaintingStyle.fill;

    final buildingBorderPaint = Paint()
      ..color = Colors.blue
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    final selectedBuildingPaint = Paint()
      ..color = Color(0xFFFF9800).withValues(alpha: 0.4)
      ..style = PaintingStyle.fill;

    for (var facility in facilities) {
      // Find associated marker for position
      final marker = markers.firstWhere(
        (m) => m['facility_id'] == facility['id'],
        orElse: () => {'x_position': 0.5, 'y_position': 0.5},
      );

      final x = (marker['x_position'] as num?)?.toDouble() ?? 0.5;
      final y = (marker['y_position'] as num?)?.toDouble() ?? 0.5;
      final isSelected = selectedFacility?['id'] == facility['id'];

      // Draw building shape
      final buildingSize = 60.0;
      final rect = Rect.fromCenter(
        center: Offset(x * size.width, y * size.height),
        width: buildingSize,
        height: buildingSize * 0.8,
      );

      final rrect = RRect.fromRectAndRadius(rect, Radius.circular(8));

      canvas.drawRRect(rrect, isSelected ? selectedBuildingPaint : buildingPaint);
      canvas.drawRRect(rrect, buildingBorderPaint);

      // Draw building label
      if (showLabels) {
        final textSpan = TextSpan(
          text: facility['building_code'] as String? ?? facility['name']?.toString().substring(0, 3) ?? '',
          style: TextStyle(
            color: isSelected ? Colors.white : Colors.blue[800],
            fontSize: 12,
            fontWeight: FontWeight.bold,
          ),
        );
        final textPainter = TextPainter(
          text: textSpan,
          textDirection: TextDirection.ltr,
        );
        textPainter.layout();
        textPainter.paint(
          canvas,
          Offset(
            x * size.width - textPainter.width / 2,
            y * size.height - textPainter.height / 2,
          ),
        );
      }
    }
  }

  void _drawMarkers(Canvas canvas, Size size) {
    final markerPaint = Paint()..color = Color(0xFFFF9800);

    for (var marker in markers) {
      final x = (marker['x_position'] as num).toDouble();
      final y = (marker['y_position'] as num).toDouble();
      final type = marker['type'] as String? ?? 'facility';

      final center = Offset(x * size.width, y * size.height);

      // Draw marker based on type
      switch (type) {
        case 'entrance':
          // Draw main gate marker
          final path = Path()
            ..moveTo(center.dx, center.dy - 15)
            ..lineTo(center.dx - 10, center.dy + 10)
            ..lineTo(center.dx + 10, center.dy + 10)
            ..close();
          final entrancePaint = Paint()..color = Colors.green;
          canvas.drawPath(path, entrancePaint);
          break;
        case 'facility':
        default:
          // Draw circle marker
          canvas.drawCircle(center, 8, markerPaint);
          canvas.drawCircle(center, 5, Paint()..color = Colors.white);
          break;
      }
    }
  }

  void _drawNodes(Canvas canvas, Size size) {
    // Draw navigation nodes (small dots for debugging/development)
    final nodePaint = Paint()
      ..color = Colors.grey.withValues(alpha: 0.5)
      ..style = PaintingStyle.fill;

    for (var node in navigationNodes) {
      final offset = Offset(node.x * size.width, node.y * size.height);
      canvas.drawCircle(offset, 4, nodePaint);
    }
  }

  @override
  bool shouldRepaint(covariant CampusMapPainter oldDelegate) {
    return oldDelegate.routeProgress != routeProgress ||
           oldDelegate.selectedFacility != selectedFacility ||
           oldDelegate.showLabels != showLabels ||
           oldDelegate.currentRoute != currentRoute;
  }

  @override
  bool hitTest(Offset position) => true;
}
