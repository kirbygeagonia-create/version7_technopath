import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'database_helper_v2.dart';
import 'chatbot_database_helper.dart';
import 'api_service.dart';
import 'qr/qr_scanner_screen.dart';
import 'map/campus_map_screen.dart';

void main() {
  runApp(const GuideMapApp());
}

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with TickerProviderStateMixin {
  late AnimationController _fadeController;
  late AnimationController _scaleController;
  late Animation<double> _fadeAnimation;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();

    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    _scaleController = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _fadeController,
        curve: Curves.easeIn,
      ),
    );

    _scaleAnimation = Tween<double>(begin: 0.5, end: 1.0).animate(
      CurvedAnimation(
        parent: _scaleController,
        curve: Curves.elasticOut,
      ),
    );

    _fadeController.forward();
    _scaleController.forward();

    Timer(const Duration(seconds: 3), () {
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (_) => const MainNavigationShellWrapper(),
          ),
        );
      }
    });
  }

  @override
  void dispose() {
    _fadeController.dispose();
    _scaleController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFF9800),
      body: Center(
        child: AnimatedBuilder(
          animation: Listenable.merge([_fadeController, _scaleController]),
          builder: (context, child) {
            return FadeTransition(
              opacity: _fadeAnimation,
              child: ScaleTransition(
                scale: _scaleAnimation,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      width: 180,
                      height: 180,
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.3),
                            blurRadius: 20,
                            offset: const Offset(0, 10),
                          ),
                        ],
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(20),
                        child: Image.asset(
                          'lib/map/SEAITlogo.png',
                          fit: BoxFit.contain,
                          errorBuilder: (context, error, stackTrace) {
                            return const Icon(
                              Icons.school,
                              size: 80,
                              color: Color(0xFFFF9800),
                            );
                          },
                        ),
                      ),
                    ),
                    const SizedBox(height: 30),
                    const Text(
                      'SEAIT Campus Guide',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 40),
                    SizedBox(
                      width: 40,
                      height: 40,
                      child: CircularProgressIndicator(
                        valueColor: AlwaysStoppedAnimation<Color>(
                          Colors.white.withValues(alpha: 0.9),
                        ),
                        strokeWidth: 3,
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}

class MainNavigationShellWrapper extends StatefulWidget {
  const MainNavigationShellWrapper({super.key});

  @override
  State<MainNavigationShellWrapper> createState() => _MainNavigationShellWrapperState();
}

class _MainNavigationShellWrapperState extends State<MainNavigationShellWrapper> {
  bool _isDarkMode = false;

  @override
  Widget build(BuildContext context) {
    return MainNavigationShell(
      isDarkMode: _isDarkMode,
      onThemeChanged: (isDark) => setState(() => _isDarkMode = isDark),
    );
  }
}

class GuideMapApp extends StatelessWidget {
  const GuideMapApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SEAIT Campus Guide',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: const Color(0xFFFF9800),
        useMaterial3: true,
        fontFamily: 'Roboto',
        cardTheme: CardThemeData(
          elevation: 2,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        ),
        appBarTheme: const AppBarTheme(
          centerTitle: true,
          elevation: 0,
          backgroundColor: Color(0xFFFF9800),
          foregroundColor: Colors.white,
        ),
        bottomNavigationBarTheme: const BottomNavigationBarThemeData(
          backgroundColor: Colors.white,
          selectedItemColor: Color(0xFFFF9800),
          unselectedItemColor: Colors.grey,
          type: BottomNavigationBarType.fixed,
          elevation: 8,
        ),
      ),
      darkTheme: ThemeData.dark(
        useMaterial3: true,
      ).copyWith(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFFFF9800),
          brightness: Brightness.dark,
        ),
        appBarTheme: const AppBarTheme(
          centerTitle: true,
          elevation: 0,
          backgroundColor: Color(0xFFFF9800),
          foregroundColor: Colors.white,
        ),
        bottomNavigationBarTheme: const BottomNavigationBarThemeData(
          backgroundColor: Color(0xFF1C1C1C),
          selectedItemColor: Color(0xFFFF9800),
          unselectedItemColor: Colors.grey,
          type: BottomNavigationBarType.fixed,
          elevation: 8,
        ),
      ),
      home: const SplashScreen(),
    );
  }
}

class MainNavigationShell extends StatefulWidget {
  const MainNavigationShell({
    super.key,
    required this.isDarkMode,
    required this.onThemeChanged,
  });

  final bool isDarkMode;
  final ValueChanged<bool> onThemeChanged;

  @override
  State<MainNavigationShell> createState() => _MainNavigationShellState();
}

