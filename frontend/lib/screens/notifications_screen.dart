import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../services/api_service.dart';

class NotificationsScreen extends StatefulWidget {
  final ApiService api;
  const NotificationsScreen({super.key, required this.api});
  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  List<dynamic> notifications = [];
  int unreadCount = 0;
  bool loading = true;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try {
      notifications = await widget.api.getNotifications();
      final uc = await widget.api.getUnreadCount();
      unreadCount = uc['count'] ?? 0;
    } catch (_) {}
    setState(() => loading = false);
  }

  Future<void> _markRead(String id) async {
    try {
      await widget.api.markNotificationRead(id);
      setState(() {
        final idx = notifications.indexWhere((n) => n['id'] == id);
        if (idx >= 0) notifications[idx]['is_read'] = true;
        if (unreadCount > 0) unreadCount--;
      });
    } catch (_) {}
  }

  Future<void> _markAllRead() async {
    try {
      await widget.api.markAllNotificationsRead();
      setState(() {
        for (var n in notifications) n['is_read'] = true;
        unreadCount = 0;
      });
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Notifications ($unreadCount unread)'),
        backgroundColor: const Color(0xFF1E3A5F), foregroundColor: Colors.white,
        actions: [
          IconButton(icon: const Icon(Icons.done_all), onPressed: _markAllRead, tooltip: 'Mark all read'),
          IconButton(icon: const Icon(Icons.refresh), onPressed: _load),
        ],
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : notifications.isEmpty
              ? const Center(child: Text('No notifications'))
              : ListView.builder(
                  itemCount: notifications.length,
                  itemBuilder: (ctx, i) {
                    final n = notifications[i];
                    final isRead = n['is_read'] == true;
                    return ListTile(
                      leading: Icon(isRead ? Icons.notifications_none : Icons.notifications_active,
                          color: isRead ? Colors.grey : const Color(0xFF1E3A5F)),
                      title: Text(n['title'] ?? '', style: TextStyle(fontWeight: isRead ? FontWeight.normal : FontWeight.bold)),
                      subtitle: Text(n['message'] ?? '', maxLines: 2, overflow: TextOverflow.ellipsis),
                      trailing: Text(n['created_at']?.toString().substring(0, 16) ?? '', style: const TextStyle(fontSize: 10, color: Colors.grey)),
                      onTap: () => _markRead(n['id']),
                    );
                  },
                ),
    );
  }
}

