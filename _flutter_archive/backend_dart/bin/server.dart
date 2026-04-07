import 'dart:convert';
import 'dart:io';

import 'package:shelf/shelf.dart';
import 'package:shelf/shelf_io.dart' as io;
import 'package:shelf_router/shelf_router.dart';
import 'package:sqlite3/sqlite3.dart';

void main() async {
  // SQLite database initialization for app data.
  final db = sqlite3.open('guide_map.db');
  db.execute('''
    CREATE TABLE IF NOT EXISTS app_stats (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      users_count INTEGER NOT NULL DEFAULT 0
    );
  ''');
  db.execute('''
    CREATE TABLE IF NOT EXISTS locations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      building TEXT NOT NULL,
      room TEXT NOT NULL
    );
  ''');

  final check = db.select('SELECT COUNT(*) AS c FROM app_stats');
  if (check.first['c'] == 0) {
    db.execute('INSERT INTO app_stats (users_count) VALUES (120)');
  }

  final router = Router()
    // Health endpoint for quick server check.
    ..get('/health', (Request request) {
      return Response.ok(jsonEncode({'status': 'ok'}), headers: {
        HttpHeaders.contentTypeHeader: 'application/json',
      });
    })
    // Admin dashboard data endpoint.
    ..get('/dashboard', (Request request) {
      final rows = db.select('SELECT users_count FROM app_stats LIMIT 1');
      final usersCount = rows.isEmpty ? 0 : rows.first['users_count'] as int;
      return Response.ok(
        jsonEncode({'users_count': usersCount}),
        headers: {HttpHeaders.contentTypeHeader: 'application/json'},
      );
    })
    // List all building-room records.
    ..get('/locations', (Request request) {
      final rows = db.select('SELECT id, building, room FROM locations');
      final result = rows
          .map((row) => {
                'id': row['id'],
                'building': row['building'],
                'room': row['room'],
              })
          .toList();
      return Response.ok(
        jsonEncode(result),
        headers: {HttpHeaders.contentTypeHeader: 'application/json'},
      );
    })
    // Add or modify building-room information.
    ..post('/locations', (Request request) async {
      final body = await request.readAsString();
      final data = jsonDecode(body) as Map<String, dynamic>;
      final building = (data['building'] ?? '').toString().trim();
      final room = (data['room'] ?? '').toString().trim();

      if (building.isEmpty || room.isEmpty) {
        return Response(
          HttpStatus.badRequest,
          body: jsonEncode({'error': 'building and room are required'}),
          headers: {HttpHeaders.contentTypeHeader: 'application/json'},
        );
      }

      db.execute(
        'INSERT INTO locations (building, room) VALUES (?, ?)',
        [building, room],
      );
      return Response.ok(
        jsonEncode({'message': 'Location saved'}),
        headers: {HttpHeaders.contentTypeHeader: 'application/json'},
      );
    });

  // CORS middleware to allow app access during development.
  final handler = const Pipeline()
      .addMiddleware(logRequests())
      .addMiddleware(_cors())
      .addHandler(router.call);

  final server = await io.serve(handler, InternetAddress.anyIPv4, 8080);
  stdout.writeln('Dart backend running on http://${server.address.host}:${server.port}');
}

Middleware _cors() {
  return (innerHandler) {
    return (request) async {
      if (request.method == 'OPTIONS') {
        return Response.ok('', headers: _corsHeaders);
      }
      final response = await innerHandler(request);
      return response.change(headers: {
        ...response.headers,
        ..._corsHeaders,
      });
    };
  };
}

const _corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Origin, Content-Type',
};