class _MainNavigationShellState extends State<MainNavigationShell> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final pages = <Widget>[
      const HomeScreen(),
      const NavigateScreen(),
      SettingsScreen(
        isDarkMode: widget.isDarkMode,
        onThemeChanged: widget.onThemeChanged,
      ),
    ];

    return Scaffold(
      body: IndexedStack(index: _currentIndex, children: pages),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) => setState(() => _currentIndex = index),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.map), label: 'Navigate'),
          NavigationDestination(icon: Icon(Icons.settings), label: 'Settings'),
        ],
      ),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<Map<String, dynamic>> facilities = [];
  List<Map<String, dynamic>> rooms = [];
  List<Map<String, dynamic>> mapMarkers = [];
  String selectedFacility = '';
  String selectedRoom = '';
  String searchText = '';
  String currentLocation = '';
  bool isFacilitiesExpanded = false;
  bool isRoomsExpanded = false;
  int unreadNotifications = 0;
  static const String mapImagePath = 'assets/maps/Example1.jpg';
  final TransformationController _transformationController = TransformationController();

  void _zoomIn() {
    final currentScale = _transformationController.value.getMaxScaleOnAxis();
    final newScale = (currentScale * 1.2).clamp(0.8, 4.0);
    _transformationController.value = Matrix4.diagonal3Values(newScale, newScale, 1.0);
  }

  void _zoomOut() {
    final currentScale = _transformationController.value.getMaxScaleOnAxis();
    final newScale = (currentScale / 1.2).clamp(0.8, 4.0);
    _transformationController.value = Matrix4.diagonal3Values(newScale, newScale, 1.0);
  }

  @override
  void initState() {
    super.initState();
    _loadData();
    _loadNotificationCount();
    // Auto-refresh notification count every 5 seconds when on home screen
    _notificationTimer = Timer.periodic(const Duration(seconds: 5), (_) {
      if (mounted) _loadNotificationCount();
    });
  }

  @override
  void dispose() {
    _transformationController.dispose();
    _notificationTimer?.cancel();
    super.dispose();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _loadNotificationCount();
  }

  Timer? _notificationTimer;

  Future<void> _loadData() async {
    final db = DatabaseHelper.instance;
    final facs = await db.getAllFacilities();
    final rms = await db.getAllRooms();
    final markers = await db.getAllMapMarkers();
    setState(() {
      facilities = facs;
      rooms = rms;
      mapMarkers = markers.isNotEmpty ? markers : _generateDefaultMarkers();
      if (facs.isNotEmpty) selectedFacility = facs.first['name'];
      if (rms.isNotEmpty) selectedRoom = rms.first['name'];
    });
  }

  List<Map<String, dynamic>> _generateDefaultMarkers() {
    // Generate default markers based on facilities and rooms
    final List<Map<String, dynamic>> defaultMarkers = [];
    
    // Building markers (positioned at different locations on the map)
    final buildingPositions = [
      {'name': 'Building', 'x': 0.3, 'y': 0.4, 'type': 'facility'},
      {'name': 'RST Building', 'x': 0.6, 'y': 0.3, 'type': 'facility'},
      {'name': 'JST Building', 'x': 0.4, 'y': 0.6, 'type': 'facility'},
      {'name': 'MST Building', 'x': 0.7, 'y': 0.5, 'type': 'facility'},
    ];
    
    // Room markers (CL1-CL4)
    final roomPositions = [
      {'name': 'CL1', 'x': 0.25, 'y': 0.35, 'type': 'room'},
      {'name': 'CL2', 'x': 0.35, 'y': 0.35, 'type': 'room'},
      {'name': 'CL3', 'x': 0.25, 'y': 0.45, 'type': 'room'},
      {'name': 'CL4', 'x': 0.35, 'y': 0.45, 'type': 'room'},
    ];
    
    defaultMarkers.addAll(buildingPositions);
    defaultMarkers.addAll(roomPositions);
    
    return defaultMarkers;
  }

  Future<void> _loadNotificationCount() async {
    final count = await DatabaseHelper.instance.getUnreadNotificationCount();
    setState(() => unreadNotifications = count);
  }

  Widget _buildShadowIconButton({
    required VoidCallback onPressed,
    required IconData icon,
    required Color color,
    double iconSize = 24,
  }) {
    return Opacity(
      opacity: 0.9,
      child: Container(
        decoration: const BoxDecoration(
          shape: BoxShape.circle,
          color: Colors.black54,
        ),
        child: IconButton(
          onPressed: onPressed,
          icon: Icon(icon, size: iconSize, color: color),
        ),
      ),
    );
  }

  void _showLocateDialog() {
    final controller = TextEditingController(text: currentLocation);
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Where are you now?'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            hintText: 'Enter your current location',
            prefixIcon: Icon(Icons.location_on),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              setState(() => currentLocation = controller.text);
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Location set to: ${controller.text}')),
              );
            },
            child: const Text('Set Location'),
          ),
        ],
      ),
    );
  }

  void _showRatingDialog() {
    int rating = 5;
    final commentController = TextEditingController();
    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Rate this App'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(5, (index) {
                  return IconButton(
                    onPressed: () => setDialogState(() => rating = index + 1),
                    icon: Icon(
                      index < rating ? Icons.star : Icons.star_border,
                      color: Colors.amber,
                      size: 32,
                    ),
                  );
                }),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: commentController,
                decoration: const InputDecoration(
                  hintText: 'Leave a comment (optional)',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                await DatabaseHelper.instance.insertRating({
                  'user_id': 1,
                  'rating': rating,
                  'comment': commentController.text,
                });
                if (!context.mounted) return;
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Thank you for your rating!')),
                );
              },
              child: const Text('Submit'),
            ),
          ],
        ),
      ),
    );
  }

  void _performSearch(String query) {
    if (query.isEmpty) return;
    
    final lowerQuery = query.toLowerCase();
    final allLocations = [
      ...facilities.map((f) => {'name': f['name'] as String, 'type': 'Facility', 'info': f['description'] ?? 'Campus facility'}),
      ...rooms.map((r) => {'name': r['name'] as String, 'type': 'Room', 'info': r['description'] ?? 'Classroom/Lab'}),
    ];
    
    final results = allLocations.where((loc) {
      final name = loc['name']!.toLowerCase();
      final info = loc['info']!.toLowerCase();
      return name.contains(lowerQuery) || info.contains(lowerQuery);
    }).toList();

    if (results.isEmpty) {
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('No Results'),
          content: Text('No locations found for "$query"\n\nTry searching for:\n• CL1, CL2, CL3, CL4, CL5, CL6\n• CR1, CR2, CR3, CR4\n• MST Building, JST Building, RST Building\n• Library, Registrar, Cafeteria'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('OK'),
            ),
          ],
        ),
      );
    } else {
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: Text('Search Results (${results.length})'),
          content: SizedBox(
            width: double.maxFinite,
            child: ListView.builder(
              shrinkWrap: true,
              itemCount: results.length,
              itemBuilder: (context, index) {
                final result = results[index];
                return ListTile(
                  leading: Icon(
                    result['type'] == 'Facility' ? Icons.business : Icons.meeting_room,
                    color: Colors.orange,
                  ),
                  title: Text(result['name']!),
                  subtitle: Text('${result['type']} - ${result['info']}'),
                  onTap: () {
                    Navigator.pop(context);
                    if (result['type'] == 'Facility') {
                      setState(() => selectedFacility = result['name']!);
                    } else {
                      setState(() => selectedRoom = result['name']!);
                    }
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Selected: ${result['name']}')),
                    );
                  },
                );
              },
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Close'),
            ),
          ],
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final facilityNames = facilities.map((f) => f['name'] as String).toList();
    final roomNames = rooms.map((r) => r['name'] as String).toList();

    return Stack(
      children: [
        // Map background - full screen
        Positioned.fill(
          child: InteractiveViewer(
            transformationController: _transformationController,
            minScale: 0.8,
            maxScale: 4,
            child: Image.asset(
              mapImagePath,
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) => Container(
                color: Colors.orange.shade100,
                alignment: Alignment.center,
                child: const SizedBox.shrink(),
              ),
            ),
          ),
        ),
        // Zoom controls
        Positioned(
          right: 16,
          top: 120,
          child: Column(
            children: [
              _buildShadowIconButton(
                onPressed: _zoomIn,
                icon: Icons.zoom_in,
                color: Colors.white,
              ),
              const SizedBox(height: 8),
              _buildShadowIconButton(
                onPressed: _zoomOut,
                icon: Icons.zoom_out,
                color: Colors.white,
              ),
            ],
          ),
        ),
        // Map markers layer
        ...mapMarkers.where((marker) {
          // Show all markers, or filter by selected facility/room
          final markerName = marker['name'] as String;
          final markerType = marker['type'] as String;
          
          if (markerType == 'facility' && selectedFacility.isNotEmpty) {
            return markerName == selectedFacility;
          }
          if (markerType == 'room' && selectedRoom.isNotEmpty) {
            return markerName == selectedRoom;
          }
          return true; // Show all if nothing selected
        }).map((marker) {
          final x = (marker['x'] as num?)?.toDouble() ?? 0.5;
          final y = (marker['y'] as num?)?.toDouble() ?? 0.5;
          final name = marker['name'] as String? ?? 'Unknown';
          final type = marker['type'] as String? ?? 'facility';
          
          return Positioned(
            left: x * MediaQuery.of(context).size.width,
            top: y * MediaQuery.of(context).size.height * 0.7, // Account for UI overlays
            child: GestureDetector(
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(name), duration: const Duration(seconds: 1)),
                );
              },
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    type == 'facility' ? Icons.business : Icons.meeting_room,
                    color: type == 'facility' ? Colors.orange : Colors.green,
                    size: 32,
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.7),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      name,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          );
        }),
        // Top bar with Facilities and Room
        Positioned(
          top: 50,
          left: 12,
          right: 12,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: _ExpandableCard(
                      title: 'Facilities',
                      isExpanded: isFacilitiesExpanded,
                      onTap: () => setState(() {
                        isFacilitiesExpanded = !isFacilitiesExpanded;
                        isRoomsExpanded = false;
                      }),
                      items: facilityNames,
                      selectedItem: selectedFacility,
                      onItemSelected: (value) => setState(() {
                        selectedFacility = value;
                        isFacilitiesExpanded = false;
                      }),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _ExpandableCard(
                      title: 'Room',
                      isExpanded: isRoomsExpanded,
                      onTap: () => setState(() {
                        isRoomsExpanded = !isRoomsExpanded;
                        isFacilitiesExpanded = false;
                      }),
                      items: roomNames,
                      selectedItem: selectedRoom,
                      onItemSelected: (value) => setState(() {
                        selectedRoom = value;
                        isRoomsExpanded = false;
                      }),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        // Bottom section with menu, icons, and search bar - now closer to nav bar
        Positioned(
          left: 12,
          right: 12,
          bottom: 16,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Icons row (Menu, Locate, Rate, Notification, Chatbot) - now at top
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // Menu button
                  FloatingActionButton.small(
                    heroTag: 'menu-button',
                    backgroundColor: Colors.black54,
                    onPressed: () {
                      showModalBottomSheet(
                        context: context,
                        builder: (context) => SafeArea(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              ListTile(
                                leading: const Icon(Icons.business),
                                title: const Text('Building Information'),
                                onTap: () {
                                  Navigator.pop(context);
                                  Navigator.of(context).push(
                                    MaterialPageRoute(builder: (_) => const BuildingInfoScreen()),
                                  );
                                },
                              ),
                              ListTile(
                                leading: const Icon(Icons.admin_panel_settings),
                                title: const Text('Rooms Info'),
                                onTap: () {
                                  Navigator.pop(context);
                                  Navigator.of(context).push(
                                    MaterialPageRoute(builder: (_) => const AdminInfoScreen()),
                                  );
                                },
                              ),
                              ListTile(
                                leading: const Icon(Icons.school),
                                title: const Text('Instructor Info'),
                                onTap: () {
                                  Navigator.pop(context);
                                  Navigator.of(context).push(
                                    MaterialPageRoute(builder: (_) => const InstructorInfoScreen()),
                                  );
                                },
                              ),
                              ListTile(
                                leading: const Icon(Icons.people),
                                title: const Text('Employees'),
                                onTap: () {
                                  Navigator.pop(context);
                                  Navigator.of(context).push(
                                    MaterialPageRoute(builder: (_) => const EmployeesScreen()),
                                  );
                                },
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                    child: const Icon(Icons.menu, color: Colors.white),
                  ),
                  // Right side icons
                  Row(
                    children: [
                      // Locate icon
                      _buildShadowIconButton(
                        onPressed: _showLocateDialog,
                        icon: Icons.my_location,
                        color: currentLocation.isNotEmpty ? Colors.green : Colors.white,
                      ),
                      // Rate icon
                      _buildShadowIconButton(
                        onPressed: _showRatingDialog,
                        icon: Icons.star_outline,
                        color: Colors.white,
                      ),
                      // Notification icon with badge
                      Stack(
                        children: [
                          _buildShadowIconButton(
                            onPressed: () {
                              Navigator.of(context).push(
                                MaterialPageRoute(builder: (_) => const NotificationsScreen()),
                              ).then((_) => _loadNotificationCount());
                            },
                            icon: Icons.notifications_outlined,
                            color: Colors.white,
                          ),
                          if (unreadNotifications > 0)
                            Positioned(
                              right: 4,
                              top: 4,
                              child: Container(
                                padding: const EdgeInsets.all(4),
                                decoration: const BoxDecoration(
                                  color: Colors.red,
                                  shape: BoxShape.circle,
                                ),
                                child: Text(
                                  unreadNotifications.toString(),
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ),
                        ],
                      ),
                      // Chatbot icon
                      _buildShadowIconButton(
                        onPressed: () {
                          Navigator.of(context).push(
                            MaterialPageRoute(builder: (_) => const ChatbotScreen()),
                          );
                        },
                        icon: Icons.smart_toy,
                        color: Colors.white,
                        iconSize: 28,
                      ),
                      // QR Scanner icon
                      _buildShadowIconButton(
                        onPressed: () async {
                          final result = await Navigator.of(context).push(
                            MaterialPageRoute(builder: (_) => const QRScannerScreen()),
                          );
                          if (!mounted) return;
                          if (result != null && result is Map) {
                            if (result['action'] == 'open_map') {
                              Navigator.of(context).push(
                                MaterialPageRoute(
                                  builder: (_) => CampusMapScreen(
                                    entryPoint: result['entry_point'],
                                  ),
                                ),
                              );
                            }
                          }
                        },
                        icon: Icons.qr_code_scanner,
                        color: Colors.white,
                        iconSize: 28,
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 12),
              // Search bar - now below icons with 60% opacity
              Opacity(
                opacity: 0.6,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.surface,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.3),
                        blurRadius: 12,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.search),
                      Expanded(
                        child: TextField(
                          onChanged: (value) => setState(() => searchText = value),
                          onSubmitted: (value) => _performSearch(value),
                          decoration: const InputDecoration(
                            hintText: 'Search location, building, room...',
                            border: InputBorder.none,
                            contentPadding: EdgeInsets.symmetric(horizontal: 12),
                          ),
                        ),
                      ),
                      if (searchText.isNotEmpty)
                        IconButton(
                          icon: const Icon(Icons.clear, size: 20),
                          onPressed: () => setState(() => searchText = ''),
                        ),
                      IconButton(
                        icon: const Icon(Icons.arrow_forward, size: 20),
                        onPressed: () => _performSearch(searchText),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _ExpandableCard extends StatelessWidget {
  const _ExpandableCard({
    required this.title,
    required this.isExpanded,
    required this.onTap,
    required this.items,
    required this.selectedItem,
    required this.onItemSelected,
  });

  final String title;
  final bool isExpanded;
  final VoidCallback onTap;
  final List<String> items;
  final String selectedItem;
  final ValueChanged<String> onItemSelected;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        GestureDetector(
          onTap: onTap,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surface.withValues(alpha: 0.95),
              borderRadius: BorderRadius.circular(14),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.2),
                  blurRadius: 8,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
                Icon(isExpanded ? Icons.expand_less : Icons.expand_more),
              ],
            ),
          ),
        ),
        if (isExpanded)
          Container(
            margin: const EdgeInsets.only(top: 4),
            padding: const EdgeInsets.only(bottom: 8),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surface.withValues(alpha: 0.95),
              borderRadius: BorderRadius.circular(14),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.15),
                  blurRadius: 6,
                  offset: const Offset(0, 3),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: items.map((item) {
                final isSelected = item == selectedItem;
                return ListTile(
                  dense: true,
                  title: Text(
                    item,
                    style: TextStyle(
                      color: isSelected ? Theme.of(context).colorScheme.primary : null,
                      fontWeight: isSelected ? FontWeight.bold : null,
                    ),
                  ),
                  trailing: isSelected ? const Icon(Icons.check, size: 18) : null,
                  onTap: () => onItemSelected(item),
                );
              }).toList(),
            ),
          ),
      ],
    );
  }
}

class NavigateScreen extends StatefulWidget {
  const NavigateScreen({super.key});

  @override
  State<NavigateScreen> createState() => _NavigateScreenState();
}

class _NavigateScreenState extends State<NavigateScreen> {
  final TransformationController _transformationController = TransformationController();
  
  // Navigation form data
  String fromLocation = '';
  String toLocation = '';
  String fromFloor = '1st Floor';
  String toFloor = '1st Floor';
  String fromRoomNumber = '';
  String toRoomNumber = '';
  String fromRoomType = '';
  String toRoomType = '';
  bool isFormVisible = true; // Toggle for showing/hiding navigation form
  
  // Available options
  final List<String> locations = [
    'Canteen', 'Building', 'RST Building', 'JST Building', 'MST Building',
    'Library', 'Registrar Office', 'Cafeteria',
    'CL1', 'CL2', 'CL3', 'CL4', 'CL5', 'CL6',
    'CR1', 'CR2', 'CR3', 'CR4',
    'Computer Lab 1', 'Computer Lab 2'
  ];
  final List<String> floors = ['1st Floor', '2nd Floor', '3rd Floor', '4th Floor'];
  final List<String> roomTypes = ['CL1', 'CL2', 'CL3', 'CL4', 'CL5', 'CL6', 'CR1', 'CR2', 'CR3', 'CR4', 'Computer Lab', 'Lecture Room', 'Office', 'Lab'];
  
  // Building floor info - MST & JST = 4 floors, RST = 3 floors, others = 1-2 floors
  final Map<String, int> buildingFloors = {
    'MST Building': 4,
    'JST Building': 4,
    'RST Building': 3,
    'Building': 4,
    'Library': 2,
    'Registrar Office': 1,
    'Cafeteria': 1,
    'Canteen': 1,
    'CL1': 1, 'CL2': 1, 'CL3': 1, 'CL4': 1,
    'CL5': 2, 'CL6': 2,
    'CR1': 1, 'CR2': 1, 'CR3': 1, 'CR4': 1,
    'Computer Lab 1': 1, 'Computer Lab 2': 1,
  };

  @override
  void dispose() {
    _transformationController.dispose();
    super.dispose();
  }

  List<String> getAvailableFloors(String location) {
    final maxFloors = buildingFloors[location] ?? 4;
    return floors.take(maxFloors).toList();
  }

  @override
  Widget build(BuildContext context) {
    // Use the new interactive campus map with navigation
    return const CampusMapScreen();
  }
}

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({
    super.key,
    required this.isDarkMode,
    required this.onThemeChanged,
  });

  final bool isDarkMode;
  final ValueChanged<bool> onThemeChanged;

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  // Predefined campus facilities with detailed info
  final List<Map<String, dynamic>> campusFacilities = [
    {
      'name': 'MST Building',
      'type': 'Academic Building',
      'description': 'Main Science and Technology Building',
      'floors': 4,
      'features': ['Computer Labs CL1, CL2 (1st Floor)', 'Computer Labs CL5, CL6 (2nd Floor)', 'Lecture Rooms CR1, CR2', 'Administrative Offices'],
      'icon': Icons.business,
    },
    {
      'name': 'JST Building',
      'type': 'Academic Building',
      'description': 'Junior Science and Technology Building',
      'floors': 4,
      'features': ['Classrooms', 'Laboratories', 'Faculty Offices', 'Student Lounges'],
      'icon': Icons.business,
    },
    {
      'name': 'RST Building',
      'type': 'Research Building',
      'description': 'Research Science and Technology Building',
      'floors': 3,
      'features': ['Research Labs', 'Graduate Studies', 'Specialized Equipment', 'Conference Rooms'],
      'icon': Icons.science,
    },
    {
      'name': 'Library',
      'type': 'Facility',
      'description': 'Main Campus Library',
      'floors': 2,
      'features': ['Book Lending', 'Study Areas', 'Research Materials', 'Digital Resources', 'Reading Rooms'],
      'icon': Icons.library_books,
    },
    {
      'name': 'Registrar Office',
      'type': 'Administrative',
      'description': 'Student Services and Records',
      'floors': 1,
      'features': ['Enrollment Services', 'Academic Records', 'Transcript Requests', 'Student Assistance'],
      'icon': Icons.admin_panel_settings,
    },
    {
      'name': 'Cafeteria',
      'type': 'Dining',
      'description': 'Main Campus Dining Hall',
      'floors': 1,
      'features': ['Meal Service', 'Snacks & Beverages', 'Seating Area', 'Food Vendors'],
      'icon': Icons.restaurant,
    },
    {
      'name': 'Gymnasium',
      'type': 'Sports Facility',
      'description': 'School Sports and Recreation Center',
      'floors': 1,
      'features': ['Basketball Court', 'Volleyball Court', 'Fitness Equipment', 'Locker Rooms', 'Sports Events'],
      'icon': Icons.sports_basketball,
    },
  ];

  // Predefined rooms by building
  final Map<String, List<Map<String, dynamic>>> buildingRooms = {
    'MST Building': [
      {'name': 'MST101', 'type': 'Lecture Room', 'floor': 1, 'capacity': '40 seats'},
      {'name': 'MST102', 'type': 'Lecture Room', 'floor': 1, 'capacity': '40 seats'},
      {'name': 'MST103', 'type': 'Lecture Room', 'floor': 1, 'capacity': '40 seats'},
      {'name': 'CL1', 'type': 'Computer Lab', 'floor': 1, 'capacity': '30 PCs'},
      {'name': 'CL2', 'type': 'Computer Lab', 'floor': 1, 'capacity': '30 PCs'},
      {'name': 'CL5', 'type': 'Computer Lab', 'floor': 2, 'capacity': '30 PCs'},
      {'name': 'CL6', 'type': 'Computer Lab', 'floor': 2, 'capacity': '30 PCs'},
      {'name': 'CR1', 'type': 'Classroom', 'floor': 1, 'capacity': '35 seats'},
      {'name': 'CR2', 'type': 'Classroom', 'floor': 1, 'capacity': '35 seats'},
    ],
    'JST Building': [
      {'name': 'JST101', 'type': 'Lecture Room', 'floor': 1, 'capacity': '45 seats'},
      {'name': 'JST102', 'type': 'Lecture Room', 'floor': 1, 'capacity': '45 seats'},
      {'name': 'JST201', 'type': 'Laboratory', 'floor': 2, 'capacity': '25 students'},
      {'name': 'JST202', 'type': 'Laboratory', 'floor': 2, 'capacity': '25 students'},
      {'name': 'JST301', 'type': 'Seminar Room', 'floor': 3, 'capacity': '20 seats'},
      {'name': 'JST302', 'type': 'Seminar Room', 'floor': 3, 'capacity': '20 seats'},
    ],
    'RST Building': [
      {'name': 'RST101', 'type': 'Research Lab', 'floor': 1, 'capacity': '15 researchers'},
      {'name': 'RST102', 'type': 'Research Lab', 'floor': 1, 'capacity': '15 researchers'},
      {'name': 'RST201', 'type': 'Graduate Lab', 'floor': 2, 'capacity': '20 students'},
      {'name': 'RST202', 'type': 'Conference Room', 'floor': 2, 'capacity': '50 seats'},
    ],
  };

  void _showFacilityDetails(Map<String, dynamic> facility) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.orange.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(facility['icon'] as IconData, color: Colors.orange, size: 28),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                facility['name'] as String,
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
              ),
            ),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              // Type badge
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.orange.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  facility['type'] as String,
                  style: const TextStyle(
                    color: Colors.orange,
                    fontWeight: FontWeight.w600,
                    fontSize: 12,
                  ),
                ),
              ),
              const SizedBox(height: 16),
              // Description
              Text(
                facility['description'] as String,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey.shade700,
                ),
              ),
              const SizedBox(height: 16),
              // Floors
              Row(
                children: [
                  Icon(Icons.stairs, size: 18, color: Colors.grey.shade600),
                  const SizedBox(width: 8),
                  Text(
                    '${facility['floors']} Floor${(facility['floors'] as int) > 1 ? 's' : ''}',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      color: Colors.grey.shade800,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              // Features
              const Text(
                'Features:',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
              const SizedBox(height: 8),
              ...(facility['features'] as List<String>).map((feature) => Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.check_circle, size: 16, color: Colors.green.shade600),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        feature,
                        style: const TextStyle(fontSize: 13),
                      ),
                    ),
                  ],
                ),
              )),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showBuildingRooms(String buildingName) {
    final rooms = buildingRooms[buildingName] ?? [];
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.blue.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.meeting_room, color: Colors.blue, size: 28),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                '$buildingName Rooms',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
            ),
          ],
        ),
        content: SizedBox(
          width: double.maxFinite,
          child: rooms.isEmpty
              ? const Text('No rooms available for this building.')
              : ListView.builder(
                  shrinkWrap: true,
                  itemCount: rooms.length,
                  itemBuilder: (context, index) {
                    final room = rooms[index];
                    return Card(
                      elevation: 1,
                      margin: const EdgeInsets.only(bottom: 8),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      child: ListTile(
                        leading: Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: Colors.blue.withValues(alpha: 0.1),
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(Icons.door_front_door, color: Colors.blue, size: 20),
                        ),
                        title: Text(
                          room['name'] as String,
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                        ),
                        subtitle: Text('${room['type']} • Floor ${room['floor']}'),
                        trailing: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.grey.shade200,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            room['capacity'] as String,
                            style: TextStyle(
                              fontSize: 11,
                              color: Colors.grey.shade700,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ),
                    );
                  },
                ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showAllFacilities() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(
          children: [
            Icon(Icons.business, color: Colors.orange),
            SizedBox(width: 12),
            Text(
              'Academic Facilities',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
          ],
        ),
        content: SizedBox(
          width: double.maxFinite,
          child: ListView.builder(
            shrinkWrap: true,
            itemCount: campusFacilities.length,
            itemBuilder: (context, index) {
              final facility = campusFacilities[index];
              return Card(
                elevation: 2,
                margin: const EdgeInsets.only(bottom: 10),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: InkWell(
                  onTap: () {
                    Navigator.pop(context);
                    _showFacilityDetails(facility);
                  },
                  borderRadius: BorderRadius.circular(12),
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: Colors.orange.withValues(alpha: 0.1),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(facility['icon'] as IconData, color: Colors.orange, size: 24),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                facility['name'] as String,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 15,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                facility['type'] as String,
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey.shade600,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const Icon(Icons.arrow_forward_ios, size: 16, color: Colors.grey),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showAllBuildingsForRooms() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(
          children: [
            Icon(Icons.meeting_room, color: Colors.blue),
            SizedBox(width: 12),
            Text(
              'Select Building',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
          ],
        ),
        content: SizedBox(
          width: double.maxFinite,
          child: ListView.builder(
            shrinkWrap: true,
            itemCount: buildingRooms.keys.length,
            itemBuilder: (context, index) {
              final building = buildingRooms.keys.elementAt(index);
              final roomCount = buildingRooms[building]!.length;
              return Card(
                elevation: 2,
                margin: const EdgeInsets.only(bottom: 10),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: InkWell(
                  onTap: () {
                    Navigator.pop(context);
                    _showBuildingRooms(building);
                  },
                  borderRadius: BorderRadius.circular(12),
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: Colors.blue.withValues(alpha: 0.1),
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(Icons.business, color: Colors.blue, size: 24),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                building,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 15,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                '$roomCount rooms available',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey.shade600,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const Icon(Icons.arrow_forward_ios, size: 16, color: Colors.grey),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        backgroundColor: Colors.deepOrange,
        elevation: 0,
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [const Color.from(alpha: 1, red: 1, green: 0.341, blue: 0.133).withValues(alpha: 0.1), Colors.white],
          ),
        ),
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Profile Header
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Colors.deepOrange, Colors.orangeAccent],
                ),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.deepOrange.withValues(alpha: 0.3),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.9),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.settings, color: Colors.deepOrange, size: 32),
                  ),
                  const SizedBox(width: 16),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'App Settings',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          'Customize your experience',
                          style: TextStyle(
                            color: Colors.white70,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            
            // Account Section
            _buildSectionTitle('Account'),
            _buildSettingsCard([
              _buildSettingsTile(
                icon: Icons.admin_panel_settings,
                iconColor: Colors.orange,
                title: 'Login Admin',
                subtitle: 'Access admin dashboard',
                onTap: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const LoginScreen()),
                  );
                },
              ),
            ]),
            const SizedBox(height: 16),
            
            // Appearance Section
            _buildSectionTitle('Appearance'),
            _buildSettingsCard([
              SwitchListTile(
                secondary: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.purple.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.dark_mode, color: Colors.purple),
                ),
                title: const Text('Dark Mode'),
                subtitle: const Text('Toggle dark theme'),
                value: widget.isDarkMode,
                onChanged: widget.onThemeChanged,
              ),
            ]),
            const SizedBox(height: 16),
            
            // Info Section - Facilities & Rooms
            _buildSectionTitle('Info'),
            _buildSettingsCard([
              _buildSettingsTile(
                icon: Icons.business,
                iconColor: Colors.orange,
                title: 'Facilities',
                subtitle: 'Academic facilities - See more',
                onTap: _showAllFacilities,
              ),
              const Divider(height: 1),
              _buildSettingsTile(
                icon: Icons.meeting_room,
                iconColor: Colors.blue,
                title: 'Rooms',
                subtitle: 'MST, JST, RST building rooms',
                onTap: _showAllBuildingsForRooms,
              ),
            ]),
            const SizedBox(height: 16),
            
            // About Section
            _buildSectionTitle('About'),
            _buildSettingsCard([
              _buildSettingsTile(
                icon: Icons.info_outline,
                iconColor: Colors.blue,
                title: 'About Us',
                subtitle: 'Guide Map Navigation app for campus routing',
                onTap: () {},
              ),
              const Divider(height: 1),
              _buildSettingsTile(
                icon: Icons.verified,
                iconColor: Colors.green,
                title: 'Version Info',
                subtitle: 'v1.0.0',
                onTap: () {},
              ),
              const Divider(height: 1),
              _buildSettingsTile(
                icon: Icons.system_update,
                iconColor: Colors.deepOrange,
                title: 'Check for Updates',
                subtitle: 'Verify you have the latest version',
                onTap: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('You are using the latest version.')),
                  );
                },
              ),
            ]),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 8, bottom: 8),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: Colors.grey[600],
          letterSpacing: 1,
        ),
      ),
    );
  }

  Widget _buildSettingsCard(List<Widget> children) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Column(children: children),
    );
  }

  Widget _buildSettingsTile({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: iconColor.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(icon, color: iconColor),
      ),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: const Icon(Icons.chevron_right, color: Colors.grey),
      onTap: onTap,
    );
  }
}

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  List<Map<String, dynamic>> notifications = [];

  @override
  void initState() {
    super.initState();
    _loadNotifications();
  }

  Future<void> _loadNotifications() async {
    final data = await DatabaseHelper.instance.getAllNotifications();
    setState(() => notifications = data);
  }

  Future<void> _markAsRead(int id) async {
    await DatabaseHelper.instance.markNotificationAsRead(id);
    _loadNotifications();
  }

  Future<void> _deleteNotification(int id) async {
    await DatabaseHelper.instance.deleteNotification(id);
    _loadNotifications();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications'),
      ),
      body: notifications.isEmpty
          ? const Center(child: Text('No notifications'))
          : ListView.builder(
              itemCount: notifications.length,
              itemBuilder: (context, index) {
                final n = notifications[index];
                return ListTile(
                  leading: Icon(
                    n['is_read'] == 1 ? Icons.check_circle : Icons.notifications,
                    color: n['is_read'] == 1 ? Colors.green : Colors.orange,
                  ),
                  title: Text(n['title']),
                  subtitle: Text(n['message']),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (n['is_read'] == 0)
                        TextButton(
                          onPressed: () => _markAsRead(n['id']),
                          child: const Text('Mark Read'),
                        ),
                      IconButton(
                        onPressed: () => _deleteNotification(n['id']),
                        icon: const Icon(Icons.delete, color: Colors.red),
                      ),
                    ],
                  ),
                );
              },
            ),
    );
  }
}

