import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'dart:convert';
import 'package:crypto/crypto.dart';

/// Enhanced Database Schema - 21 Tables
/// ============================================
/// 1. users - Admin/user accounts with 3-tier role system
/// 2. facilities - Campus buildings and facilities
/// 3. rooms - Rooms within facilities with floor info
/// 4. notifications - System notifications
/// 5. ratings - User feedback ratings
/// 6. map_markers - Visual map markers
/// 7. app_usage - Usage analytics
/// 8. navigation_nodes - Dijkstra pathfinding nodes
/// 9. navigation_edges - Path connections between nodes
/// 10. faq_entries - FAQ database for chatbot
/// 11. ai_chat_logs - AI conversation history
/// 12. feedback_flags - Flagged content for review
/// 13. search_history - User search analytics
/// 14. usage_analytics - Detailed usage metrics
/// 15. admin_audit_log - Administrative action tracking
/// 16. notification_types - Notification categories
/// 17. notification_preferences - User notification settings
/// 18. device_preferences - Device-specific settings
/// 19. map_labels - Custom map labels
/// 20. app_config - Application configuration
/// 21. connectivity_log - Network connectivity tracking
/// 22. departments - Department data (Bonus table for role-based access)

class DatabaseHelper {
  static final DatabaseHelper instance = DatabaseHelper._init();
  static Database? _database;

  DatabaseHelper._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB('guidemap_v2.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);

    return await openDatabase(
      path,
      version: 3,
      onCreate: _createDB,
      onUpgrade: _onUpgrade,
    );
  }

  /// SHA-256 Password Hashing
  String hashPassword(String password) {
    final bytes = utf8.encode(password);
    final digest = sha256.convert(bytes);
    return digest.toString();
  }

  Future _onUpgrade(Database db, int oldVersion, int newVersion) async {
    if (oldVersion < 2) {
      await _migrateToV2(db);
    }
    if (oldVersion < 3) {
      await _migrateToV3(db);
    }
  }

  Future _migrateToV2(Database db) async {
    // Add soft delete columns to existing tables
    await db.execute('ALTER TABLE facilities ADD COLUMN is_active INTEGER DEFAULT 1');
    await db.execute('ALTER TABLE rooms ADD COLUMN is_active INTEGER DEFAULT 1');
    await db.execute('ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1');
    await db.execute('ALTER TABLE users ADD COLUMN department_id INTEGER');
    await db.execute('ALTER TABLE rooms ADD COLUMN floor INTEGER DEFAULT 1');
    await db.execute('ALTER TABLE rooms ADD COLUMN room_type TEXT DEFAULT \'classroom\'');
    await db.execute('ALTER TABLE rooms ADD COLUMN capacity INTEGER DEFAULT 30');
  }

  Future _migrateToV3(Database db) async {
    // Create all navigation and audit tables
    await _createNavigationTables(db);
    await _createAuditAndAnalyticsTables(db);
    await _createConfigurationTables(db);
  }

  Future _createDB(Database db, int version) async {
    // ============================================
    // TABLE 1: users - Enhanced with 3-tier roles
    // ============================================
    // Roles: 'safety_security', 'program_head', 'dean', 'admin', 'user'
    await db.execute('''
      CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT,
        role TEXT NOT NULL DEFAULT 'user',
        department_id INTEGER,
        is_active INTEGER DEFAULT 1,
        last_login TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (department_id) REFERENCES departments (id) ON DELETE SET NULL
      )
    ''');

    // ============================================
    // TABLE 2: departments - For role-based access
    // ============================================
    await db.execute('''
      CREATE TABLE departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT UNIQUE NOT NULL,
        description TEXT,
        head_user_id INTEGER,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (head_user_id) REFERENCES users (id) ON DELETE SET NULL
      )
    ''');

    // ============================================
    // TABLE 3: facilities - Enhanced with soft delete
    // ============================================
    await db.execute('''
      CREATE TABLE facilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        building_code TEXT,
        department_id INTEGER,
        latitude REAL,
        longitude REAL,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (department_id) REFERENCES departments (id) ON DELETE SET NULL
      )
    ''');

    // ============================================
    // TABLE 4: rooms - Enhanced with floor and room type
    // ============================================
    await db.execute('''
      CREATE TABLE rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        facility_id INTEGER,
        name TEXT NOT NULL,
        description TEXT,
        room_number TEXT,
        floor INTEGER DEFAULT 1,
        room_type TEXT DEFAULT 'classroom',
        capacity INTEGER DEFAULT 30,
        is_office INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (facility_id) REFERENCES facilities (id) ON DELETE CASCADE
      )
    ''');

    // ============================================
    // TABLE 5: notifications
    // ============================================
    await db.execute('''
      CREATE TABLE notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        notification_type_id INTEGER,
        is_read INTEGER DEFAULT 0,
        priority TEXT DEFAULT 'normal',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (notification_type_id) REFERENCES notification_types (id) ON DELETE SET NULL
      )
    ''');

    // ============================================
    // TABLE 6: ratings - Enhanced with category
    // ============================================
    await db.execute('''
      CREATE TABLE ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        facility_id INTEGER,
        room_id INTEGER,
        rating INTEGER NOT NULL,
        comment TEXT,
        category TEXT DEFAULT 'general',
        is_anonymous INTEGER DEFAULT 1,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL,
        FOREIGN KEY (facility_id) REFERENCES facilities (id) ON DELETE CASCADE,
        FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE
      )
    ''');

    // ============================================
    // TABLE 7: map_markers - Enhanced with facility reference
    // ============================================
    await db.execute('''
      CREATE TABLE map_markers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        facility_id INTEGER,
        name TEXT NOT NULL,
        x_position REAL NOT NULL,
        y_position REAL NOT NULL,
        type TEXT NOT NULL,
        icon_name TEXT DEFAULT 'location_on',
        color_hex TEXT DEFAULT '#FF9800',
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (facility_id) REFERENCES facilities (id) ON DELETE SET NULL
      )
    ''');

    // ============================================
    // TABLE 8: app_usage
    // ============================================
    await db.execute('''
      CREATE TABLE app_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        session_date TEXT NOT NULL,
        session_duration INTEGER DEFAULT 0,
        screen_views INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
      )
    ''');

    // Create navigation tables
    await _createNavigationTables(db);

    // Create audit and analytics tables
    await _createAuditAndAnalyticsTables(db);

    // Create configuration tables
    await _createConfigurationTables(db);

    // Insert default data
    await _insertDefaultData(db);
  }

