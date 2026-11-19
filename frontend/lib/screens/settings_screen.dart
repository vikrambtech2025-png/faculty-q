import 'package:flutter/material.dart';
import '../services/api_service.dart';

class SettingsScreen extends StatefulWidget {
  final ApiService api;
  const SettingsScreen({super.key, required this.api});
  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool emailEnabled = true;
  bool inAppEnabled = true;
  int reminderMinutes = 5;
  String testResult = '';
  bool testing = false;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try {
      final prefs = await widget.api.getNotificationPrefs();
      setState(() {
        emailEnabled = prefs['email_enabled'] ?? true;
        inAppEnabled = prefs['in_app_enabled'] ?? true;
        reminderMinutes = prefs['class_reminder_minutes'] ?? 5;
      });
    } catch (_) {}
  }

  Future<void> _save() async {
    try {
      await widget.api.updateNotificationPrefs(emailEnabled: emailEnabled, inAppEnabled: inAppEnabled);
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Preferences saved')));
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    }
  }

  Future<void> _testEmail() async {
    setState(() { testing = true; testResult = ''; });
    try {
      final res = await widget.api.testEmail();
      setState(() => testResult = res['message'] ?? res['status'] ?? 'Done');
    } catch (e) {
      setState(() => testResult = e.toString());
    } finally {
      setState(() => testing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings'), backgroundColor: const Color(0xFF1E3A5F), foregroundColor: Colors.white),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Notification Preferences', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          SwitchListTile(title: const Text('Email notifications'), value: emailEnabled, onChanged: (v) => setState(() => emailEnabled = v)),
          SwitchListTile(title: const Text('In-app notifications'), value: inAppEnabled, onChanged: (v) => setState(() => inAppEnabled = v)),
          ListTile(title: const Text('Class reminder (minutes before)'), trailing: DropdownButton<int>(
            value: reminderMinutes,
            items: [1, 3, 5, 10, 15].map((m) => DropdownMenuItem(value: m, child: Text('$m min'))).toList(),
            onChanged: (v) => setState(() => reminderMinutes = v!),
          )),
          const SizedBox(height: 8),
          ElevatedButton(onPressed: _save, child: const Text('Save Preferences')),
          const Divider(height: 32),
          const Text('Email Configuration', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          const Text('Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD environment variables on the backend. Then test:', style: TextStyle(color: Colors.grey, fontSize: 12)),
          const SizedBox(height: 8),
          ElevatedButton(
            onPressed: testing ? null : _testEmail,
            child: Text(testing ? 'Sending...' : 'Send Test Email'),
          ),
          if (testResult.isNotEmpty) Padding(padding: const EdgeInsets.only(top: 8), child: Text(testResult, style: const TextStyle(color: Colors.blue))),
          const Divider(height: 32),
          const Text('SMTP Setup (backend .env)', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
          const SizedBox(height: 4),
          const Text('SMTP_HOST=smtp.gmail.com\nSMTP_PORT=587\nSMTP_USER=your@gmail.com\nSMTP_PASSWORD=your-app-password', style: TextStyle(fontFamily: 'monospace', fontSize: 12, color: Colors.grey)),
        ],
      ),
    );
  }
}