class AdminPanelScreen extends StatefulWidget {
  const AdminPanelScreen({super.key});

  @override
  State<AdminPanelScreen> createState() => _AdminPanelScreenState();
}

class _AdminPanelScreenState extends State<AdminPanelScreen> {
  List<Map<String, dynamic>> facilities = [];
  List<Map<String, dynamic>> rooms = [];
  List<Map<String, dynamic>> users = [];
  List<Map<String, dynamic>> ratings = [];
  List<Map<String, dynamic>> weeklyUsage = [];
  List<Map<String, dynamic>> mapMarkers = [];
  int totalActiveUsers = 0;
  
  // AI Performance Metrics
  int totalChatInteractions = 0;
  int aiAccuracyRate = 94; // Simulated percentage
  Map<String, int> faqCounts = {
    'Where the MST?': 45,
    'Comfort Room?': 38,
    'How do I navigate?': 32,
    'Where the CICT office?': 28,
    'Library hours?': 25,
    'Cafeteria location?': 20,
  };
  
  // Performance Metrics for Bar Chart
  final Map<String, double> performanceMetrics = {
    'System Reliability': 92,
    'User Satisfaction': 88,
    'AI Response Time': 95,
    'Navigation Accuracy': 90,
    'Content Coverage': 85,
  };