  Future _createNavigationTables(Database db) async {
    // ============================================
    // TABLE 9: navigation_nodes - For Dijkstra's algorithm
    // ============================================
    await db.execute('''
      CREATE TABLE navigation_nodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        node_type TEXT NOT NULL,
        facility_id INTEGER,
        room_id INTEGER,
        x_position REAL NOT NULL,
        y_position REAL NOT NULL,
        floor INTEGER DEFAULT 1,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (facility_id) REFERENCES facilities (id) ON DELETE SET NULL,
        FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE SET NULL
      )
    ''');

    // ============================================
    // TABLE 10: navigation_edges - Path connections
    // ============================================
    await db.execute('''
      CREATE TABLE navigation_edges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_node_id INTEGER NOT NULL,
        to_node_id INTEGER NOT NULL,
        weight REAL NOT NULL DEFAULT 1.0,
        edge_type TEXT DEFAULT 'walkway',
        is_accessible INTEGER DEFAULT 1,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (from_node_id) REFERENCES navigation_nodes (id) ON DELETE CASCADE,
        FOREIGN KEY (to_node_id) REFERENCES navigation_nodes (id) ON DELETE CASCADE,
        UNIQUE(from_node_id, to_node_id)
      )
    ''');
  }

  Future _createAuditAndAnalyticsTables(Database db) async {
    // ============================================
    // TABLE 11: faq_entries - For chatbot offline mode
    // ============================================
    await db.execute('''
      CREATE TABLE faq_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        keywords TEXT,
        category TEXT DEFAULT 'general',
        hit_count INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    ''');

    // ============================================
    // TABLE 12: ai_chat_logs
    // ============================================
    await db.execute('''
      CREATE TABLE ai_chat_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        query TEXT NOT NULL,
        response TEXT NOT NULL,
        response_time_ms INTEGER,
        was_helpful INTEGER,
        mode TEXT DEFAULT 'offline',
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
      )
    ''');

    // ============================================
    // TABLE 13: feedback_flags
    // ============================================
    await db.execute('''
      CREATE TABLE feedback_flags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        rating_id INTEGER,
        reason TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        resolved_by INTEGER,
        resolved_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL,
        FOREIGN KEY (rating_id) REFERENCES ratings (id) ON DELETE CASCADE,
        FOREIGN KEY (resolved_by) REFERENCES users (id) ON DELETE SET NULL
      )
    ''');

    // ============================================
    // TABLE 14: search_history
    // ============================================
    await db.execute('''
      CREATE TABLE search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        query TEXT NOT NULL,
        results_count INTEGER DEFAULT 0,
        was_clicked INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
      )
    ''');

    // ============================================
    // TABLE 15: usage_analytics
    // ============================================
    await db.execute('''
      CREATE TABLE usage_analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        event_type TEXT NOT NULL,
        event_data TEXT,
        screen_name TEXT,
        session_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
      )
    ''');

    // ============================================
    // TABLE 16: admin_audit_log
    // ============================================
    await db.execute('''
      CREATE TABLE admin_audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id INTEGER,
        old_values TEXT,
        new_values TEXT,
        ip_address TEXT,
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
      )
    ''');
  }

  Future _createConfigurationTables(Database db) async {
    // ============================================
    // TABLE 17: notification_types
    // ============================================
    await db.execute('''
      CREATE TABLE notification_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        icon_name TEXT DEFAULT 'notifications',
        color_hex TEXT DEFAULT '#FF9800',
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    ''');

    // ============================================
    // TABLE 18: notification_preferences
    // ============================================
    await db.execute('''
      CREATE TABLE notification_preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        notification_type_id INTEGER NOT NULL,
        is_enabled INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (notification_type_id) REFERENCES notification_types (id) ON DELETE CASCADE,
        UNIQUE(user_id, notification_type_id)
      )
    ''');

    // ============================================
    // TABLE 19: device_preferences
    // ============================================
    await db.execute('''
      CREATE TABLE device_preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        device_id TEXT NOT NULL,
        dark_mode INTEGER DEFAULT 0,
        language TEXT DEFAULT 'en',
        font_scale REAL DEFAULT 1.0,
        high_contrast INTEGER DEFAULT 0,
        reduce_animations INTEGER DEFAULT 0,
        last_sync TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
      )
    ''');

    // ============================================
    // TABLE 20: map_labels
    // ============================================
    await db.execute('''
      CREATE TABLE map_labels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        label_text TEXT NOT NULL,
        x_position REAL NOT NULL,
        y_position REAL NOT NULL,
        font_size INTEGER DEFAULT 14,
        color_hex TEXT DEFAULT '#000000',
        rotation REAL DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    ''');

    // ============================================
    // TABLE 21: app_config
    // ============================================
    await db.execute('''
      CREATE TABLE app_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        config_key TEXT NOT NULL UNIQUE,
        config_value TEXT NOT NULL,
        description TEXT,
        updated_by INTEGER,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (updated_by) REFERENCES users (id) ON DELETE SET NULL
      )
    ''');

    // ============================================
    // TABLE 22: connectivity_log
    // ============================================
    await db.execute('''
      CREATE TABLE connectivity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        is_online INTEGER NOT NULL,
        connection_type TEXT,
        latency_ms INTEGER,
        error_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
      )
    ''');
  }

