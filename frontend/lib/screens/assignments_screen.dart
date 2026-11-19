import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../services/api_service.dart';

class AssignmentsScreen extends StatefulWidget {
  final ApiService api;
  final String role;
  const AssignmentsScreen({super.key, required this.api, required this.role});
  @override
  State<AssignmentsScreen> createState() => _AssignmentsScreenState();
}

class _AssignmentsScreenState extends State<AssignmentsScreen> {
  List<dynamic> assignments = [];
  bool loading = true;
  String error = '';

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try {
      if (widget.role == 'student') {
        assignments = await widget.api.getStudentAssignments();
      } else {
        assignments = await widget.api.getAssignments();
      }
    } catch (e) { error = e.toString(); }
    setState(() => loading = false);
  }

  Color _statusColor(String s) {
    switch (s) {
      case 'Submitted': return Colors.green;
      case 'Overdue': return Colors.red;
      case 'Completed': return Colors.blue;
      default: return Colors.orange;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Assignments'), backgroundColor: const Color(0xFF1E3A5F), foregroundColor: Colors.white,
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _load)]),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : error.isNotEmpty
              ? Center(child: Text(error))
              : assignments.isEmpty
                  ? const Center(child: Text('No assignments'))
                  : ListView.builder(
                      itemCount: assignments.length,
                      itemBuilder: (ctx, i) {
                        final a = assignments[i];
                        final status = a['status'] ?? 'Pending';
                        return Card(
                          margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          child: ListTile(
                            leading: CircleAvatar(backgroundColor: _statusColor(status), child: Text(status[0], style: const TextStyle(color: Colors.white))),
                            title: Text(a['title'] ?? ''),
                            subtitle: Text('${a['subject'] ?? ''} | Due: ${a['deadline']?.toString().substring(0, 16) ?? ''}'),
                            trailing: widget.role == 'student'
                                ? (status == 'Pending' || status == 'Overdue'
                                    ? ElevatedButton(
                                        onPressed: () async {
                                          try {
                                            await widget.api.submitAssignment(a['id']);
                                            _load();
                                          } catch (e) { ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString()))); }
                                        },
                                        child: const Text('Submit'),
                                      )
                                    : Text(status, style: TextStyle(color: _statusColor(status), fontWeight: FontWeight.bold)))
                                : Text(status, style: TextStyle(color: _statusColor(status))),
                          ),
                        );
                      },
                    ),
      floatingActionButton: (widget.role == 'faculty' || widget.role == 'admin')
          ? FloatingActionButton(
              backgroundColor: const Color(0xFF1E3A5F),
              onPressed: () => _showCreateDialog(context),
              child: const Icon(Icons.add, color: Colors.white),
            )
          : null,
    );
  }

  void _showCreateDialog(BuildContext context) {
    final titleCtrl = TextEditingController();
    final descCtrl = TextEditingController();
    final deadlineCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Create Assignment'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(controller: titleCtrl, decoration: const InputDecoration(labelText: 'Title', border: OutlineInputBorder())),
              const SizedBox(height: 8),
              TextField(controller: descCtrl, decoration: const InputDecoration(labelText: 'Description', border: OutlineInputBorder()), maxLines: 3),
              const SizedBox(height: 8),
              TextField(controller: deadlineCtrl, decoration: const InputDecoration(labelText: 'Deadline (YYYY-MM-DD HH:MM)', border: OutlineInputBorder())),
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              try {
                // Need subject_id and class_id - fetch from API or hardcode for demo
                await widget.api.createAssignment({
                  'title': titleCtrl.text,
                  'description': descCtrl.text,
                  'subject_id': '00000000-0000-0000-0000-000000000000',
                  'class_id': '00000000-0000-0000-0000-000000000000',
                  'deadline': deadlineCtrl.text,
                });
                Navigator.pop(context);
                _load();
              } catch (e) {
                ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
              }
            },
            child: const Text('Create'),
          ),
        ],
      ),
    );
  }
}

