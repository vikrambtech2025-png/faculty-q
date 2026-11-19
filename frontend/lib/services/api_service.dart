import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000';
  String? _token;

  Future<void> loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('access_token');
  }

  Future<void> saveToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', token);
  }

  Future<void> clearToken() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
  }

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_token != null) 'Authorization': 'Bearer $_token',
      };

  Future<Map<String, dynamic>> login(String email, String password) async {
    final res = await http.post(
      Uri.parse('$baseUrl/api/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      await saveToken(data['access_token']);
      return data;
    }
    throw Exception(jsonDecode(res.body)['detail'] ?? 'Login failed');
  }

  Future<Map<String, dynamic>> getMe() async {
    final res = await http.get(Uri.parse('$baseUrl/api/auth/me'), headers: _headers);
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('Failed to get user');
  }

  Future<Map<String, dynamic>> getAdminDashboard() async {
    final res = await http.get(Uri.parse('$baseUrl/api/dashboard/admin'), headers: _headers);
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('Failed');
  }

  Future<Map<String, dynamic>> getFacultyDashboard() async {
    final res = await http.get(Uri.parse('$baseUrl/api/dashboard/faculty'), headers: _headers);
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('Failed');
  }

  Future<Map<String, dynamic>> getStudentDashboard() async {
    final res = await http.get(Uri.parse('$baseUrl/api/dashboard/student'), headers: _headers);
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('Failed');
  }

  Future<List<dynamic>> getFacultyList() async {
    final res = await http.get(Uri.parse('$baseUrl/api/admin/faculty'), headers: _headers);
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('Failed');
  }

  Future<List<dynamic>> getStudentList() async {
    final res = await http.get(Uri.parse('$baseUrl/api/admin/students'), headers: _headers);
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('Failed');
  }

  Future<List<dynamic>> getTodayTimetable() async {
    final res = await http.get(Uri.parse('$baseUrl/api/timetables/today'), headers: _headers);
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('Failed');
  }

  Future<Map<String, dynamic>> getWeekTimetable() async {
    final res = await http.get(Uri.parse('$baseUrl/api/timetables/week'), headers: _headers);
    if (res.statusCode == 200) return jsonDecode(res.body) as Map<String, dynamic>;
    throw Exception('Failed');
  }

  Future<List<dynamic>> getNotifications() async {
    final res = await http.get(Uri.parse('$baseUrl/api/notifications'), headers: _headers);
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('Failed');
  }

  Future<Map<String, dynamic>> getUnreadCount() async {
    final res = await http.get(Uri.parse('$baseUrl/api/notifications/unread-count'), headers: _headers);
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('Failed');
  }

  Future<void> markNotificationRead(String id) async {
    final res = await http.put(Uri.parse('$baseUrl/api/notifications/$id/read'), headers: _headers);
    if (res.statusCode != 200) throw Exception('Failed');
  }

  Future<void> markAllNotificationsRead() async {
    final res = await http.put(Uri.parse('$baseUrl/api/notifications/read-all'), headers: _headers);
    if (res.statusCode != 200) throw Exception('Failed');
  }

  Future<List<dynamic>> getAssignments() async {
    final res = await http.get(Uri.parse('$baseUrl/api/assignments'), headers: _headers);
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('Failed');
  }

  Future<List<dynamic>> getStudentAssignments() async {
    final res = await http.get(Uri.parse('$baseUrl/api/assignments/student'), headers: _headers);
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('Failed');
  }

  Future<void> submitAssignment(String id) async {
    final res = await http.post(Uri.parse('$baseUrl/api/assignments/$id/submit'), headers: _headers);
    if (res.statusCode != 200) throw Exception('Failed');
  }

  Future<void> createAssignment(Map<String, dynamic> data) async {
    final res = await http.post(Uri.parse('$baseUrl/api/assignments'), headers: _headers, body: jsonEncode(data));
    if (res.statusCode != 200 && res.statusCode != 201) throw Exception('Failed: ${res.body}');
  }

  Future<Map<String, dynamic>> getNotificationPrefs() async {
    final res = await http.get(Uri.parse('$baseUrl/api/notifications/preferences'), headers: _headers);
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('Failed');
  }

  Future<void> updateNotificationPrefs({bool? emailEnabled, bool? inAppEnabled}) async {
    final params = <String, String>{};
    if (emailEnabled != null) params['email_enabled'] = emailEnabled.toString();
    if (inAppEnabled != null) params['in_app_enabled'] = inAppEnabled.toString();
    final uri = Uri.parse('$baseUrl/api/notifications/preferences').replace(queryParameters: params);
    final res = await http.put(uri, headers: _headers);
    if (res.statusCode != 200) throw Exception('Failed');
  }

  Future<Map<String, dynamic>> testEmail() async {
    final res = await http.post(Uri.parse('$baseUrl/api/notifications/test-email'), headers: _headers);
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('Failed: ${res.body}');
  }

  Future<List<dynamic>> getSubstitutions() async {
    final res = await http.get(Uri.parse('$baseUrl/api/substitutions'), headers: _headers);
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('Failed');
  }

  Future<List<dynamic>> getAvailableFaculty(int day, int period) async {
    final res = await http.get(Uri.parse('$baseUrl/api/substitutions/available-faculty?day=$day&period=$period'), headers: _headers);
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('Failed');
  }

  Future<void> createSubstitution(Map<String, dynamic> data) async {
    final res = await http.post(Uri.parse('$baseUrl/api/substitutions'), headers: _headers, body: jsonEncode(data));
    if (res.statusCode != 200 && res.statusCode != 201) throw Exception('Failed: ${res.body}');
  }
}