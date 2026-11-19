import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'dashboard_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _api = ApiService();
  final _emailCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  bool _loading = false;
  String _error = '';

  Future<void> _login() async {
    setState(() { _loading = true; _error = ''; });
    try {
      final data = await _api.login(_emailCtrl.text.trim(), _passCtrl.text);
      final user = data['user'];
      final roles = List<String>.from(user['roles'] ?? []);
      if (!mounted) return;
      final role = roles.contains('admin') ? 'admin' : (roles.contains('faculty') ? 'faculty' : 'student');
      Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => DashboardScreen(api: _api, user: user, role: role)));
    } catch (e) {
      setState(() => _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 400),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.school, size: 64, color: Color(0xFF1E3A5F)),
                const SizedBox(height: 16),
                const Text('FACULTY Q', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Color(0xFF1E3A5F))),
                const Text('Smart Faculty Scheduling & Reminder System', style: TextStyle(color: Colors.grey, fontSize: 12)),
                const SizedBox(height: 32),
                TextField(controller: _emailCtrl, decoration: const InputDecoration(labelText: 'Email', border: OutlineInputBorder()), keyboardType: TextInputType.emailAddress),
                const SizedBox(height: 12),
                TextField(controller: _passCtrl, decoration: const InputDecoration(labelText: 'Password', border: OutlineInputBorder()), obscureText: true),
                const SizedBox(height: 8),
                if (_error.isNotEmpty) Text(_error, style: const TextStyle(color: Colors.red)),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF1E3A5F), foregroundColor: Colors.white, padding: const EdgeInsets.symmetric(vertical: 14)),
                    onPressed: _loading ? null : _login,
                    child: Text(_loading ? 'Signing in...' : 'Login'),
                  ),
                ),
                const SizedBox(height: 16),
                const Text('Demo credentials:', style: TextStyle(fontSize: 11, color: Colors.grey)),
                const Text('admin@facultyq.com / admin123', style: TextStyle(fontSize: 11, color: Colors.grey)),
                const Text('faculty1@facultyq.com / faculty123', style: TextStyle(fontSize: 11, color: Colors.grey)),
                const Text('student1@facultyq.com / student123', style: TextStyle(fontSize: 11, color: Colors.grey)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