  @override
  void initState() {
    super.initState();
    _loadAllData();
    _loadDashboardData();
  }

  Future<void> _loadAllData() async {
    try {
      final facs = await ApiService.getAllFacilities();
      final rms = await ApiService.getAllRooms();
      final usrs = await ApiService.getAllUsers();
      final rtngs = await ApiService.getAllRatings();
      final markers = await ApiService.getAllMapMarkers();
      final chatHistory = await ChatbotDatabaseHelper.instance.getAllChatHistory();
      setState(() {
        facilities = facs;
        rooms = rms;
        users = usrs;
        ratings = rtngs;
        mapMarkers = markers;
        totalChatInteractions = chatHistory.length;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading data: $e')),
        );
      }
    }
  }

  Future<void> _loadDashboardData() async {
    try {
      final usage = await ApiService.getWeeklyAppUsage();
      final active = await ApiService.getTotalActiveUsers();
      setState(() {
        weeklyUsage = usage;
        totalActiveUsers = active;
      });
    } catch (e) {
      // Fallback to empty data
      setState(() {
        weeklyUsage = [];
        totalActiveUsers = 0;
      });
    }
  }


  void _showFacilityDialog({Map<String, dynamic>? facility}) {
    final nameController = TextEditingController(text: facility?['name'] ?? '');
    final descController = TextEditingController(text: facility?['description'] ?? '');
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(facility == null ? 'Add Facility' : 'Edit Facility'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameController,
              decoration: const InputDecoration(labelText: 'Name'),
            ),
            TextField(
              controller: descController,
              decoration: const InputDecoration(labelText: 'Description'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              final data = {
                'name': nameController.text,
                'description': descController.text,
              };
              try {
                if (facility == null) {
                  await ApiService.createFacility(data);
                } else {
                  await ApiService.updateFacility(facility['id'], data);
                }
                if (!context.mounted) return;
                Navigator.pop(context);
                _loadAllData();
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Facility saved successfully')),
                );
              } catch (e) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Error saving facility: $e')),
                );
              }
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  void _showRoomDialog({Map<String, dynamic>? room}) {
    final nameController = TextEditingController(text: room?['name'] ?? '');
    final descController = TextEditingController(text: room?['description'] ?? '');
    int? selectedFacilityId = room?['facility_id'];
    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: Text(room == null ? 'Add Room' : 'Edit Room'),
          insetPadding: const EdgeInsets.fromLTRB(20, 90, 20, 20),
          content: SizedBox(
            width: double.maxFinite,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: nameController,
                  decoration: const InputDecoration(labelText: 'Name'),
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: descController,
                  decoration: const InputDecoration(labelText: 'Description'),
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<int>(
                  isExpanded: true,
                  decoration: const InputDecoration(
                    labelText: 'Facility',
                    contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  ),
                  initialValue: selectedFacilityId,
                  items: facilities.map<DropdownMenuItem<int>>((f) {
                    return DropdownMenuItem<int>(
                      value: f['id'] as int,
                      child: Text(f['name'] as String, overflow: TextOverflow.ellipsis),
                    );
                  }).toList(),
                  onChanged: (value) => setDialogState(() => selectedFacilityId = value),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                if (selectedFacilityId == null) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Please select a facility')),
                  );
                  return;
                }
                final data = {
                  'name': nameController.text,
                  'description': descController.text,
                  'facility_id': selectedFacilityId,
                };
                try {
                  if (room == null) {
                    await ApiService.createRoom(data);
                  } else {
                    await ApiService.updateRoom(room['id'], data);
                  }
                  if (!context.mounted) return;
                  Navigator.pop(context);
                  _loadAllData();
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Room saved successfully')),
                  );
                } catch (e) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Error saving room: $e')),
                  );
                }
              },
              child: const Text('Save'),
            ),
          ],
        ),
      ),
    );
  }

  void _showUserDialog({Map<String, dynamic>? user}) {
    final usernameController = TextEditingController(text: user?['username'] ?? '');
    final passwordController = TextEditingController();
    String role = user?['role'] ?? 'user';
    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: Text(user == null ? 'Add User' : 'Edit User'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: usernameController,
                decoration: const InputDecoration(labelText: 'Username'),
              ),
              TextField(
                controller: passwordController,
                decoration: const InputDecoration(labelText: 'Password (leave blank to keep current)'),
                obscureText: true,
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                initialValue: role,
                items: ['admin', 'user'].map((r) {
                  return DropdownMenuItem(value: r, child: Text(r));
                }).toList(),
                onChanged: (value) => setDialogState(() => role = value!),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                final data = {
                  'username': usernameController.text,
                  'role': role,
                };
                if (passwordController.text.isNotEmpty) {
                  data['password'] = passwordController.text;
                }
                try {
                  if (user == null) {
                    data['password'] = passwordController.text.isNotEmpty
                        ? passwordController.text
                        : 'default';
                    await ApiService.createUser(data);
                  } else {
                    await ApiService.updateUser(user['id'], data);
                  }
                  if (!context.mounted) return;
                  Navigator.pop(context);
                  _loadAllData();
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('User saved successfully')),
                  );
                } catch (e) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Error saving user: $e')),
                  );
                }
              },
              child: const Text('Save'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _deleteFacility(int id) async {
    try {
      await ApiService.deleteFacility(id);
      _loadAllData();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Facility deleted successfully')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error deleting facility: $e')),
        );
      }
    }
  }

  Future<void> _deleteRoom(int id) async {
    try {
      await ApiService.deleteRoom(id);
      _loadAllData();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Room deleted successfully')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error deleting room: $e')),
        );
      }
    }
  }

  Future<void> _deleteUser(int id) async {
    try {
      await ApiService.deleteUser(id);
      _loadAllData();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('User deleted successfully')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error deleting user: $e')),
        );
      }
    }
  }

  Future<void> _deleteMapMarker(int id) async {
    try {
      await ApiService.deleteMapMarker(id);
      _loadAllData();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Map marker deleted successfully')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error deleting map marker: $e')),
        );
      }
    }
  }

  void _showMapMarkerDialog({Map<String, dynamic>? marker}) {
    final nameController = TextEditingController(text: marker?['name'] ?? '');
    final xController = TextEditingController(text: marker?['x_position']?.toString() ?? '0.5');
    final yController = TextEditingController(text: marker?['y_position']?.toString() ?? '0.5');
    String markerType = marker?['type'] ?? 'facility';
    
    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: Text(marker == null ? 'Add Map Marker' : 'Edit Map Marker'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: nameController,
                  decoration: const InputDecoration(
                    labelText: 'Name',
                    hintText: 'e.g., MST Building',
                    prefixIcon: Icon(Icons.label),
                  ),
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  initialValue: markerType,
                  decoration: const InputDecoration(
                    labelText: 'Type',
                    prefixIcon: Icon(Icons.category),
                  ),
                  items: ['facility', 'room'].map((type) {
                    return DropdownMenuItem(
                      value: type,
                      child: Text(type.toUpperCase()),
                    );
                  }).toList(),
                  onChanged: (value) => setDialogState(() => markerType = value!),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: xController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'X Position (0.0 - 1.0)',
                    hintText: '0.5',
                    prefixIcon: Icon(Icons.horizontal_rule),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: yController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Y Position (0.0 - 1.0)',
                    hintText: '0.5',
                    prefixIcon: Icon(Icons.vertical_align_center),
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.orange,
                foregroundColor: Colors.white,
              ),
              onPressed: () async {
                final data = {
                  'name': nameController.text,
                  'type': markerType,
                  'x_position': double.tryParse(xController.text) ?? 0.5,
                  'y_position': double.tryParse(yController.text) ?? 0.5,
                };
                try {
                  if (marker == null) {
                    await ApiService.createMapMarker(data);
                  } else {
                    await ApiService.updateMapMarker(marker['id'], data);
                  }
                  if (!context.mounted) return;
                  Navigator.pop(context);
                  _loadAllData();
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(marker == null ? 'Marker added' : 'Marker updated')),
                  );
                } catch (e) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Error saving marker: $e')),
                  );
                }
              },
              child: const Text('Save'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildContentManagementTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Facilities Section
          _buildContentSection(
            title: 'Facilities',
            icon: Icons.business,
            color: Colors.blue,
            items: facilities,
            onAdd: () => _showFacilityDialog(),
            onEdit: (item) => _showFacilityDialog(facility: item),
            onDelete: (item) => _deleteFacility(item['id']),
            titleField: 'name',
            subtitleField: 'description',
          ),
          const SizedBox(height: 24),
          // Rooms Section
          _buildContentSection(
            title: 'Rooms',
            icon: Icons.meeting_room,
            color: Colors.orange,
            items: rooms,
            onAdd: () => _showRoomDialog(),
            onEdit: (item) => _showRoomDialog(room: item),
            onDelete: (item) => _deleteRoom(item['id']),
            titleField: 'name',
            subtitleField: 'description',
          ),
          const SizedBox(height: 24),
          // Map Markers Section
          _buildContentSection(
            title: 'Map Markers',
            icon: Icons.location_on,
            color: Colors.red,
            items: mapMarkers,
            onAdd: () => _showMapMarkerDialog(),
            onEdit: (item) => _showMapMarkerDialog(marker: item),
            onDelete: (item) => _deleteMapMarker(item['id']),
            titleField: 'name',
            subtitleField: 'type',
          ),
          const SizedBox(height: 24),
          // Map Editor Section
          _buildMapEditorCard(),
          const SizedBox(height: 24),
          // Admin Users Section
          _buildContentSection(
            title: 'Admin Users',
            icon: Icons.admin_panel_settings,
            color: Colors.purple,
            items: users,
            onAdd: () => _showUserDialog(),
            onEdit: (item) => _showUserDialog(user: item),
            onDelete: (item) => _deleteUser(item['id']),
            titleField: 'username',
            subtitleField: 'role',
          ),
        ],
      ),
    );
  }

  Widget _buildMapEditorCard() {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.green.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.map, color: Colors.green),
                ),
                const SizedBox(width: 12),
                const Text(
                  'Map Editor',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                  onPressed: () => _openMapEditor(),
                  icon: const Icon(Icons.edit, size: 18),
                  label: const Text('Edit Map'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey.shade100,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.grey.shade300),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.info_outline, size: 18, color: Colors.grey.shade600),
                      const SizedBox(width: 8),
                      Text(
                        'Map Layout Controls',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: Colors.grey.shade700,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      _buildMapControlChip(Icons.add_location, 'Add Marker', Colors.blue),
                      _buildMapControlChip(Icons.edit_road, 'Edit Paths', Colors.orange),
                      _buildMapControlChip(Icons.layers, 'Floor Plans', Colors.purple),
                      _buildMapControlChip(Icons.zoom_in, 'Zoom Controls', Colors.teal),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMapControlChip(IconData icon, String label, Color color) {
    return Chip(
      avatar: Icon(icon, size: 16, color: color),
      label: Text(
        label,
        style: TextStyle(fontSize: 11, color: color),
      ),
      backgroundColor: color.withValues(alpha: 0.1),
      side: BorderSide(color: color.withValues(alpha: 0.3)),
      padding: const EdgeInsets.symmetric(horizontal: 4),
    );
  }

  void _openMapEditor() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => MapEditorScreen(
          markers: mapMarkers,
          onMarkersUpdated: (updatedMarkers) {
            setState(() {
              mapMarkers = updatedMarkers;
            });
          },
        ),
      ),
    );
  }

  Widget _buildContentSection({
    required String title,
    required IconData icon,
    required Color color,
    required List<Map<String, dynamic>> items,
    required VoidCallback onAdd,
    required Function(Map<String, dynamic>) onEdit,
    required Function(Map<String, dynamic>) onDelete,
    required String titleField,
    required String subtitleField,
  }) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(icon, color: color),
                ),
                const SizedBox(width: 12),
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: color,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                  onPressed: onAdd,
                  icon: const Icon(Icons.add, size: 18),
                  label: const Text('Add'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (items.isEmpty)
              Center(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Text(
                    'No $title yet',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey.shade600,
                    ),
                  ),
                ),
              )
            else
              ...items.map((item) => Card(
                elevation: 1,
                margin: const EdgeInsets.only(bottom: 8),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                child: ListTile(
                  dense: true,
                  leading: CircleAvatar(
                    backgroundColor: color.withValues(alpha: 0.1),
                    child: Icon(icon, color: color, size: 20),
                  ),
                  title: Text(
                    item[titleField]?.toString() ?? '',
                    style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                  ),
                  subtitle: Text(
                    item[subtitleField]?.toString() ?? '',
                    style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                  ),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                        onPressed: () => onEdit(item),
                        icon: const Icon(Icons.edit, color: Colors.blue, size: 20),
                      ),
                      IconButton(
                        onPressed: () => onDelete(item),
                        icon: const Icon(Icons.delete, color: Colors.red, size: 20),
                      ),
                    ],
                  ),
                ),
              )),
          ],
        ),
      ),
    );
  }

  Widget _buildReportsTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Most Picked FAQs Section
          Card(
            elevation: 4,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: Colors.indigo.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(Icons.question_answer, color: Colors.indigo, size: 28),
                      ),
                      const SizedBox(width: 12),
                      const Text(
                        'Most Picked FAQs',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  ...faqCounts.entries.toList().asMap().entries.map((entry) {
                    final index = entry.key;
                    final faq = entry.value;
                    final question = faq.key;
                    final count = faq.value;
                    final percentage = (count / faqCounts.values.reduce((a, b) => a + b) * 100).toInt();
                    
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: Row(
                        children: [
                          Container(
                            width: 28,
                            height: 28,
                            decoration: BoxDecoration(
                              color: Colors.indigo.withValues(alpha: 0.1),
                              shape: BoxShape.circle,
                            ),
                            child: Center(
                              child: Text(
                                '${index + 1}',
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.indigo,
                                  fontSize: 12,
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  question,
                                  style: const TextStyle(
                                    fontWeight: FontWeight.w600,
                                    fontSize: 14,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                LinearProgressIndicator(
                                  value: count / faqCounts.values.first,
                                  backgroundColor: Colors.grey.shade200,
                                  valueColor: AlwaysStoppedAnimation<Color>(
                                    Colors.indigo.withValues(alpha: 0.6 + (index * 0.1)),
                                  ),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 12),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: Colors.indigo.withValues(alpha: 0.1),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              '$count ($percentage%)',
                              style: const TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                                color: Colors.indigo,
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  }),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          // User Ratings & Comments Section
          Card(
            elevation: 4,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: Colors.amber.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(Icons.star, color: Colors.amber, size: 28),
                      ),
                      const SizedBox(width: 12),
                      Text(
                        'User Ratings & Comments (${ratings.length})',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  if (ratings.isEmpty)
                    Center(
                      child: Padding(
                        padding: const EdgeInsets.all(20),
                        child: Text(
                          'No ratings yet',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey.shade600,
                          ),
                        ),
                      ),
                    )
                  else
                    ...ratings.take(10).map((r) => Card(
                      elevation: 1,
                      margin: const EdgeInsets.only(bottom: 8),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      child: ListTile(
                        dense: true,
                        leading: CircleAvatar(
                          backgroundColor: Colors.amber.withValues(alpha: 0.1),
                          child: const Icon(Icons.star, color: Colors.amber, size: 20),
                        ),
                        title: Row(
                          children: List.generate(5, (i) {
                            return Icon(
                              i < (r['rating'] ?? 0) ? Icons.star : Icons.star_border,
                              color: Colors.amber,
                              size: 16,
                            );
                          }),
                        ),
                        subtitle: Text(
                          r['comment'] ?? 'No comment',
                          style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                        ),
                        trailing: Text(
                          r['created_at']?.toString().substring(0, 10) ?? '',
                          style: TextStyle(fontSize: 11, color: Colors.grey.shade500),
                        ),
                      ),
                    )),
                  if (ratings.length > 10)
                    Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Center(
                        child: Text(
                          '+ ${ratings.length - 10} more ratings',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey.shade500,
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }


  Widget _buildDashboardTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Stats Cards
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  icon: Icons.people,
                  title: 'Total Users',
                  value: users.length.toString(),
                  color: Colors.blue,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatCard(
                  icon: Icons.business,
                  title: 'Facilities',
                  value: facilities.length.toString(),
                  color: Colors.green,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  icon: Icons.meeting_room,
                  title: 'Rooms',
                  value: rooms.length.toString(),
                  color: Colors.orange,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatCard(
                  icon: Icons.star,
                  title: 'Ratings',
                  value: ratings.length.toString(),
                  color: Colors.purple,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Active Users Card
          Card(
            elevation: 4,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.orange.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(Icons.trending_up, color: Colors.orange, size: 24),
                      ),
                      const SizedBox(width: 10),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Weekly Active Users',
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Text(
                              'Last 7 days',
                              style: TextStyle(
                                fontSize: 11,
                                color: Colors.grey,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.orange,
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Text(
                          '$totalActiveUsers',
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  if (weeklyUsage.isEmpty)
                    const Center(
                      child: Padding(
                        padding: EdgeInsets.all(8),
                        child: Text(
                          'No usage data yet',
                          style: TextStyle(color: Colors.grey, fontSize: 12),
                        ),
                      ),
                    )
                  else
                    SizedBox(
                      height: 100,
                      child: _buildUsageChart(),
                    ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          // AI Performance Card
          _buildAIPerformanceCard(),
          const SizedBox(height: 10),
          // Overall Performance Bar Chart
          _buildOverallPerformanceCard(),
          const SizedBox(height: 20),
        ],
      ),
    );
  }

  Widget _buildStatCard({
    required IconData icon,
    required String title,
    required String value,
    required Color color,
  }) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.15),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: color, size: 28),
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              title,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey.shade600,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }


  Widget _buildUsageChart() {
    // Simple bar chart representation
    final maxUsers = weeklyUsage.isNotEmpty
        ? weeklyUsage.map((u) => u['user_count'] as int).reduce((a, b) => a > b ? a : b)
        : 1;

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      crossAxisAlignment: CrossAxisAlignment.end,
      children: weeklyUsage.map((usage) {
        final count = usage['user_count'] as int;
        final date = usage['session_date'] as String;
        final day = date.substring(5); // Get MM-DD
        final height = maxUsers > 0 ? (count / maxUsers * 150) : 0.0;

        return Column(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            Text(
              count.toString(),
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Container(
              width: 30,
              height: height.toDouble(),
              decoration: BoxDecoration(
                color: Colors.orangeAccent,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
            const SizedBox(height: 4),
            Text(
              day,
              style: const TextStyle(
                fontSize: 10,
                color: Colors.grey,
              ),
            ),
          ],
        );
      }).toList(),
    );
  }

  Widget _buildCompactAIMetric({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: color, size: 18),
          const SizedBox(width: 6),
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                value,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
              Text(
                label,
                style: TextStyle(
                  fontSize: 10,
                  color: Colors.grey.shade600,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }




  Widget _buildAIPerformanceCard() {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.purple.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.smart_toy, color: Colors.purple, size: 24),
                ),
                const SizedBox(width: 10),
                const Text(
                  'AI Performance',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.purple,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    '$aiAccuracyRate%',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildCompactAIMetric(
                    icon: Icons.chat_bubble,
                    label: 'Chats',
                    value: totalChatInteractions.toString(),
                    color: Colors.blue,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildCompactAIMetric(
                    icon: Icons.speed,
                    label: 'Accuracy',
                    value: '$aiAccuracyRate%',
                    color: Colors.green,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildCompactAIMetric(
                    icon: Icons.timer,
                    label: 'Response',
                    value: '0.5s',
                    color: Colors.orange,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOverallPerformanceCard() {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.teal.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.pie_chart, color: Colors.teal, size: 24),
                ),
                const SizedBox(width: 10),
                const Text(
                  'Overall Performance',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                // Pie Chart
                SizedBox(
                  width: 120,
                  height: 120,
                  child: _buildPerformancePieChart(),
                ),
                const SizedBox(width: 16),
                // Legend
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: performanceMetrics.entries.map((entry) {
                      final value = entry.value;
                      final label = entry.key;
                      Color color;
                      if (value < 70) {
                        color = Colors.red;
                      } else if (value < 80) {
                        color = Colors.blue;
                      } else if (value < 90) {
                        color = Colors.amber;
                      } else {
                        color = Colors.green;
                      }
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 4),
                        child: Row(
                          children: [
                            Container(
                              width: 10,
                              height: 10,
                              decoration: BoxDecoration(
                                color: color,
                                shape: BoxShape.circle,
                              ),
                            ),
                            const SizedBox(width: 6),
                            Expanded(
                              child: Text(
                                label,
                                style: const TextStyle(fontSize: 10),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            Text(
                              '${value.toInt()}%',
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: color,
                              ),
                            ),
                          ],
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPerformancePieChart() {
    return CustomPaint(
      size: const Size(120, 120),
      painter: PieChartPainter(performanceMetrics),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(30),
            border: Border.all(
              color: Colors.white.withValues(alpha: 0.3),
              width: 1,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: const BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.admin_panel_settings,
                  color: Colors.orange,
                  size: 22,
                ),
              ),
              const SizedBox(width: 10),
              const Text(
                'Admin Panel',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                  letterSpacing: 0.5,
                ),
              ),
              const SizedBox(width: 8),
            ],
          ),
        ),
        automaticallyImplyLeading: false,
        backgroundColor: Colors.orange,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: false,
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Colors.orange,
                Colors.orange.shade700,
                Colors.orange.shade900,
              ],
            ),
          ),
        ),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 8),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(20),
            ),
            child: IconButton(
              icon: const Icon(Icons.settings, color: Colors.white),
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const AdminSettingsScreen()),
                );
              },
              tooltip: 'Settings',
            ),
          ),
          Container(
            margin: const EdgeInsets.only(right: 8),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(20),
            ),
            child: IconButton(
              icon: const Icon(Icons.logout, color: Colors.white),
              onPressed: () {
                Navigator.of(context).pushAndRemoveUntil(
                  MaterialPageRoute(builder: (_) => MainNavigationShell(
                    isDarkMode: false,
                    onThemeChanged: (_) {},
                  )),
                  (route) => false,
                );
              },
              tooltip: 'Logout',
            ),
          ),
        ],
      ),
      body: DefaultTabController(
        length: 3,
        child: Column(
          children: [
            Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Colors.orange.shade600,
                    Colors.orange.shade800,
                    Colors.orange.shade900,
                  ],
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.orange.withValues(alpha: 0.4),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: TabBar(
                isScrollable: false,
                indicator: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: Colors.white.withValues(alpha: 0.4),
                    width: 1,
                  ),
                ),
                indicatorSize: TabBarIndicatorSize.tab,
                indicatorWeight: 0,
                dividerColor: Colors.transparent,
                labelStyle: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
                unselectedLabelStyle: const TextStyle(
                  fontWeight: FontWeight.normal,
                  fontSize: 13,
                ),
                labelColor: Colors.white,
                unselectedLabelColor: Colors.white.withValues(alpha: 0.7),
                tabs: const [
                  Tab(
                    icon: Icon(Icons.dashboard, size: 24),
                    text: 'Dashboard',
                    iconMargin: EdgeInsets.only(bottom: 4),
                  ),
                  Tab(
                    icon: Icon(Icons.folder, size: 24),
                    text: 'Content',
                    iconMargin: EdgeInsets.only(bottom: 4),
                  ),
                  Tab(
                    icon: Icon(Icons.analytics, size: 24),
                    text: 'Reports',
                    iconMargin: EdgeInsets.only(bottom: 4),
                  ),
                ],
              ),
            ),
            Expanded(
              child: TabBarView(
                children: [
                  _buildDashboardTab(),
                  _buildContentManagementTab(),
                  _buildReportsTab(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }


}

class BuildingInfoScreen extends StatelessWidget {
  const BuildingInfoScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Building Information')),
      body: FutureBuilder(
        future: DatabaseHelper.instance.getAllFacilities(),
        builder: (context, snapshot) {
          if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
          final facilities = snapshot.data!;
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: facilities.length,
            itemBuilder: (context, index) {
              final f = facilities[index];
              return Card(
                child: ListTile(
                  leading: const Icon(Icons.business),
                  title: Text(f['name']),
                  subtitle: Text(f['description'] ?? ''),
                ),
              );
            },
          );
        },
      ),
    );
  }
}

