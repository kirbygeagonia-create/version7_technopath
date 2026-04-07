import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

/// Database Schema Documentation for guidemap.db
/// 
/// ============================================
/// TABLE: users
/// --------------------------------------------
/// id          INTEGER PRIMARY KEY AUTOINCREMENT
/// username    TEXT NOT NULL UNIQUE
/// password    TEXT NOT NULL
/// role        TEXT NOT NULL DEFAULT 'user'
/// created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
/// 
/// Default account: admin / admin (role: admin)
/// 
/// ============================================
/// TABLE: facilities
/// --------------------------------------------
/// id          INTEGER PRIMARY KEY AUTOINCREMENT
/// name        TEXT NOT NULL
/// description TEXT
/// created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
/// 
/// Default data: Building, RST Building, JST Building, MST Building,
///               Library, Registrar Office, Cafeteria
/// 
/// ============================================
/// TABLE: rooms
/// --------------------------------------------
/// id          INTEGER PRIMARY KEY AUTOINCREMENT
/// facility_id INTEGER (FK -> facilities.id)
/// name        TEXT NOT NULL
/// description TEXT
/// created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
/// 
/// Default data: CL1-CL6 (Computer Labs)
///               CR1-CR4 (Lecture Rooms)
///               Computer Lab 1-2
/// 
/// ============================================
/// TABLE: notifications
/// --------------------------------------------
/// id          INTEGER PRIMARY KEY AUTOINCREMENT
/// title       TEXT NOT NULL
/// message     TEXT NOT NULL
/// is_read     INTEGER DEFAULT 0
/// created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
/// 
/// ============================================
/// TABLE: ratings
/// --------------------------------------------
/// id          INTEGER PRIMARY KEY AUTOINCREMENT
/// user_id     INTEGER (FK -> users.id)
/// rating      INTEGER NOT NULL
/// comment     TEXT
/// created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
/// 
/// ============================================
/// TABLE: map_markers
/// --------------------------------------------
/// id          INTEGER PRIMARY KEY AUTOINCREMENT
/// name        TEXT NOT NULL
/// x_position  REAL NOT NULL
/// y_position  REAL NOT NULL
/// type        TEXT NOT NULL (facility/room)
/// created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
/// 
/// Query Examples:
/// - SELECT * FROM users WHERE role = 'admin'
/// - SELECT * FROM facilities WHERE name LIKE '%Building%'
/// - SELECT r.*, f.name as facility_name FROM rooms r JOIN facilities f ON r.facility_id = f.id
/// - SELECT * FROM map_markers WHERE type = 'facility'

class DatabaseHelper {
  static final DatabaseHelper instance = DatabaseHelper._init();
  static Database? _database;

  DatabaseHelper._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB('guidemap.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);

    return await openDatabase(path, version: 2, onCreate: _createDB, onUpgrade: _onUpgrade);
  }

  Future _onUpgrade(Database db, int oldVersion, int newVersion) async {
    if (oldVersion < 2) {
      // Check if admin user exists, if not create it
      final result = await db.query(
        'users',
        where: 'username = ?',
        whereArgs: ['admin'],
      );
      if (result.isEmpty) {
        await db.insert('users', {
          'username': 'admin',
          'password': 'admin',
          'role': 'admin',
        });
      }
    }
  }

  Future _createDB(Database db, int version) async {
    // Users table for login
    await db.execute('''
      CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    ''');

    // Facilities/Buildings table
    await db.execute('''
      CREATE TABLE facilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    ''');

    // Rooms table
    await db.execute('''
      CREATE TABLE rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        facility_id INTEGER,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (facility_id) REFERENCES facilities (id) ON DELETE CASCADE
      )
    ''');

    // Notifications table
    await db.execute('''
      CREATE TABLE notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    ''');

    // Ratings table
    await db.execute('''
      CREATE TABLE ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        rating INTEGER NOT NULL,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
      )
    ''');

    // Map markers/locations table
    await db.execute('''
      CREATE TABLE map_markers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        x_position REAL NOT NULL,
        y_position REAL NOT NULL,
        type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    ''');

    // App usage tracking table
    await db.execute('''
      CREATE TABLE app_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        session_date TEXT NOT NULL,
        session_duration INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
      )
    ''');

    // Insert default admin user
    await db.insert('users', {
      'username': 'admin',
      'password': 'admin',
      'role': 'admin',
    });

    // Insert default facilities
    await db.insert('facilities', {'name': 'Building', 'description': 'Default building'});
    await db.insert('facilities', {'name': 'RST Building', 'description': 'Research Science and Technology'});
    await db.insert('facilities', {'name': 'JST Building', 'description': 'Junior Science and Technology'});
    await db.insert('facilities', {'name': 'MST Building', 'description': 'Main Science and Technology'});
    await db.insert('facilities', {'name': 'Library', 'description': 'School Library and Resource Center'});
    await db.insert('facilities', {'name': 'Registrar Office', 'description': 'Student Records and Enrollment'});
    await db.insert('facilities', {'name': 'Cafeteria', 'description': 'School Cafeteria and Dining Area'});

    // Insert default rooms - Building (facility_id: 1)
    for (var i = 1; i <= 4; i++) {
      await db.insert('rooms', {'name': 'CL$i', 'facility_id': 1, 'description': 'Computer Lab $i'});
    }
    for (var i = 1; i <= 4; i++) {
      await db.insert('rooms', {'name': 'CR$i', 'facility_id': 1, 'description': 'Lecture Room $i'});
    }
    await db.insert('rooms', {'name': 'CL5', 'facility_id': 1, 'description': 'Computer Lab 5 (2nd Floor)'});
    await db.insert('rooms', {'name': 'CL6', 'facility_id': 1, 'description': 'Computer Lab 6 (2nd Floor)'});
    await db.insert('rooms', {'name': 'Computer Lab 1', 'facility_id': 1, 'description': 'Main Computer Lab'});
    await db.insert('rooms', {'name': 'Computer Lab 2', 'facility_id': 1, 'description': 'Secondary Computer Lab'});
  }

