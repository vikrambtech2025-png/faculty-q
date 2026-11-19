import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'notifications_screen.dart';
import 'timetable_screen.dart';
import 'assignments_screen.dart';

class DashboardScreen extends StatefulWidget {
  final ApiService api;
  final Map<String, dynamic> user;
  final String role;
  const DashboardScreen({super.key, required this.api, required this.user, required this.role});
  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic>? data;
  bool loading = true;
  String error = '';
  int _tab = 0;

  @override
  void initState() {
    super.initState();
    _load();
  }

  String get _role => widget.role;

  Future<void> _load() async {
    try {
      if (widget.role == 'admin') {
        data = await widget.api.getAdminDashboard();
      } else if (widget.role == 'faculty') {
        data = await widget.api.getFacultyDashboard();
      } else {
        data = await widget.api.getStudentDashboard();
      }
    } catch (e) {
      error = e.toString();
    }
    setState(() => loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('${widget.role[0].toUpperCase()}${widget.role.substring(1)} Dashboard'),
        backgroundColor: const Color(0xFF1E3A5F), foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => NotificationsScreen(api: widget.api))),
          ),
          IconButton(icon: const Icon(Icons.logout), onPressed: () => Navigator.pop(context)),
        ],
      ),
      body: _tab == 0
          ? (loading
              ? const Center(child: CircularProgressIndicator())
              : error.isNotEmpty
                  ? Center(child: Text(error, style: const TextStyle(color: Colors.red)))
                  : SingleChildScrollView(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: _buildCards(),
                      ),
                    ))
          : _tab == 1
              ? TimetableScreen(api: widget.api)
              : AssignmentsScreen(api: widget.api, role: widget.role),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _tab,
        onTap: (i) => setState(() => _tab = i),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.dashboard), label: 'Dashboard'),
          BottomNavigationBarItem(icon: Icon(Icons.calendar_today), label: 'Timetable'),
          BottomNavigationBarItem(icon: Icon(Icons.assignment), label: 'Assignments'),
        ],
      ),
    );
  }

  List<Widget> _buildCards() {
    if (data == null) return [];
    final d = data!;
    if (widget.role == 'admin') {
      return [
        _statCard('Total Faculty', '${d['total_faculty']}', Icons.people),
        _statCard('Total Students', '${d['total_students']}', Icons.school),
        _statCard('Total Users', '${d['total_users']}', Icons.person),
        _statCard('Active Timetables', '${d['active_timetables']}', Icons.calendar_today),
        _statCard('Total Assignments', '${d['total_assignments']}', Icons.assignment),
        _statCard('Pending Substitutions', '${d['pending_substitutions']}', Icons.swap_horiz),
      ];
    } else if (widget.role == 'faculty') {
      return [
        Text('Welcome, ${d['faculty_name']}', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
        const SizedBox(height: 12),
        Text('Today\'s Classes: ${d['today_count']}', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        ...((d['today_classes'] as List?) ?? []).map((c) => Card(
              child: ListTile(
                leading: const Icon(Icons.class_),
                title: Text('${c['subject']} (P${c['period']})'),
                subtitle: Text('${c['start']}-${c['end']} | ${c['class']} ${c['section']} | Room ${c['classroom']}'),
              ),
            )),
        const SizedBox(height: 12),
        _statCard('Active Assignments', '${d['active_assignments']}', Icons.assignment),
        _statCard('Pending Substitutions', '${d['pending_substitutions']}', Icons.swap_horiz),
        _statCard('Unread Notifications', '${d['unread_notifications']}', Icons.notifications),
      ];
    } else {
      return [
        Text('Welcome, ${d['student_name']}', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
        Text('Roll: ${d['roll_number']}', style: const TextStyle(color: Colors.grey)),
        const SizedBox(height: 12),
        Text('Today\'s Classes: ${d['today_count']}', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        ...((d['today_classes'] as List?) ?? []).map((c) => Card(
              child: ListTile(
                leading: const Icon(Icons.class_),
                title: Text('${c['subject']} (P${c['period']})'),
                subtitle: Text('${c['start']}-${c['end']} | Room ${c['classroom']}, Floor ${c['floor']}'),
              ),
            )),
        const SizedBox(height: 12),
        _statCard('Pending Assignments', '${d['pending_assignments']}', Icons.assignment),
        _statCard('Unread Notifications', '${d['unread_notifications']}', Icons.notifications),
      ];
    }
  }

  Widget _statCard(String label, String value, IconData icon) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(icon, color: const Color(0xFF1E3A5F)),
        title: Text(label),
        trailing: Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF1E3A5F))),
      ),
    );
  }
}