  Future _insertDefaultData(Database db) async {
    // Insert departments
    final departments = [
      {'name': 'Computer Science', 'code': 'CS', 'description': 'Computer Science Department'},
      {'name': 'Information Technology', 'code': 'IT', 'description': 'Information Technology Department'},
      {'name': 'Engineering', 'code': 'ENG', 'description': 'Engineering Department'},
      {'name': 'Safety and Security', 'code': 'SAS', 'description': 'Campus Safety and Security Office'},
      {'name': 'Administration', 'code': 'ADMIN', 'description': 'School Administration'},
    ];

    for (var dept in departments) {
      await db.insert('departments', dept);
    }

    // Insert users with hashed passwords and 3-tier roles
    final users = [
      {
        'username': 'admin',
        'password': hashPassword('admin123'),
        'email': 'admin@seait.edu.ph',
        'role': 'dean',
        'department_id': 5,
      },
      {
        'username': 'safety',
        'password': hashPassword('safety123'),
        'email': 'safety@seait.edu.ph',
        'role': 'safety_security',
        'department_id': 4,
      },
      {
        'username': 'cict_head',
        'password': hashPassword('cict123'),
        'email': 'cict.head@seait.edu.ph',
        'role': 'program_head',
        'department_id': 2,
      },
    ];

    for (var user in users) {
      await db.insert('users', user);
    }

    // Insert facilities with coordinates
    final facilities = [
      {'name': 'RST Building', 'description': 'Research Science and Technology Building', 'building_code': 'RST', 'latitude': 14.1001, 'longitude': 121.0801},
      {'name': 'JST Building', 'description': 'Junior Science and Technology Building', 'building_code': 'JST', 'latitude': 14.1002, 'longitude': 121.0802},
      {'name': 'MST Building', 'description': 'Main Science and Technology Building', 'building_code': 'MST', 'latitude': 14.1003, 'longitude': 121.0803},
      {'name': 'Basic Education Building', 'description': 'Basic Education Department', 'building_code': 'BED', 'latitude': 14.1004, 'longitude': 121.0804},
      {'name': 'Gymnasium', 'description': 'Sports and Activities Center', 'building_code': 'GYM', 'latitude': 14.1005, 'longitude': 121.0805},
      {'name': 'Library', 'description': 'School Library and Resource Center', 'building_code': 'LIB', 'latitude': 14.1006, 'longitude': 121.0806},
      {'name': 'Registrar Office', 'description': 'Student Records and Enrollment', 'building_code': 'REG', 'latitude': 14.1007, 'longitude': 121.0807},
      {'name': 'Cafeteria', 'description': 'Main Cafeteria and Dining Area', 'building_code': 'CAF', 'latitude': 14.1008, 'longitude': 121.0808},
      {'name': 'Playground', 'description': 'Student Recreation Area', 'building_code': 'PLY', 'latitude': 14.1009, 'longitude': 121.0809},
    ];

    for (var facility in facilities) {
      await db.insert('facilities', facility);
    }

    // Insert rooms with floor information
    final rooms = [
      // RST Building - Ground Floor
      {'facility_id': 1, 'name': 'CL1', 'description': 'Computer Lab 1', 'room_number': 'RST-GF-CL1', 'floor': 1, 'room_type': 'computer_lab', 'capacity': 40},
      {'facility_id': 1, 'name': 'CL2', 'description': 'Computer Lab 2', 'room_number': 'RST-GF-CL2', 'floor': 1, 'room_type': 'computer_lab', 'capacity': 40},
      {'facility_id': 1, 'name': 'CR1', 'description': 'Classroom 1', 'room_number': 'RST-GF-CR1', 'floor': 1, 'room_type': 'classroom', 'capacity': 50},
      {'facility_id': 1, 'name': 'CR2', 'description': 'Classroom 2', 'room_number': 'RST-GF-CR2', 'floor': 1, 'room_type': 'classroom', 'capacity': 50},
      // RST Building - 2nd Floor
      {'facility_id': 1, 'name': 'CL3', 'description': 'Computer Lab 3', 'room_number': 'RST-2F-CL3', 'floor': 2, 'room_type': 'computer_lab', 'capacity': 40},
      {'facility_id': 1, 'name': 'CR3', 'description': 'Classroom 3', 'room_number': 'RST-2F-CR3', 'floor': 2, 'room_type': 'classroom', 'capacity': 50},
      {'facility_id': 1, 'name': 'Faculty Office', 'description': 'RST Faculty Office', 'room_number': 'RST-2F-FO', 'floor': 2, 'room_type': 'office', 'capacity': 10, 'is_office': 1},
      // JST Building - Ground Floor
      {'facility_id': 2, 'name': 'CL4', 'description': 'Computer Lab 4', 'room_number': 'JST-GF-CL4', 'floor': 1, 'room_type': 'computer_lab', 'capacity': 35},
      {'facility_id': 2, 'name': 'CR4', 'description': 'Classroom 4', 'room_number': 'JST-GF-CR4', 'floor': 1, 'room_type': 'classroom', 'capacity': 45},
      // JST Building - 2nd Floor
      {'facility_id': 2, 'name': 'CL5', 'description': 'Computer Lab 5', 'room_number': 'JST-2F-CL5', 'floor': 2, 'room_type': 'computer_lab', 'capacity': 35},
      {'facility_id': 2, 'name': 'CR5', 'description': 'Classroom 5', 'room_number': 'JST-2F-CR5', 'floor': 2, 'room_type': 'classroom', 'capacity': 45},
      // MST Building - Multiple Floors
      {'facility_id': 3, 'name': 'CL6', 'description': 'Computer Lab 6', 'room_number': 'MST-GF-CL6', 'floor': 1, 'room_type': 'computer_lab', 'capacity': 50},
      {'facility_id': 3, 'name': 'CL7', 'description': 'Computer Lab 7', 'room_number': 'MST-2F-CL7', 'floor': 2, 'room_type': 'computer_lab', 'capacity': 50},
      {'facility_id': 3, 'name': 'CICT Office', 'description': 'CICT Department Office', 'room_number': 'MST-2F-CICT', 'floor': 2, 'room_type': 'office', 'capacity': 15, 'is_office': 1},
      {'facility_id': 3, 'name': 'Dean Office', 'description': 'College Dean Office', 'room_number': 'MST-3F-DEAN', 'floor': 3, 'room_type': 'office', 'capacity': 8, 'is_office': 1},
      // BED Building
      {'facility_id': 4, 'name': 'BED Classroom 1', 'description': 'Basic Ed Classroom', 'room_number': 'BED-GF-C1', 'floor': 1, 'room_type': 'classroom', 'capacity': 30},
      {'facility_id': 4, 'name': 'BED Classroom 2', 'description': 'Basic Ed Classroom', 'room_number': 'BED-2F-C2', 'floor': 2, 'room_type': 'classroom', 'capacity': 30},
    ];

    for (var room in rooms) {
      await db.insert('rooms', room);
    }

    // Insert navigation nodes for pathfinding
    final nodes = [
      // Main Gate
      {'name': 'Main Gate', 'node_type': 'entrance', 'x_position': 0.5, 'y_position': 0.9, 'floor': 0},
      // Building connections
      {'name': 'RST Node', 'node_type': 'building', 'facility_id': 1, 'x_position': 0.3, 'y_position': 0.5, 'floor': 1},
      {'name': 'JST Node', 'node_type': 'building', 'facility_id': 2, 'x_position': 0.5, 'y_position': 0.5, 'floor': 1},
      {'name': 'MST Node', 'node_type': 'building', 'facility_id': 3, 'x_position': 0.7, 'y_position': 0.5, 'floor': 1},
      {'name': 'BED Node', 'node_type': 'building', 'facility_id': 4, 'x_position': 0.2, 'y_position': 0.3, 'floor': 1},
      {'name': 'Gym Node', 'node_type': 'building', 'facility_id': 5, 'x_position': 0.8, 'y_position': 0.3, 'floor': 1},
      {'name': 'Library Node', 'node_type': 'building', 'facility_id': 6, 'x_position': 0.4, 'y_position': 0.2, 'floor': 1},
      {'name': 'Registrar Node', 'node_type': 'building', 'facility_id': 7, 'x_position': 0.6, 'y_position': 0.2, 'floor': 1},
      {'name': 'Cafeteria Node', 'node_type': 'building', 'facility_id': 8, 'x_position': 0.5, 'y_position': 0.7, 'floor': 1},
      {'name': 'Playground Node', 'node_type': 'building', 'facility_id': 9, 'x_position': 0.9, 'y_position': 0.7, 'floor': 1},
    ];

    for (var node in nodes) {
      await db.insert('navigation_nodes', node);
    }

    // Insert navigation edges (pathways)
    final edges = [
      // From Main Gate
      {'from_node_id': 1, 'to_node_id': 9, 'weight': 2.0, 'edge_type': 'walkway'}, // Gate to Cafeteria
      // Cafeteria connections
      {'from_node_id': 9, 'to_node_id': 2, 'weight': 3.0, 'edge_type': 'walkway'}, // Cafeteria to RST
      {'from_node_id': 9, 'to_node_id': 3, 'weight': 2.0, 'edge_type': 'walkway'}, // Cafeteria to JST
      {'from_node_id': 9, 'to_node_id': 4, 'weight': 3.0, 'edge_type': 'walkway'}, // Cafeteria to MST
      // Building connections
      {'from_node_id': 2, 'to_node_id': 5, 'weight': 4.0, 'edge_type': 'walkway'}, // RST to BED
      {'from_node_id': 4, 'to_node_id': 6, 'weight': 3.0, 'edge_type': 'walkway'}, // MST to Gym
      {'from_node_id': 2, 'to_node_id': 7, 'weight': 2.5, 'edge_type': 'walkway'}, // RST to Library
      {'from_node_id': 3, 'to_node_id': 7, 'weight': 1.5, 'edge_type': 'walkway'}, // JST to Library
      {'from_node_id': 3, 'to_node_id': 8, 'weight': 1.5, 'edge_type': 'walkway'}, // JST to Registrar
      {'from_node_id': 4, 'to_node_id': 8, 'weight': 2.0, 'edge_type': 'walkway'}, // MST to Registrar
      {'from_node_id': 4, 'to_node_id': 10, 'weight': 3.0, 'edge_type': 'walkway'}, // MST to Playground
    ];

    for (var edge in edges) {
      await db.insert('navigation_edges', edge);
    }

    // Insert FAQ entries for chatbot
    final faqs = [
      {'question': 'Where is the MST Building?', 'answer': 'The MST (Main Science and Technology) Building is located at the center-right of the campus. From the main gate, walk straight past the cafeteria and turn right.', 'keywords': 'mst,main,building,location', 'category': 'navigation'},
      {'question': 'Where is the JST Building?', 'answer': 'The JST (Junior Science and Technology) Building is in the center of the campus, between the Library and the Cafeteria.', 'keywords': 'jst,junior,building,location', 'category': 'navigation'},
      {'question': 'Where is the RST Building?', 'answer': 'The RST (Research Science and Technology) Building is on the left side of the campus, near the Basic Education Building.', 'keywords': 'rst,research,building,location', 'category': 'navigation'},
      {'question': 'Where is the comfort room?', 'answer': 'Comfort rooms are available on each floor of all buildings. The nearest one to the main gate is in the Cafeteria building.', 'keywords': 'comfort room,cr,restroom,toilet,bathroom', 'category': 'facilities'},
      {'question': 'Where is the library?', 'answer': 'The Library is located behind the JST Building, near the Registrar Office.', 'keywords': 'library,books,study', 'category': 'facilities'},
      {'question': 'How do I navigate to a room?', 'answer': 'Use the Navigate tab at the bottom of the screen. Select your destination building and room, and the app will show you the shortest path from the main gate or your current location.', 'keywords': 'navigate,find,go to,how to', 'category': 'help'},
      {'question': 'Where is the CICT office?', 'answer': 'The CICT office is located on the 2nd floor of the MST Building, room MST-2F-CICT.', 'keywords': 'cict,office,department,location', 'category': 'navigation'},
      {'question': 'What are the library hours?', 'answer': 'The Library is open Monday to Friday, 8:00 AM to 6:00 PM, and Saturday, 8:00 AM to 12:00 PM.', 'keywords': 'library,hours,open,time', 'category': 'facilities'},
      {'question': 'Where is the cafeteria?', 'answer': 'The Cafeteria is located straight ahead from the main gate, between the JST and MST buildings.', 'keywords': 'cafeteria,canteen,food,eat', 'category': 'facilities'},
      {'question': 'Where is the Registrar Office?', 'answer': 'The Registrar Office is located behind the JST Building, next to the Library.', 'keywords': 'registrar,office,enrollment,records', 'category': 'facilities'},
    ];

    for (var faq in faqs) {
      await db.insert('faq_entries', faq);
    }

    // Insert notification types
    final notificationTypes = [
      {'name': 'general', 'description': 'General announcements', 'icon_name': 'notifications', 'color_hex': '#FF9800'},
      {'name': 'navigation', 'description': 'Navigation updates', 'icon_name': 'navigation', 'color_hex': '#2196F3'},
      {'name': 'emergency', 'description': 'Emergency alerts', 'icon_name': 'warning', 'color_hex': '#F44336'},
      {'name': 'facility', 'description': 'Facility updates', 'icon_name': 'business', 'color_hex': '#4CAF50'},
      {'name': 'system', 'description': 'System notifications', 'icon_name': 'settings', 'color_hex': '#9C27B0'},
    ];

    for (var type in notificationTypes) {
      await db.insert('notification_types', type);
    }

    // Insert app config
    final configs = [
      {'config_key': 'app_version', 'config_value': '1.0.0', 'description': 'Current app version'},
      {'config_key': 'offline_mode_enabled', 'config_value': 'true', 'description': 'Allow offline operation'},
      {'config_key': 'qr_code_enabled', 'config_value': 'true', 'description': 'Enable QR code scanning'},
      {'config_key': 'navigation_enabled', 'config_value': 'true', 'description': 'Enable navigation features'},
      {'config_key': 'maintenance_mode', 'config_value': 'false', 'description': 'App maintenance status'},
    ];

    for (var config in configs) {
      await db.insert('app_config', config);
    }
  }