  // User CRUD
  Future<Map<String, dynamic>?> getUser(String username, String password) async {
    final db = await database;
    final result = await db.query(
      'users',
      where: 'username = ? AND password = ?',
      whereArgs: [username, password],
    );
    return result.isNotEmpty ? result.first : null;
  }

  Future<List<Map<String, dynamic>>> getAllUsers() async {
    final db = await database;
    return await db.query('users');
  }

  Future<int> insertUser(Map<String, dynamic> user) async {
    final db = await database;
    return await db.insert('users', user);
  }

  Future<int> updateUser(Map<String, dynamic> user) async {
    final db = await database;
    return await db.update('users', user, where: 'id = ?', whereArgs: [user['id']]);
  }

  Future<int> deleteUser(int id) async {
    final db = await database;
    return await db.delete('users', where: 'id = ?', whereArgs: [id]);
  }

  // Facility CRUD
  Future<List<Map<String, dynamic>>> getAllFacilities() async {
    final db = await database;
    return await db.query('facilities', orderBy: 'name');
  }

  Future<int> insertFacility(Map<String, dynamic> facility) async {
    final db = await database;
    return await db.insert('facilities', facility);
  }

  Future<int> updateFacility(Map<String, dynamic> facility) async {
    final db = await database;
    return await db.update('facilities', facility, where: 'id = ?', whereArgs: [facility['id']]);
  }

  Future<int> deleteFacility(int id) async {
    final db = await database;
    return await db.delete('facilities', where: 'id = ?', whereArgs: [id]);
  }

  // Room CRUD
  Future<List<Map<String, dynamic>>> getAllRooms() async {
    final db = await database;
    return await db.query('rooms', orderBy: 'name');
  }

  Future<List<Map<String, dynamic>>> getRoomsByFacility(int facilityId) async {
    final db = await database;
    return await db.query('rooms', where: 'facility_id = ?', whereArgs: [facilityId]);
  }

  Future<int> insertRoom(Map<String, dynamic> room) async {
    final db = await database;
    return await db.insert('rooms', room);
  }

  Future<int> updateRoom(Map<String, dynamic> room) async {
    final db = await database;
    return await db.update('rooms', room, where: 'id = ?', whereArgs: [room['id']]);
  }

  Future<int> deleteRoom(int id) async {
    final db = await database;
    return await db.delete('rooms', where: 'id = ?', whereArgs: [id]);
  }

  // Notification CRUD
  Future<List<Map<String, dynamic>>> getAllNotifications() async {
    final db = await database;
    return await db.query('notifications', orderBy: 'created_at DESC');
  }

  Future<int> getUnreadNotificationCount() async {
    final db = await database;
    final result = await db.rawQuery('SELECT COUNT(*) as count FROM notifications WHERE is_read = 0');
    return result.first['count'] as int? ?? 0;
  }

  Future<int> insertNotification(Map<String, dynamic> notification) async {
    final db = await database;
    return await db.insert('notifications', notification);
  }

  Future<int> markNotificationAsRead(int id) async {
    final db = await database;
    return await db.update('notifications', {'is_read': 1}, where: 'id = ?', whereArgs: [id]);
  }

  Future<int> deleteNotification(int id) async {
    final db = await database;
    return await db.delete('notifications', where: 'id = ?', whereArgs: [id]);
  }

  // Rating CRUD
  Future<List<Map<String, dynamic>>> getAllRatings() async {
    final db = await database;
    return await db.query('ratings', orderBy: 'created_at DESC');
  }

  Future<double> getAverageRating() async {
    final db = await database;
    final result = await db.rawQuery('SELECT AVG(rating) as avg FROM ratings');
    return result.first['avg'] as double? ?? 0.0;
  }

  Future<int> insertRating(Map<String, dynamic> rating) async {
    final db = await database;
    return await db.insert('ratings', rating);
  }

  Future<int> deleteRating(int id) async {
    final db = await database;
    return await db.delete('ratings', where: 'id = ?', whereArgs: [id]);
  }

  // Map Markers CRUD
  Future<List<Map<String, dynamic>>> getAllMapMarkers() async {
    final db = await database;
    return await db.query('map_markers');
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

  // App Usage CRUD
  Future<int> insertAppUsage(Map<String, dynamic> usage) async {
    final db = await database;
    return await db.insert('app_usage', usage);
  }

  Future<List<Map<String, dynamic>>> getWeeklyAppUsage() async {
    final db = await database;
    final result = await db.rawQuery('''
      SELECT session_date, COUNT(DISTINCT user_id) as user_count, SUM(session_duration) as total_duration
      FROM app_usage
      WHERE session_date >= date('now', '-7 days')
      GROUP BY session_date
      ORDER BY session_date DESC
    ''');
    return result;
  }

  Future<int> getTotalActiveUsers() async {
    final db = await database;
    final result = await db.rawQuery('SELECT COUNT(DISTINCT user_id) as count FROM app_usage WHERE session_date >= date(\'now\', \'-7 days\')');
    return result.first['count'] as int? ?? 0;
  }

  Future close() async {
    final db = await database;
    await db.close();
  }
}
