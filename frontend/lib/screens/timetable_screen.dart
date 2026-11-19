import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../services/api_service.dart';

class TimetableScreen extends StatefulWidget {
  final ApiService api;
  const TimetableScreen({super.key, required this.api});
  @override
  State<TimetableScreen> createState() => _TimetableScreenState();
}

class _TimetableScreenState extends State<TimetableScreen> {
  Map<String, dynamic> weekData = {};
  bool loading = true;
  String error = '';

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try {
      weekData = await widget.api.getWeekTimetable();
    } catch (e) { error = e.toString(); }
    setState(() => loading = false);
  }

  static const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Timetable'), backgroundColor: const Color(0xFF1E3A5F), foregroundColor: Colors.white,
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _load)]),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : error.isNotEmpty
              ? Center(child: Text(error))
              : SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: List.generate(6, (dayIdx) {
                      final entries = (weekData['$dayIdx'] as List?) ?? [];
                      return Container(
                        width: 160,
                        margin: const EdgeInsets.all(4),
                        child: Column(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              color: const Color(0xFF1E3A5F),
                              child: Text(dayNames[dayIdx], style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold), textAlign: TextAlign.center),
                            ),
                            ...entries.map((e) => Card(
                                  margin: const EdgeInsets.symmetric(vertical: 2),
                                  child: Padding(
                                    padding: const EdgeInsets.all(8),
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text('P${e['period']}: ${e['subject']}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                                        Text('${e['start']}-${e['end']}', style: const TextStyle(fontSize: 10, color: Colors.grey)),
                                        Text(e['faculty'] ?? '', style: const TextStyle(fontSize: 10)),
                                        if (e['classroom'] != null) Text('Room ${e['classroom']}', style: const TextStyle(fontSize: 10, color: Colors.blue)),
                                      ],
                                    ),
                                  ),
                                )),
                          ],
                        ),
                      );
                    }),
                  ),
                ),
    );
  }
}