class AdminInfoScreen extends StatelessWidget {
  const AdminInfoScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Rooms Information')),
      body: FutureBuilder(
        future: DatabaseHelper.instance.getAllRooms(),
        builder: (context, snapshot) {
          if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
          final rooms = snapshot.data!;
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: rooms.length,
            itemBuilder: (context, index) {
              final r = rooms[index];
              return Card(
                child: ListTile(
                  leading: const Icon(Icons.meeting_room),
                  title: Text(r['name']),
                  subtitle: Text(r['description'] ?? ''),
                ),
              );
            },
          );
        },
      ),
    );
  }
}

// Pie Chart Custom Painter
class PieChartPainter extends CustomPainter {
  final Map<String, double> data;

  PieChartPainter(this.data);

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2;

    final total = data.values.reduce((a, b) => a + b);
    double startAngle = -pi / 2;

    final colors = [
      Colors.green,    // System Reliability
      Colors.blue,     // User Satisfaction
      Colors.orange,   // AI Response Time
      Colors.purple,   // Navigation Accuracy
      Colors.red,      // Content Coverage
    ];

    int colorIndex = 0;
    for (final entry in data.entries) {
      final sweepAngle = (entry.value / total) * 2 * pi;

      final paint = Paint()
        ..color = colors[colorIndex % colors.length]
        ..style = PaintingStyle.fill;

      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        startAngle,
        sweepAngle,
        true,
        paint,
      );