  // ============================================
  // AUTHENTICATION METHODS WITH SHA-256 HASHING
  // ============================================

  Future<Map<String, dynamic>?> getUser(String username, String password) async {
    final db = await database;
    final hashedPassword = hashPassword(password);
    final result = await db.query(
      'users',
      where: 'username = ? AND password = ? AND is_active = 1',
      whereArgs: [username, hashedPassword],
    );
    if (result.isNotEmpty) {
      // Update last login
      await db.update(
        'users',
        {'last_login': DateTime.now().toIso8601String()},
        where: 'id = ?',
        whereArgs: [result.first['id']],
      );
    }
    return result.isNotEmpty ? result.first : null;
  }

  Future<Map<String, dynamic>?> getUserByUsername(String username) async {
    final db = await database;
    final result = await db.query(
      'users',
      where: 'username = ? AND is_active = 1',
      whereArgs: [username],
    );
    return result.isNotEmpty ? result.first : null;
  }

  Future<bool> validatePassword(String username, String password) async {
    final user = await getUser(username, password);
    return user != null;
  }

  // ============================================
  // AUDIT LOGGING
  // ============================================

  Future<int> logAuditAction({
    required int userId,
    required String action,
    required String entityType,
    int? entityId,
    Map<String, dynamic>? oldValues,
    Map<String, dynamic>? newValues,
    String? ipAddress,
    String? userAgent,
  }) async {
    final db = await database;
    return await db.insert('admin_audit_log', {
      'user_id': userId,
      'action': action,
      'entity_type': entityType,
      'entity_id': entityId,
      'old_values': oldValues != null ? jsonEncode(oldValues) : null,
      'new_values': newValues != null ? jsonEncode(newValues) : null,
      'ip_address': ipAddress,
      'user_agent': userAgent,
    });
  }

