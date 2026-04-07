import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

/// Database Schema Documentation for chatbot.db
/// 
/// ============================================
/// TABLE: chat_history
/// --------------------------------------------
/// id          INTEGER PRIMARY KEY AUTOINCREMENT
/// message     TEXT NOT NULL
/// reply       TEXT NOT NULL
/// timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
/// 
/// Query Examples:
/// - SELECT * FROM chat_history ORDER BY timestamp DESC
/// - SELECT * FROM chat_history WHERE timestamp >= date('now', '-7 days')
/// - DELETE FROM chat_history WHERE timestamp < date('now', '-30 days')

class ChatbotDatabaseHelper {
  static final ChatbotDatabaseHelper instance = ChatbotDatabaseHelper._init();
  static Database? _database;

  ChatbotDatabaseHelper._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB('chatbot.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);

    return await openDatabase(path, version: 1, onCreate: _createDB);
  }

  Future _createDB(Database db, int version) async {
    // Chat history table to store conversations
    await db.execute('''
      CREATE TABLE chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT NOT NULL,
        reply TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    ''');
  }

  // Chat History CRUD
  Future<int> insertChatHistory(Map<String, dynamic> chat) async {
    final db = await database;
    return await db.insert('chat_history', chat);
  }

  Future<List<Map<String, dynamic>>> getAllChatHistory() async {
    final db = await database;
    return await db.query('chat_history', orderBy: 'timestamp DESC');
  }

  Future<List<Map<String, dynamic>>> getRecentChatHistory(int limit) async {
    final db = await database;
    return await db.query(
      'chat_history',
      orderBy: 'timestamp DESC',
      limit: limit,
    );
  }

  Future<int> deleteChatHistory(int id) async {
    final db = await database;
    return await db.delete('chat_history', where: 'id = ?', whereArgs: [id]);
  }

  Future<int> clearAllChatHistory() async {
    final db = await database;
    return await db.delete('chat_history');
  }

  Future close() async {
    final db = await database;
    await db.close();
  }
}