      // Draw border
      final borderPaint = Paint()
        ..color = Colors.white
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2;

      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        startAngle,
        sweepAngle,
        true,
        borderPaint,
      );

      startAngle += sweepAngle;
      colorIndex++;
    }

    // Draw center hole for donut chart effect
    final holePaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;

    canvas.drawCircle(center, radius * 0.4, holePaint);

    // Draw center text
    final textPainter = TextPainter(
      text: TextSpan(
        text: '${(total / data.length).toInt()}%',
        style: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.bold,
          color: Colors.teal,
        ),
      ),
      textDirection: TextDirection.ltr,
    );
    textPainter.layout();
    textPainter.paint(
      canvas,
      center - Offset(textPainter.width / 2, textPainter.height / 2),
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class InstructorInfoScreen extends StatelessWidget {
  const InstructorInfoScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Instructor Info')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          Card(
            child: ListTile(
              leading: Icon(Icons.person),
              title: Text('Dr. Smith'),
              subtitle: Text('Computer Science Department'),
            ),
          ),
          Card(
            child: ListTile(
              leading: Icon(Icons.person),
              title: Text('Prof. Johnson'),
              subtitle: Text('Mathematics Department'),
            ),
          ),
          Card(
            child: ListTile(
              leading: Icon(Icons.person),
              title: Text('Dr. Williams'),
              subtitle: Text('Physics Department'),
            ),
          ),
        ],
      ),
    );
  }
}

class EmployeesScreen extends StatelessWidget {
  const EmployeesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Employees')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          Card(
            child: ListTile(
              leading: Icon(Icons.support_agent),
              title: Text('Support Staff'),
              subtitle: Text('IT Support - ext. 1001'),
            ),
          ),
          Card(
            child: ListTile(
              leading: Icon(Icons.cleaning_services),
              title: Text('Maintenance'),
              subtitle: Text('Building Maintenance - ext. 1002'),
            ),
          ),
          Card(
            child: ListTile(
              leading: Icon(Icons.security),
              title: Text('Security'),
              subtitle: Text('Campus Security - ext. 1003'),
            ),
          ),
        ],
      ),
    );
  }
}

class ChatbotScreen extends StatefulWidget {
  const ChatbotScreen({super.key});

  @override
  State<ChatbotScreen> createState() => _ChatbotScreenState();
}

class _ChatbotScreenState extends State<ChatbotScreen> {
  final TextEditingController inputController = TextEditingController();
  final List<Map<String, dynamic>> messages = [];
  bool loading = false;

  @override
  void initState() {
    super.initState();
    _loadChatHistory();
  }

  Future<void> _loadChatHistory() async {
    final history = await ChatbotDatabaseHelper.instance.getRecentChatHistory(50);
    setState(() {
      messages.clear();
      // Convert database format to display format
      for (final chat in history.reversed) {
        messages.add({
          'text': 'You: ${chat['message']}',
          'isUser': true,
        });
        messages.add({
          'text': 'Bot: ${chat['reply']}',
          'isUser': false,
        });
      }
    });
  }

  // Enhanced rule-based campus guide AI - completely free, no API needed
  String generateCampusReply(String message) {
    final lowerMsg = message.toLowerCase();
    
    // Greetings
    if (lowerMsg.contains('hello') || lowerMsg.contains('hi') || lowerMsg.contains('hey')) {
      return 'Hello! Welcome to SEAIT Campus Guide! 🎓\n\nI can help you with:\n• Finding buildings (MST, JST, RST)\n• Locating rooms (CL1-CL6, CR1-CR4)\n• Campus facilities (Library, Cafeteria, Registrar)\n• Floor information\n• General navigation\n\nWhat would you like to know?';
    }
    
    // Building information
    if (lowerMsg.contains('mst building') || lowerMsg.contains('mst')) {
      return '🏢 MST Building (Main Science and Technology)\n• 4 floors total\n• Computer Labs: CL1, CL2 (1st Floor)\n• Computer Labs: CL5, CL6 (2nd Floor)\n• Lecture Rooms: CR1, CR2\n• Type: Main academic building\n\nNavigate to MST Building from anywhere using the Navigate tab!';
    }
    
    if (lowerMsg.contains('jst building') || lowerMsg.contains('jst')) {
      return '🏢 JST Building (Junior Science and Technology)\n• 4 floors total\n• Various classrooms and labs\n• Type: Academic building\n\nNavigate to JST Building from anywhere using the Navigate tab!';
    }
    
    if (lowerMsg.contains('rst building') || lowerMsg.contains('rst')) {
      return '🏢 RST Building (Research Science and Technology)\n• 3 floors total (note: no 4th floor)\n• Research facilities and labs\n• Type: Research building\n\nNavigate to RST Building from anywhere using the Navigate tab!';
    }
    
    // Computer Labs
    if (lowerMsg.contains('cl1') || lowerMsg.contains('computer lab 1')) {
      return '💻 CL1 (Computer Lab 1)\n• Location: Building / MST Building, 1st Floor\n• Type: Computer Laboratory\n• Equipment: PCs with internet, projectors\n• Perfect for: Computer classes, programming labs\n\nNavigate to CL1 using the Navigate tab!';
    }
    
    if (lowerMsg.contains('cl2') || lowerMsg.contains('computer lab 2')) {
      return '💻 CL2 (Computer Lab 2)\n• Location: Building / MST Building, 1st Floor\n• Type: Computer Laboratory\n• Equipment: PCs with internet, projectors\n• Perfect for: Computer classes, programming labs\n\nNavigate to CL2 using the Navigate tab!';
    }
    
    if (lowerMsg.contains('cl3')) {
      return '💻 CL3 (Computer Lab 3)\n• Location: Building, 1st Floor\n• Type: Computer Laboratory\n• Equipment: PCs with internet access\n• Perfect for: Computer classes, research\n\nNavigate to CL3 using the Navigate tab!';
    }
    
    if (lowerMsg.contains('cl4')) {
      return '💻 CL4 (Computer Lab 4)\n• Location: Building, 1st Floor\n• Type: Computer Laboratory\n• Equipment: PCs with internet access\n• Perfect for: Computer classes, research\n\nNavigate to CL4 using the Navigate tab!';
    }
    
    if (lowerMsg.contains('cl5')) {
      return '💻 CL5 (Computer Lab 5)\n• Location: Building / MST Building, 2nd Floor\n• Type: Computer Laboratory\n• Note: This is on the 2nd Floor!\n• Equipment: PCs with projectors\n\nNavigate to CL5 using the Navigate tab!';
    }
    
    if (lowerMsg.contains('cl6')) {
      return '💻 CL6 (Computer Lab 6)\n• Location: Building / MST Building, 2nd Floor\n• Type: Computer Laboratory\n• Note: This is on the 2nd Floor!\n• Equipment: PCs with projectors\n\nNavigate to CL6 using the Navigate tab!';
    }
    
    // Lecture Rooms
    if (lowerMsg.contains('cr1') || lowerMsg.contains('lecture room 1')) {
      return '📚 CR1 (Classroom/Lecture Room 1)\n• Location: Building, 1st Floor\n• Type: Lecture Room\n• Capacity: Standard classroom size\n• Perfect for: Lectures, seminars\n\nNavigate to CR1 using the Navigate tab!';
    }
    
    if (lowerMsg.contains('cr2') || lowerMsg.contains('lecture room 2')) {
      return '📚 CR2 (Classroom/Lecture Room 2)\n• Location: Building, 1st Floor\n• Type: Lecture Room\n• Capacity: Standard classroom size\n• Perfect for: Lectures, seminars\n\nNavigate to CR2 using the Navigate tab!';
    }
    
    if (lowerMsg.contains('cr3') || lowerMsg.contains('lecture room 3')) {
      return '📚 CR3 (Classroom/Lecture Room 3)\n• Location: Building, 1st Floor\n• Type: Lecture Room\n• Capacity: Standard classroom size\n\nNavigate to CR3 using the Navigate tab!';
    }
    
    if (lowerMsg.contains('cr4') || lowerMsg.contains('lecture room 4')) {
      return '📚 CR4 (Classroom/Lecture Room 4)\n• Location: Building, 1st Floor\n• Type: Lecture Room\n• Capacity: Standard classroom size\n\nNavigate to CR4 using the Navigate tab!';
    }
    
    // Facilities
    if (lowerMsg.contains('library')) {
      return '📖 Library\n• Location: Main Campus\n• Floors: 2 floors\n• Services: Book lending, study areas, research materials\n• Hours: Check notice board for current hours\n\nNavigate to Library using the Navigate tab!';
    }
    
    if (lowerMsg.contains('registrar') || lowerMsg.contains('office')) {
      return '📋 Registrar Office\n• Location: Main Campus, Ground Floor\n• Services: Enrollment, records, student services\n• Hours: Monday-Friday, 8AM-5PM\n\nNavigate to Registrar Office using the Navigate tab!';
    }
    
    if (lowerMsg.contains('cafeteria') || lowerMsg.contains('canteen') || lowerMsg.contains('food')) {
      return '🍽️ Cafeteria / Canteen\n• Location: Main Campus\n• Floor: Ground Floor\n• Services: Meals, snacks, beverages\n• Hours: 7AM-6PM daily\n\nNavigate to Cafeteria using the Navigate tab!';
    }
    
    // Navigation help
    if (lowerMsg.contains('navigate') || lowerMsg.contains('direction') || lowerMsg.contains('how to get')) {
      return '🧭 How to Navigate:\n1. Go to the "Navigate" tab at the bottom\n2. Tap "Set origin and destination"\n3. Select where you are (From)\n4. Select where you want to go (To)\n5. Choose the floor if needed\n6. Tap "Start Navigate"\n\nThe map will show you the route!';
    }
    
    if (lowerMsg.contains('floor') || lowerMsg.contains('1st') || lowerMsg.contains('2nd') || lowerMsg.contains('3rd') || lowerMsg.contains('4th')) {
      return '🏢 Floor Information:\n• MST Building: 4 floors\n• JST Building: 4 floors\n• RST Building: 3 floors (no 4th floor)\n• Library: 2 floors\n• Registrar: 1 floor\n• Cafeteria: 1 floor\n• CL1-CL4, CR1-CR4: 1st Floor\n• CL5-CL6: 2nd Floor\n\nUse the Navigate tab to select your floor!';
    }
    
    // Help
    if (lowerMsg.contains('help') || lowerMsg.contains('what can you do')) {
      return '🤖 I am your SEAIT Campus Guide! I can help with:\n\n🏢 Buildings: MST, JST, RST\n💻 Computer Labs: CL1-CL6\n📚 Lecture Rooms: CR1-CR4\n📖 Facilities: Library, Registrar, Cafeteria\n🧭 Navigation: How to use the app\n📍 Locations: Where things are\n\nJust ask me anything about the campus!';
    }
    
    // Thank you
    if (lowerMsg.contains('thank') || lowerMsg.contains('thanks')) {
      return "You're welcome! 😊 I'm here to help anytime. Have a great day at SEAIT!";
    }
    
    // Default response
    return "🤔 I want to help! Here are some things you can ask:\n\n• 'Where is CL1?'\n• 'How many floors in MST Building?'\n• 'Navigate to Library'\n• 'Where is the Cafeteria?'\n• 'Help' for more options\n\nOr use the Navigate tab to find routes between locations!";
  }