  Future<List<Map<String, dynamic>>> getAuditLogs({int limit = 100}) async {
    final db = await database;
    return await db.query(
      'admin_audit_log',
      orderBy: 'created_at DESC',
      limit: limit,
    );
  }

  Future<List<Map<String, dynamic>>> getAuditLogsByUser(int userId) async {
    final db = await database;
    return await db.query(
      'admin_audit_log',
      where: 'user_id = ?',
      whereArgs: [userId],
      orderBy: 'created_at DESC',
    );
  }

  // ============================================
  // SOFT DELETE METHODS
  // ============================================

  Future<int> softDeleteUser(int id, int deletedBy) async {
    final db = await database;
    // Log the action first
    final user = await db.query('users', where: 'id = ?', whereArgs: [id]);
    if (user.isNotEmpty) {
      await logAuditAction(
        userId: deletedBy,
        action: 'SOFT_DELETE',
        entityType: 'users',
        entityId: id,
        oldValues: {'is_active': user.first['is_active']},
        newValues: {'is_active': 0},
      );
    }
    return await db.update(
      'users',
      {'is_active': 0},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<int> softDeleteFacility(int id, int deletedBy) async {
    final db = await database;
    final facility = await db.query('facilities', where: 'id = ?', whereArgs: [id]);
    if (facility.isNotEmpty) {
      await logAuditAction(
        userId: deletedBy,
        action: 'SOFT_DELETE',
        entityType: 'facilities',
        entityId: id,
        oldValues: {'is_active': facility.first['is_active']},
        newValues: {'is_active': 0},
      );
    }
    return await db.update(
      'facilities',
      {'is_active': 0},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<int> softDeleteRoom(int id, int deletedBy) async {
    final db = await database;
    final room = await db.query('rooms', where: 'id = ?', whereArgs: [id]);
    if (room.isNotEmpty) {
      await logAuditAction(
        userId: deletedBy,
        action: 'SOFT_DELETE',
        entityType: 'rooms',
        entityId: id,
        oldValues: {'is_active': room.first['is_active']},
        newValues: {'is_active': 0},
      );
    }
    return await db.update(
      'rooms',
      {'is_active': 0},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<int> restoreUser(int id, int restoredBy) async {
    final db = await database;
    await logAuditAction(
      userId: restoredBy,
      action: 'RESTORE',
      entityType: 'users',
      entityId: id,
    );
    return await db.update(
      'users',
      {'is_active': 1},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  // ============================================
  // ROLE-BASED ACCESS CONTROL
  // ============================================

  bool hasPermission(String role, String permission) {
    final permissions = {
      'dean': ['all', 'users', 'facilities', 'rooms', 'audit', 'reports', 'config'],
      'safety_security': ['facilities', 'rooms', 'map_markers', 'navigation'],
      'program_head': ['rooms', 'facilities_view', 'reports_view'],
      'admin': ['users', 'facilities', 'rooms', 'notifications'],
      'user': ['view'],
    };

    final rolePermissions = permissions[role] ?? ['view'];
    return rolePermissions.contains('all') || rolePermissions.contains(permission);
  }

  Future<List<Map<String, dynamic>>> getUsersByRole(String role) async {
    final db = await database;
    return await db.query(
      'users',
      where: 'role = ? AND is_active = 1',
      whereArgs: [role],
      orderBy: 'username',
    );
  }

  Future<List<Map<String, dynamic>>> getUsersByDepartment(int departmentId) async {
    final db = await database;
    return await db.query(
      'users',
      where: 'department_id = ? AND is_active = 1',
      whereArgs: [departmentId],
      orderBy: 'username',
    );
  }

  // ============================================
  // NAVIGATION / PATHFINDING METHODS
  // ============================================

  Future<List<Map<String, dynamic>>> getAllNavigationNodes() async {
    final db = await database;
    return await db.query(
      'navigation_nodes',
      where: 'is_active = 1',
      orderBy: 'name',
    );
  }

  Future<List<Map<String, dynamic>>> getAllNavigationEdges() async {
    final db = await database;
    return await db.query(
      'navigation_edges',
      where: 'is_active = 1',
    );
  }

  Future<Map<String, dynamic>?> getNodeByFacilityId(int facilityId) async {
    final db = await database;
    final result = await db.query(
      'navigation_nodes',
      where: 'facility_id = ? AND is_active = 1',
      whereArgs: [facilityId],
    );
    return result.isNotEmpty ? result.first : null;
  }

  Future<Map<String, dynamic>?> getNodeByRoomId(int roomId) async {
    final db = await database;
    final result = await db.query(
      'navigation_nodes',
      where: 'room_id = ? AND is_active = 1',
      whereArgs: [roomId],
    );
    return result.isNotEmpty ? result.first : null;
  }

  // ============================================
  // FAQ METHODS FOR CHATBOT
  // ============================================

  Future<List<Map<String, dynamic>>> searchFAQs(String query) async {
    final db = await database;
    final keywords = query.toLowerCase().split(' ');
    
    // Build a query that matches any keyword
    final conditions = keywords.map((_) => 'question LIKE ? OR keywords LIKE ?').join(' OR ');
    final args = keywords.expand((k) => ['%$k%', '%$k%']).toList();
    
    final results = await db.query(
      'faq_entries',
      where: '($conditions) AND is_active = 1',
      whereArgs: args,
      orderBy: 'hit_count DESC',
    );
    
    // Update hit count for top result
    if (results.isNotEmpty) {
      final topId = results.first['id'];
      await db.rawUpdate(
        'UPDATE faq_entries SET hit_count = hit_count + 1 WHERE id = ?',
        [topId],
      );
    }
    
    return results;
  }

  Future<List<Map<String, dynamic>>> getFAQsByCategory(String category) async {
    final db = await database;
    return await db.query(
      'faq_entries',
      where: 'category = ? AND is_active = 1',
      whereArgs: [category],
      orderBy: 'hit_count DESC',
    );
  }

  // ============================================
  // USER CRUD WITH HASHING
  // ============================================

  Future<int> insertUser(Map<String, dynamic> user, int createdBy) async {
    final db = await database;
    // Hash password if provided
    if (user.containsKey('password')) {
      user['password'] = hashPassword(user['password']);
    }
    final id = await db.insert('users', user);
    await logAuditAction(
      userId: createdBy,
      action: 'CREATE',
      entityType: 'users',
      entityId: id,
      newValues: {...user, 'password': '[HASHED]'},
    );
    return id;
  }

  Future<int> updateUser(Map<String, dynamic> user, int updatedBy) async {
    final db = await database;
    // Get old values for audit
    final oldUser = await db.query('users', where: 'id = ?', whereArgs: [user['id']]);
    
    // Hash password if provided and changed
    if (user.containsKey('password') && user['password'].toString().isNotEmpty) {
      user['password'] = hashPassword(user['password']);
    } else if (user.containsKey('password')) {
      user.remove('password'); // Don't update if empty
    }
    
    final result = await db.update('users', user, where: 'id = ?', whereArgs: [user['id']]);
    
    await logAuditAction(
      userId: updatedBy,
      action: 'UPDATE',
      entityType: 'users',
      entityId: user['id'],
      oldValues: oldUser.isNotEmpty ? {...oldUser.first, 'password': '[HASHED]'} : null,
      newValues: {...user, 'password': '[HASHED]'},
    );
    return result;
  }

  Future<List<Map<String, dynamic>>> getAllUsers({bool includeInactive = false}) async {
    final db = await database;
    if (includeInactive) {
      return await db.query('users', orderBy: 'username');
    }
    return await db.query('users', where: 'is_active = 1', orderBy: 'username');
  }

  // ============================================
  // FACILITY CRUD
  // ============================================

  Future<int> insertFacility(Map<String, dynamic> facility, int createdBy) async {
    final db = await database;
    final id = await db.insert('facilities', facility);
    await logAuditAction(
      userId: createdBy,
      action: 'CREATE',
      entityType: 'facilities',
      entityId: id,
      newValues: facility,
    );
    return id;
  }

  Future<int> updateFacility(Map<String, dynamic> facility, int updatedBy) async {
    final db = await database;
    final oldFacility = await db.query('facilities', where: 'id = ?', whereArgs: [facility['id']]);
    final result = await db.update('facilities', facility, where: 'id = ?', whereArgs: [facility['id']]);
    
    await logAuditAction(
      userId: updatedBy,
      action: 'UPDATE',
      entityType: 'facilities',
      entityId: facility['id'],
      oldValues: oldFacility.isNotEmpty ? oldFacility.first : null,
      newValues: facility,
    );
    return result;
  }

  Future<List<Map<String, dynamic>>> getAllFacilities({bool includeInactive = false}) async {
    final db = await database;
    if (includeInactive) {
      return await db.query('facilities', orderBy: 'name');
    }
    return await db.query('facilities', where: 'is_active = 1', orderBy: 'name');
  }

  // ============================================
  // ROOM CRUD WITH FLOOR FILTERING
  // ============================================

  Future<int> insertRoom(Map<String, dynamic> room, int createdBy) async {
    final db = await database;
    final id = await db.insert('rooms', room);
    await logAuditAction(
      userId: createdBy,
      action: 'CREATE',
      entityType: 'rooms',
      entityId: id,
      newValues: room,
    );
    return id;
  }

  Future<int> updateRoom(Map<String, dynamic> room, int updatedBy) async {
    final db = await database;
    final oldRoom = await db.query('rooms', where: 'id = ?', whereArgs: [room['id']]);
    final result = await db.update('rooms', room, where: 'id = ?', whereArgs: [room['id']]);
    
    await logAuditAction(
      userId: updatedBy,
      action: 'UPDATE',
      entityType: 'rooms',
      entityId: room['id'],
      oldValues: oldRoom.isNotEmpty ? oldRoom.first : null,
      newValues: room,
    );
    return result;
  }

  Future<List<Map<String, dynamic>>> getAllRooms({bool includeInactive = false}) async {
    final db = await database;
    if (includeInactive) {
      return await db.query('rooms', orderBy: 'name');
    }
    return await db.query('rooms', where: 'is_active = 1', orderBy: 'name');
  }

  Future<List<Map<String, dynamic>>> getRoomsByFacility(int facilityId) async {
    final db = await database;
    return await db.query(
      'rooms',
      where: 'facility_id = ? AND is_active = 1',
      whereArgs: [facilityId],
      orderBy: 'floor, name',
    );
  }

  Future<List<Map<String, dynamic>>> getRoomsByFloor(int facilityId, int floor) async {
    final db = await database;
    return await db.query(
      'rooms',
      where: 'facility_id = ? AND floor = ? AND is_active = 1',
      whereArgs: [facilityId, floor],
      orderBy: 'name',
    );
  }

  Future<List<int>> getAvailableFloors(int facilityId) async {
    final db = await database;
    final result = await db.rawQuery('''
      SELECT DISTINCT floor FROM rooms 
      WHERE facility_id = ? AND is_active = 1 
      ORDER BY floor
    ''', [facilityId]);
    return result.map((r) => r['floor'] as int).toList();
  }

  // ============================================
  // RATING / FEEDBACK METHODS
  // ============================================

  Future<int> insertRating(Map<String, dynamic> rating) async {
    final db = await database;
    return await db.insert('ratings', rating);
  }

  Future<List<Map<String, dynamic>>> getAllRatings({bool includeInactive = false}) async {
    final db = await database;
    if (includeInactive) {
      return await db.query('ratings', orderBy: 'created_at DESC');
    }
    return await db.query('ratings', where: 'is_active = 1', orderBy: 'created_at DESC');
  }

  Future<double> getAverageRating({String? category}) async {
    final db = await database;
    String query = 'SELECT AVG(rating) as avg FROM ratings WHERE is_active = 1';
    List<dynamic> args = [];
    
    if (category != null) {
      query += ' AND category = ?';
      args.add(category);
    }
    
    final result = await db.rawQuery(query, args);
    return result.first['avg'] as double? ?? 0.0;
  }

  // ============================================
  // NOTIFICATION METHODS
  // ============================================

  Future<List<Map<String, dynamic>>> getAllNotifications() async {
    final db = await database;
    return await db.query('notifications', orderBy: 'created_at DESC');
  }

  Future<int> getUnreadNotificationCount() async {
    final db = await database;
    final result = await db.rawQuery('SELECT COUNT(*) as count FROM notifications WHERE is_read = 0');
    return result.first['count'] as int? ?? 0;
  }

  Future<int> markNotificationAsRead(int id) async {
    final db = await database;
    return await db.update('notifications', {'is_read': 1}, where: 'id = ?', whereArgs: [id]);
  }

  Future<int> deleteNotification(int id) async {
    final db = await database;
    return await db.delete('notifications', where: 'id = ?', whereArgs: [id]);
  }

  // ============================================
  // MAP MARKER METHODS
  // ============================================

  Future<List<Map<String, dynamic>>> getAllMapMarkers({bool includeInactive = false}) async {
    final db = await database;
    if (includeInactive) {
      return await db.query('map_markers');
    }
    return await db.query('map_markers', where: 'is_active = 1');
  }

  Future<int> insertMapMarker(Map<String, dynamic> marker) async {
    final db = await database;
    return await db.insert('map_markers', marker);
  }

  Future<int> updateMapMarker(Map<String, dynamic> marker) async {
    final db = await database;
    return await db.update('map_markers', marker, where: 'id = ?', whereArgs: [marker['id']]);
  }

  Future<int> deleteMapMarker(int id) async {
    final db = await database;
    return await db.delete('map_markers', where: 'id = ?', whereArgs: [id]);
  }

  // ============================================
  // SEARCH METHODS
  // ============================================

  Future<List<Map<String, dynamic>>> searchFacilitiesAndRooms(String query) async {
    final db = await database;
    final searchTerm = '%$query%';
    
    // Search facilities
    final facilities = await db.query(
      'facilities',
      where: '(name LIKE ? OR description LIKE ? OR building_code LIKE ?) AND is_active = 1',
      whereArgs: [searchTerm, searchTerm, searchTerm],
    );
    
    // Search rooms
    final rooms = await db.rawQuery('''
      SELECT r.*, f.name as facility_name 
      FROM rooms r 
      JOIN facilities f ON r.facility_id = f.id 
      WHERE (r.name LIKE ? OR r.description LIKE ? OR r.room_number LIKE ?) 
      AND r.is_active = 1 AND f.is_active = 1
    ''', [searchTerm, searchTerm, searchTerm]);
    
    // Combine results
    final results = <Map<String, dynamic>>[];
    for (var f in facilities) {
      results.add({...f, 'result_type': 'facility'});
    }
    for (var r in rooms) {
      results.add({...r, 'result_type': 'room'});
    }
    
    return results;
  }

  Future<int> logSearch(String query, int resultsCount, {int? userId, bool wasClicked = false}) async {
    final db = await database;
    return await db.insert('search_history', {
      'user_id': userId,
      'query': query,
      'results_count': resultsCount,
      'was_clicked': wasClicked ? 1 : 0,
    });
  }

  // ============================================
  // APP CONFIG METHODS
  // ============================================

  Future<String?> getConfig(String key) async {
    final db = await database;
    final result = await db.query(
      'app_config',
      where: 'config_key = ?',
      whereArgs: [key],
    );
    return result.isNotEmpty ? result.first['config_value'] as String : null;
  }

  Future<int> setConfig(String key, String value, {int? updatedBy, String? description}) async {
    final db = await database;
    final existing = await db.query('app_config', where: 'config_key = ?', whereArgs: [key]);
    
    if (existing.isNotEmpty) {
      return await db.update(
        'app_config',
        {
          'config_value': value,
          'updated_by': updatedBy,
          'updated_at': DateTime.now().toIso8601String(),
        },
        where: 'config_key = ?',
        whereArgs: [key],
      );
    } else {
      return await db.insert('app_config', {
        'config_key': key,
        'config_value': value,
        'description': description,
        'updated_by': updatedBy,
      });
    }
  }

  Future close() async {
    final db = await database;
    await db.close();
  }
}
