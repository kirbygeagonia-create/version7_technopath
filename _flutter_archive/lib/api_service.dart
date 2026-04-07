import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // Change this to your backend URL
  // For Android emulator: http://10.0.2.2:3000/api
  // For iOS simulator: http://localhost:3000/api
  // For physical device: http://YOUR_COMPUTER_IP:3000/api
  static const String baseUrl = 'http://10.0.2.2:3000/api';
  
  static final Map<String, String> headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  // ========== DASHBOARD ==========
  static Future<Map<String, dynamic>> getDashboardStats() async {
    final response = await http.get(
      Uri.parse('$baseUrl/dashboard/stats'),
      headers: headers,
    );
    return _handleResponse(response);
  }

  // ========== USERS ==========
  static Future<List<Map<String, dynamic>>> getAllUsers() async {
    final response = await http.get(
      Uri.parse('$baseUrl/users'),
      headers: headers,
    );
    final data = _handleResponse(response);
    return List<Map<String, dynamic>>.from(data['data'] ?? []);
  }

  static Future<Map<String, dynamic>> getUser(int id) async {
    final response = await http.get(
      Uri.parse('$baseUrl/users/$id'),
      headers: headers,
    );
    final data = _handleResponse(response);
    return data['data'] ?? {};
  }

  static Future<Map<String, dynamic>?> loginUser(String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/users/login'),
      headers: headers,
      body: jsonEncode({'username': username, 'password': password}),
    );
    final data = _handleResponse(response);
    return data['data'];
  }

  static Future<Map<String, dynamic>> createUser(Map<String, dynamic> user) async {
    final response = await http.post(
      Uri.parse('$baseUrl/users'),
      headers: headers,
      body: jsonEncode(user),
    );
    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> updateUser(int id, Map<String, dynamic> user) async {
    final response = await http.put(
      Uri.parse('$baseUrl/users/$id'),
      headers: headers,
      body: jsonEncode(user),
    );
    return _handleResponse(response);
  }

  static Future<void> deleteUser(int id) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/users/$id'),
      headers: headers,
    );
    _handleResponse(response);
  }

  // ========== FACILITIES ==========
  static Future<List<Map<String, dynamic>>> getAllFacilities() async {
    final response = await http.get(
      Uri.parse('$baseUrl/facilities'),
      headers: headers,
    );
    final data = _handleResponse(response);
    return List<Map<String, dynamic>>.from(data['data'] ?? []);
  }

  static Future<Map<String, dynamic>> getFacility(int id) async {
    final response = await http.get(
      Uri.parse('$baseUrl/facilities/$id'),
      headers: headers,
    );
    final data = _handleResponse(response);
    return data['data'] ?? {};
  }

  static Future<Map<String, dynamic>> createFacility(Map<String, dynamic> facility) async {
    final response = await http.post(
      Uri.parse('$baseUrl/facilities'),
      headers: headers,
      body: jsonEncode(facility),
    );
    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> updateFacility(int id, Map<String, dynamic> facility) async {
    final response = await http.put(
      Uri.parse('$baseUrl/facilities/$id'),
      headers: headers,
      body: jsonEncode(facility),
    );
    return _handleResponse(response);
  }

  static Future<void> deleteFacility(int id) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/facilities/$id'),
      headers: headers,
    );
    _handleResponse(response);
  }

  // ========== ROOMS ==========
  static Future<List<Map<String, dynamic>>> getAllRooms() async {
    final response = await http.get(
      Uri.parse('$baseUrl/rooms'),
      headers: headers,
    );
    final data = _handleResponse(response);
    return List<Map<String, dynamic>>.from(data['data'] ?? []);
  }

  static Future<List<Map<String, dynamic>>> getRoomsByFacility(int facilityId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/facilities/$facilityId/rooms'),
      headers: headers,
    );
    final data = _handleResponse(response);
    return List<Map<String, dynamic>>.from(data['data'] ?? []);
  }

  static Future<Map<String, dynamic>> getRoom(int id) async {
    final response = await http.get(
      Uri.parse('$baseUrl/rooms/$id'),
      headers: headers,
    );
    final data = _handleResponse(response);
    return data['data'] ?? {};
  }

  static Future<Map<String, dynamic>> createRoom(Map<String, dynamic> room) async {
    final response = await http.post(
      Uri.parse('$baseUrl/rooms'),
      headers: headers,
      body: jsonEncode(room),
    );
    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> updateRoom(int id, Map<String, dynamic> room) async {
    final response = await http.put(
      Uri.parse('$baseUrl/rooms/$id'),
      headers: headers,
      body: jsonEncode(room),
    );
    return _handleResponse(response);
  }

  static Future<void> deleteRoom(int id) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/rooms/$id'),
      headers: headers,
    );
    _handleResponse(response);
  }

  // ========== MAP MARKERS ==========
  static Future<List<Map<String, dynamic>>> getAllMapMarkers() async {
    final response = await http.get(
      Uri.parse('$baseUrl/map-markers'),
      headers: headers,
    );
    final data = _handleResponse(response);
    return List<Map<String, dynamic>>.from(data['data'] ?? []);
  }

  static Future<Map<String, dynamic>> getMapMarker(int id) async {
    final response = await http.get(
      Uri.parse('$baseUrl/map-markers/$id'),
      headers: headers,
    );
    final data = _handleResponse(response);
    return data['data'] ?? {};
  }

  static Future<Map<String, dynamic>> createMapMarker(Map<String, dynamic> marker) async {
    final response = await http.post(
      Uri.parse('$baseUrl/map-markers'),
      headers: headers,
      body: jsonEncode(marker),
    );
    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> updateMapMarker(int id, Map<String, dynamic> marker) async {
    final response = await http.put(
      Uri.parse('$baseUrl/map-markers/$id'),
      headers: headers,
      body: jsonEncode(marker),
    );
    return _handleResponse(response);
  }

  static Future<void> deleteMapMarker(int id) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/map-markers/$id'),
      headers: headers,
    );
    _handleResponse(response);
  }

  // ========== RATINGS ==========
  static Future<List<Map<String, dynamic>>> getAllRatings() async {
    final response = await http.get(
      Uri.parse('$baseUrl/ratings'),
      headers: headers,
    );
    final data = _handleResponse(response);
    return List<Map<String, dynamic>>.from(data['data'] ?? []);
  }

  static Future<double> getAverageRating() async {
    final response = await http.get(
      Uri.parse('$baseUrl/ratings/average'),
      headers: headers,
    );
    final data = _handleResponse(response);
    return (data['data']?['average'] ?? 0).toDouble();
  }

  static Future<Map<String, dynamic>> createRating(Map<String, dynamic> rating) async {
    final response = await http.post(
      Uri.parse('$baseUrl/ratings'),
      headers: headers,
      body: jsonEncode(rating),
    );
    return _handleResponse(response);
  }

  static Future<void> deleteRating(int id) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/ratings/$id'),
      headers: headers,
    );
    _handleResponse(response);
  }

  // ========== NOTIFICATIONS ==========
  static Future<List<Map<String, dynamic>>> getAllNotifications() async {
    final response = await http.get(
      Uri.parse('$baseUrl/notifications'),
      headers: headers,
    );
    final data = _handleResponse(response);
    return List<Map<String, dynamic>>.from(data['data'] ?? []);
  }

  static Future<int> getUnreadNotificationCount() async {
    final response = await http.get(
      Uri.parse('$baseUrl/notifications/unread/count'),
      headers: headers,
    );
    final data = _handleResponse(response);
    return data['data']?['count'] ?? 0;
  }

  static Future<Map<String, dynamic>> createNotification(Map<String, dynamic> notification) async {
    final response = await http.post(
      Uri.parse('$baseUrl/notifications'),
      headers: headers,
      body: jsonEncode(notification),
    );
    return _handleResponse(response);
  }

  static Future<void> markNotificationAsRead(int id) async {
    final response = await http.put(
      Uri.parse('$baseUrl/notifications/$id/read'),
      headers: headers,
    );
    _handleResponse(response);
  }

  static Future<void> deleteNotification(int id) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/notifications/$id'),
      headers: headers,
    );
    _handleResponse(response);
  }

  // ========== CHAT HISTORY ==========
  static Future<List<Map<String, dynamic>>> getChatHistory({int limit = 50}) async {
    final response = await http.get(
      Uri.parse('$baseUrl/chat-history?limit=$limit'),
      headers: headers,
    );
    final data = _handleResponse(response);
    return List<Map<String, dynamic>>.from(data['data'] ?? []);
  }

  static Future<Map<String, dynamic>> addChatHistory(Map<String, dynamic> chat) async {
    final response = await http.post(
      Uri.parse('$baseUrl/chat-history'),
      headers: headers,
      body: jsonEncode(chat),
    );
    return _handleResponse(response);
  }

  static Future<void> clearChatHistory() async {
    final response = await http.delete(
      Uri.parse('$baseUrl/chat-history'),
      headers: headers,
    );
    _handleResponse(response);
  }

  // ========== APP USAGE ==========
  static Future<List<Map<String, dynamic>>> getWeeklyAppUsage() async {
    final response = await http.get(
      Uri.parse('$baseUrl/app-usage/weekly'),
      headers: headers,
    );
    final data = _handleResponse(response);
    return List<Map<String, dynamic>>.from(data['data'] ?? []);
  }

  static Future<int> getTotalActiveUsers() async {
    final response = await http.get(
      Uri.parse('$baseUrl/app-usage/active-users'),
      headers: headers,
    );
    final data = _handleResponse(response);
    return data['data']?['count'] ?? 0;
  }

  static Future<Map<String, dynamic>> recordAppUsage(Map<String, dynamic> usage) async {
    final response = await http.post(
      Uri.parse('$baseUrl/app-usage'),
      headers: headers,
      body: jsonEncode(usage),
    );
    return _handleResponse(response);
  }

  // Helper method to handle HTTP responses
  static Map<String, dynamic> _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return jsonDecode(response.body);
    } else {
      throw Exception('API Error: ${response.statusCode} - ${response.body}');
    }
  }

  // Health check
  static Future<bool> checkHealth() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
        headers: headers,
      ).timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}