  Future<void> sendMessage() async {
    final text = inputController.text.trim();
    if (text.isEmpty) return;

    setState(() {
      messages.add({'text': 'You: $text', 'isUser': true});
      loading = true;
      inputController.clear();
    });

    // Generate reply using free local AI (no API calls, no internet needed)
    final reply = generateCampusReply(text);
    
    // Small delay to simulate thinking (optional, improves UX)
    await Future.delayed(const Duration(milliseconds: 500));
    
    // Save to database
    await ChatbotDatabaseHelper.instance.insertChatHistory({
      'message': text,
      'reply': reply,
    });
    
    setState(() {
      messages.add({'text': 'Bot: $reply', 'isUser': false});
      loading = false;
    });
  }

  void _sendQuickQuestion(String question) {
    inputController.text = question;
    sendMessage();
  }

  Widget _buildQuickQuestionChip(String text, IconData icon) {
    return ActionChip(
      avatar: Icon(icon, size: 18, color: Colors.orange),
      label: Text(
        text,
        style: const TextStyle(fontSize: 12),
      ),
      backgroundColor: Colors.orange.withValues(alpha: 0.1),
      side: BorderSide(color: Colors.orange.withValues(alpha: 0.3)),
      onPressed: () => _sendQuickQuestion(text),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SEAIT Guide'),
        backgroundColor: Colors.orange,
        elevation: 0,
        actions: [
          IconButton(
            onPressed: () {
              setState(() => messages.clear());
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('New conversation started')),
              );
            },
            icon: const Icon(Icons.add_comment, color: Colors.white),
            tooltip: 'New Chat',
          ),
          IconButton(
            onPressed: () async {
              await ChatbotDatabaseHelper.instance.clearAllChatHistory();
              setState(() => messages.clear());
              if (!mounted) return;
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Chat history cleared')),
              );
            },
            icon: const Icon(Icons.delete_outline, color: Colors.white),
            tooltip: 'Clear history',
          ),
        ],
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Colors.orange.withValues(alpha: 0.1), Colors.grey.shade50],
          ),
        ),
        child: Column(
          children: [
            // Chatbot Header Card
            Container(
              margin: const EdgeInsets.all(16),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Colors.orange, Colors.orangeAccent],
                ),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.orange.withValues(alpha: 0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.9),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.smart_toy, color: Colors.orange, size: 28),
                  ),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Campus Assistant',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          'Ask me about buildings, rooms, facilities',
                          style: TextStyle(
                            color: Colors.white70,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            // Recommended Questions Chips (Offline Mode)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Quick Questions (Offline)',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: Colors.grey.shade600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      _buildQuickQuestionChip('Where is CL1?', Icons.computer),
                      _buildQuickQuestionChip('Where is CR1?', Icons.meeting_room),
                      _buildQuickQuestionChip('MST Building info', Icons.business),
                      _buildQuickQuestionChip('Library location', Icons.library_books),
                      _buildQuickQuestionChip('Cafeteria', Icons.restaurant),
                      _buildQuickQuestionChip('How to navigate?', Icons.navigation),
                      _buildQuickQuestionChip('Floor info', Icons.stairs),
                      _buildQuickQuestionChip('Help', Icons.help_outline),
                    ],
                  ),
                ],
              ),
            ),
            // Messages List
            Expanded(
              child: messages.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.chat_bubble_outline,
                            size: 64,
                            color: Colors.grey.shade400,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'Start a conversation!',
                            style: TextStyle(
                              fontSize: 16,
                              color: Colors.grey.shade600,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Ask: "Where is CL1?" or "How to get to Library?"',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey.shade500,
                            ),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      itemCount: messages.length,
                      itemBuilder: (_, index) {
                        final msg = messages[index];
                        final isUser = msg['isUser'] as bool;
                        return Container(
                          margin: const EdgeInsets.only(bottom: 8),
                          child: Row(
                            mainAxisAlignment: isUser
                                ? MainAxisAlignment.end
                                : MainAxisAlignment.start,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              if (!isUser)
                                Container(
                                  margin: const EdgeInsets.only(right: 8),
                                  padding: const EdgeInsets.all(8),
                                  decoration: BoxDecoration(
                                    color: Colors.orange.withValues(alpha: 0.1),
                                    shape: BoxShape.circle,
                                  ),
                                  child: const Icon(
                                    Icons.smart_toy,
                                    color: Colors.orange,
                                    size: 16,
                                  ),
                                ),
                              Flexible(
                                child: Container(
                                  padding: const EdgeInsets.all(12),
                                  decoration: BoxDecoration(
                                    color: isUser
                                        ? Colors.orange
                                        : Colors.white,
                                    borderRadius: BorderRadius.circular(16),
                                    boxShadow: [
                                      BoxShadow(
                                        color: Colors.black.withValues(alpha: 0.05),
                                        blurRadius: 4,
                                        offset: const Offset(0, 2),
                                      ),
                                    ],
                                  ),
                                  child: Text(
                                    (msg['text'] as String)
                                        .replaceFirst(isUser ? 'You: ' : 'Bot: ', ''),
                                    style: TextStyle(
                                      color: isUser ? Colors.white : Colors.black87,
                                      fontSize: 14,
                                    ),
                                  ),
                                ),
                              ),
                              if (isUser)
                                Container(
                                  margin: const EdgeInsets.only(left: 8),
                                  padding: const EdgeInsets.all(8),
                                  decoration: BoxDecoration(
                                    color: Colors.blue.withValues(alpha: 0.1),
                                    shape: BoxShape.circle,
                                  ),
                                  child: const Icon(
                                    Icons.person,
                                    color: Colors.blue,
                                    size: 16,
                                  ),
                                ),
                            ],
                          ),
                        );
                      },
                    ),
            ),
            // Input Area
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.05),
                    blurRadius: 8,
                    offset: const Offset(0, -2),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: inputController,
                      decoration: InputDecoration(
                        hintText: 'Ask about buildings, rooms, facilities...',
                        hintStyle: TextStyle(
                          color: Colors.grey.shade400,
                          fontSize: 14,
                        ),
                        filled: true,
                        fillColor: Colors.grey.shade100,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: BorderSide.none,
                        ),
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 20,
                          vertical: 14,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.orange,
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: Colors.orange.withValues(alpha: 0.3),
                          blurRadius: 8,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: IconButton(
                      onPressed: loading ? null : sendMessage,
                      icon: loading
                          ? const SizedBox.square(
                              dimension: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Icon(Icons.send, color: Colors.white),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  String errorMessage = '';
  bool isLoading = false;
  bool _obscurePassword = true;

  void login() async {
    setState(() => isLoading = true);
    final user = await DatabaseHelper.instance.getUser(
      emailController.text,
      passwordController.text,
    );
    setState(() => isLoading = false);
    if (!mounted) return;
    if (user != null && (user['role'] == 'admin' || user['role'] == 'dean')) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const AdminLoadingScreen()),
      );
    } else {
      setState(() => errorMessage = 'Invalid email or password');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Logo at top left
              Row(
                children: [
                  Image.asset(
                    'lib/map/SEAITlogo.png',
                    height: 60,
                    fit: BoxFit.contain,
                    errorBuilder: (context, error, stackTrace) =>
                        const Icon(Icons.school, size: 60, color: Colors.orange),
                  ),
                  const SizedBox(width: 12),
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'SEAIT',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.orange,
                        ),
                      ),
                      Text(
                        'Admin Portal',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 48),
              // Welcome text
              const Text(
                'Welcome Back',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Please sign in to continue',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey,
                ),
              ),
              const SizedBox(height: 32),
              // Username field
              TextField(
                controller: emailController,
                keyboardType: TextInputType.text,
                decoration: InputDecoration(
                  labelText: 'Username',
                  hintText: 'Enter your username',
                  prefixIcon: const Icon(Icons.person_outline),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: Colors.grey.shade300),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Colors.orange, width: 2),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              // Password field with show/hide toggle
              TextField(
                controller: passwordController,
                obscureText: _obscurePassword,
                decoration: InputDecoration(
                  labelText: 'Password',
                  hintText: 'Enter your password',
                  prefixIcon: const Icon(Icons.lock_outlined),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscurePassword ? Icons.visibility_off : Icons.visibility,
                      color: Colors.grey,
                    ),
                    onPressed: () {
                      setState(() {
                        _obscurePassword = !_obscurePassword;
                      });
                    },
                  ),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: Colors.grey.shade300),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Colors.orange, width: 2),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              // Forgot password
              Align(
                alignment: Alignment.centerRight,
                child: TextButton(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Contact admin to reset password')),
                    );
                  },
                  child: const Text('Forgot Password?'),
                ),
              ),
              const SizedBox(height: 24),
              // Error message
              if (errorMessage.isNotEmpty)
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.red.shade200),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.error_outline, color: Colors.red.shade700, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          errorMessage,
                          style: TextStyle(color: Colors.red.shade700),
                        ),
                      ),
                    ],
                  ),
                ),
              if (errorMessage.isNotEmpty) const SizedBox(height: 16),
              // Login button
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: isLoading ? null : login,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.orange,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    elevation: 2,
                  ),
                  child: isLoading
                      ? const SizedBox.square(
                          dimension: 24,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Text(
                          'Sign In',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                ),
              ),
              const Spacer(),
              // Help text
              Center(
                child: TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('Back to App'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class AdminLoadingScreen extends StatefulWidget {
  const AdminLoadingScreen({super.key});

  @override
  State<AdminLoadingScreen> createState() => _AdminLoadingScreenState();
}

class _AdminLoadingScreenState extends State<AdminLoadingScreen>
    with TickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnimation;
  late Animation<double> _scaleAnimation;
  late Animation<double> _rotateAnimation;

  @override
  void initState() {
    super.initState();

    _controller = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.5, curve: Curves.easeIn),
      ),
    );

    _scaleAnimation = Tween<double>(begin: 0.5, end: 1.2).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.6, curve: Curves.elasticOut),
      ),
    );

    _rotateAnimation = Tween<double>(begin: 0.0, end: 2.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.2, 0.8, curve: Curves.easeInOut),
      ),
    );

    _controller.forward();

    Timer(const Duration(seconds: 3), () {
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const AdminPanelScreen()),
        );
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.orange,
      body: Center(
        child: AnimatedBuilder(
          animation: _controller,
          builder: (context, child) {
            return FadeTransition(
              opacity: _fadeAnimation,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Transform.rotate(
                    angle: _rotateAnimation.value * 3.14159,
                    child: Transform.scale(
                      scale: _scaleAnimation.value,
                      child: Container(
                        padding: const EdgeInsets.all(24),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withValues(alpha: 0.2),
                              blurRadius: 20,
                              offset: const Offset(0, 10),
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.admin_panel_settings,
                          size: 64,
                          color: Colors.orange,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 40),
                  const Text(
                    'Loading Admin Panel...',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: 200,
                    child: LinearProgressIndicator(
                      value: _controller.value,
                      backgroundColor: Colors.white.withValues(alpha: 0.3),
                      valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                  const SizedBox(height: 24),
                  Text(
                    'Authenticating...',
                    style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.8),
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}

// Map Editor Screen for editing campus map markers
class MapEditorScreen extends StatefulWidget {
  final List<Map<String, dynamic>> markers;
  final Function(List<Map<String, dynamic>>) onMarkersUpdated;

  const MapEditorScreen({
    super.key,
    required this.markers,
    required this.onMarkersUpdated,
  });

  @override
  State<MapEditorScreen> createState() => _MapEditorScreenState();
}

class _MapEditorScreenState extends State<MapEditorScreen> {
  late List<Map<String, dynamic>> _markers;
  int? _selectedMarkerIndex;

  @override
  void initState() {
    super.initState();
    _markers = List<Map<String, dynamic>>.from(widget.markers);
  }

  void _addMarker() {
    setState(() {
      _markers.add({
        'id': DateTime.now().millisecondsSinceEpoch,
        'name': 'New Marker ${_markers.length + 1}',
        'type': 'custom',
        'x': 100.0 + (_markers.length * 20),
        'y': 100.0 + (_markers.length * 20),
      });
    });
  }

  void _updateMarkerPosition(int index, Offset position) {
    setState(() {
      _markers[index]['x'] = position.dx;
      _markers[index]['y'] = position.dy;
    });
  }

  void _deleteMarker(int index) {
    setState(() {
      _markers.removeAt(index);
      _selectedMarkerIndex = null;
    });
  }

  void _saveChanges() {
    widget.onMarkersUpdated(_markers);
    Navigator.pop(context);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Map markers updated successfully')),
    );
  }

  void _showMarkerDialog(int index) {
    final marker = _markers[index];
    final nameController = TextEditingController(text: marker['name']?.toString() ?? '');
    final typeController = TextEditingController(text: marker['type']?.toString() ?? '');

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Edit Marker'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameController,
              decoration: const InputDecoration(
                labelText: 'Name',
                prefixIcon: Icon(Icons.label),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: typeController,
              decoration: const InputDecoration(
                labelText: 'Type',
                prefixIcon: Icon(Icons.category),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              setState(() {
                _markers[index]['name'] = nameController.text;
                _markers[index]['type'] = typeController.text;
              });
              Navigator.pop(context);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Map Editor'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.save),
            onPressed: _saveChanges,
            tooltip: 'Save Changes',
          ),
        ],
      ),
      body: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.grey.shade100,
              border: Border(bottom: BorderSide(color: Colors.grey.shade300)),
            ),
            child: Row(
              children: [
                ElevatedButton.icon(
                  onPressed: _addMarker,
                  icon: const Icon(Icons.add_location),
                  label: const Text('Add Marker'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                  ),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.green.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    '${_markers.length} markers',
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      color: Colors.green,
                    ),
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: InteractiveViewer(
              boundaryMargin: const EdgeInsets.all(100),
              minScale: 0.5,
              maxScale: 3.0,
              child: Container(
                width: 800,
                height: 600,
                color: Colors.grey.shade200,
                child: Stack(
                  children: [
                    CustomPaint(
                      size: const Size(800, 600),
                      painter: GridPainter(),
                    ),
                    ..._markers.asMap().entries.map((entry) {
                      final index = entry.key;
                      final marker = entry.value;
                      final isSelected = _selectedMarkerIndex == index;
                      return Positioned(
                        left: (marker['x'] ?? 0).toDouble() - 15,
                        top: (marker['y'] ?? 0).toDouble() - 30,
                        child: GestureDetector(
                          onPanUpdate: (details) {
                            final newPos = Offset(
                              marker['x'] + details.delta.dx,
                              marker['y'] + details.delta.dy,
                            );
                            _updateMarkerPosition(index, newPos);
                          },
                          onTap: () {
                            setState(() {
                              _selectedMarkerIndex = index;
                            });
                            _showMarkerDialog(index);
                          },
                          onLongPress: () => _deleteMarker(index),
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                                decoration: BoxDecoration(
                                  color: isSelected ? Colors.blue : Colors.red,
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  marker['name'] ?? 'Marker',
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                              Icon(
                                Icons.location_on,
                                color: isSelected ? Colors.blue : Colors.red,
                                size: 30,
                              ),
                            ],
                          ),
                        ),
                      );
                    }),
                  ],
                ),
              ),
            ),
          ),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.grey.shade100,
              border: Border(top: BorderSide(color: Colors.grey.shade300)),
            ),
            child: const Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.touch_app, size: 16, color: Colors.grey),
                SizedBox(width: 8),
                Text(
                  'Tap marker to edit • Long press to delete • Drag to move',
                  style: TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class GridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.grey.shade400
      ..strokeWidth = 0.5;

    for (double i = 0; i < size.width; i += 50) {
      canvas.drawLine(Offset(i, 0), Offset(i, size.height), paint);
    }
    for (double i = 0; i < size.height; i += 50) {
      canvas.drawLine(Offset(0, i), Offset(size.width, i), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

// Admin Settings Screen - Module for managing admin configuration
// ============================================================================
// SECTION 1: Class Definition & State Variables
// ============================================================================
class AdminSettingsScreen extends StatefulWidget {
  const AdminSettingsScreen({super.key});

  @override
  State<AdminSettingsScreen> createState() => _AdminSettingsScreenState();
}

class _AdminSettingsScreenState extends State<AdminSettingsScreen> {
  // -------------------------------------------------------------------------
  // STATE VARIABLES - Module: Settings State Management
  // -------------------------------------------------------------------------
  bool _darkMode = false;
  bool _notifications = true;
  bool _autoSave = true;
  String _selectedLanguage = 'English';
  String _campusName = 'SEAIT Campus';

  // ============================================================================
  // SECTION 2: Build Method - Main UI Structure
  // ============================================================================
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // -----------------------------------------------------------------------
      // MODULE: App Bar Configuration
      // -----------------------------------------------------------------------
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.settings),
            SizedBox(width: 8),
            Text('Admin Settings'),
          ],
        ),
        backgroundColor: Colors.orange,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      // -----------------------------------------------------------------------
      // MODULE: Settings Body Content
      // -----------------------------------------------------------------------
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
          // SUB-SECTION: Profile Section
          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
          _buildSectionHeader('Admin Profile', Icons.person_outline),
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Column(
              children: [
                ListTile(
                  leading: const CircleAvatar(
                    backgroundColor: Colors.orange,
                    child: Icon(Icons.admin_panel_settings, color: Colors.white),
                  ),
                  title: const Text('Administrator'),
                  subtitle: const Text('admin@seait.edu.ph'),
                  trailing: TextButton(
                    onPressed: () {},
                    child: const Text('Edit'),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
          // SUB-SECTION: General Settings
          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
          _buildSectionHeader('General Settings', Icons.tune),
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Column(
              children: [
                SwitchListTile(
                  secondary: const Icon(Icons.dark_mode),
                  title: const Text('Dark Mode'),
                  subtitle: const Text('Enable dark theme for admin panel'),
                  value: _darkMode,
                  onChanged: (value) {
                    setState(() => _darkMode = value);
                  },
                ),
                const Divider(height: 1),
                SwitchListTile(
                  secondary: const Icon(Icons.notifications),
                  title: const Text('Notifications'),
                  subtitle: const Text('Receive system notifications'),
                  value: _notifications,
                  onChanged: (value) {
                    setState(() => _notifications = value);
                  },
                ),
                const Divider(height: 1),
                SwitchListTile(
                  secondary: const Icon(Icons.save),
                  title: const Text('Auto Save'),
                  subtitle: const Text('Automatically save changes'),
                  value: _autoSave,
                  onChanged: (value) {
                    setState(() => _autoSave = value);
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
          // SUB-SECTION: Campus Settings
          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
          _buildSectionHeader('Campus Settings', Icons.school),
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.business),
                  title: const Text('Campus Name'),
                  subtitle: Text(_campusName),
                  trailing: const Icon(Icons.edit, color: Colors.grey),
                  onTap: () => _showEditDialog('Campus Name', _campusName, (value) {
                    setState(() => _campusName = value);
                  }),
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.language),
                  title: const Text('Language'),
                  subtitle: Text(_selectedLanguage),
                  trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                  onTap: () => _showLanguageSelector(),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
          // SUB-SECTION: Data Management
          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
          _buildSectionHeader('Data Management', Icons.storage),
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.backup, color: Colors.blue),
                  title: const Text('Backup Data'),
                  subtitle: const Text('Export database backup'),
                  trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Backup feature coming soon')),
                    );
                  },
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.restore, color: Colors.green),
                  title: const Text('Restore Data'),
                  subtitle: const Text('Import from backup file'),
                  trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Restore feature coming soon')),
                    );
                  },
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.delete_sweep, color: Colors.red),
                  title: const Text('Clear Cache'),
                  subtitle: const Text('Remove temporary files'),
                  trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                  onTap: () {
                    showDialog(
                      context: context,
                      builder: (context) => AlertDialog(
                        title: const Text('Clear Cache'),
                        content: const Text('Are you sure you want to clear the cache?'),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.pop(context),
                            child: const Text('Cancel'),
                          ),
                          TextButton(
                            onPressed: () {
                              Navigator.pop(context);
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Cache cleared successfully')),
                              );
                            },
                            child: const Text('Clear', style: TextStyle(color: Colors.red)),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
          // SUB-SECTION: About Information
          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
          _buildSectionHeader('About', Icons.info_outline),
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: const Column(
              children: [
                ListTile(
                  leading: Icon(Icons.app_shortcut),
                  title: Text('App Version'),
                  subtitle: Text('v4.0.1'),
                ),
                Divider(height: 1),
                ListTile(
                  leading: Icon(Icons.code),
                  title: Text('Build Number'),
                  subtitle: Text('20250327'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 32),

          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
          // SUB-SECTION: Logout Button
          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () {
                Navigator.of(context).pushAndRemoveUntil(
                  MaterialPageRoute(builder: (_) => MainNavigationShell(
                    isDarkMode: _darkMode,
                    onThemeChanged: (_) {},
                  )),
                  (route) => false,
                );
              },
              icon: const Icon(Icons.logout),
              label: const Text('Logout from Admin'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  // ============================================================================
  // SECTION 3: Helper Widget Methods
  // ============================================================================

  // -------------------------------------------------------------------------
  // MODULE: Section Header Builder
  // Lines: Builds a labeled header for each settings section
  // -------------------------------------------------------------------------
  Widget _buildSectionHeader(String title, IconData icon) {
    return Padding(
      padding: const EdgeInsets.only(left: 8, bottom: 8),
      child: Row(
        children: [
          Icon(icon, size: 18, color: Colors.grey.shade600),
          const SizedBox(width: 8),
          Text(
            title,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: Colors.grey.shade700,
            ),
          ),
        ],
      ),
    );
  }

  // ============================================================================
  // SECTION 4: Dialog Methods
  // ============================================================================

  // -------------------------------------------------------------------------
  // MODULE: Edit Dialog
  // Lines: Shows dialog for editing text fields (campus name, etc.)
  // -------------------------------------------------------------------------
  void _showEditDialog(String title, String currentValue, Function(String) onSave) {
    final controller = TextEditingController(text: currentValue);
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Edit $title'),
        content: TextField(
          controller: controller,
          decoration: InputDecoration(
            labelText: title,
            border: const OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              onSave(controller.text);
              Navigator.pop(context);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  // -------------------------------------------------------------------------
  // MODULE: Language Selector Dialog
  // Lines: Shows dialog for selecting app language
  // -------------------------------------------------------------------------
  void _showLanguageSelector() {
    final languages = ['English', 'Filipino', 'Cebuano'];
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Select Language'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: languages.map((lang) => ListTile(
            title: Text(lang),
            trailing: _selectedLanguage == lang ? const Icon(Icons.check, color: Colors.orange) : null,
            onTap: () {
              setState(() => _selectedLanguage = lang);
              Navigator.pop(context);
            },
          )).toList(),
        ),
      ),
    );
  }
}
// ============================================================================
// END OF AdminSettingsScreen MODULE
// ============================================================================
