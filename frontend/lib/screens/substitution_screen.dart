import 'package:flutter/material.dart';
import '../services/api_service.dart';

class SubstitutionScreen extends StatefulWidget {
  final ApiService api;
  const SubstitutionScreen({super.key, required this.api});
  @override
  State<SubstitutionScreen> createState() => _SubstitutionScreenState();
}

class _SubstitutionScreenState extends State<SubstitutionScreen> {
  List<dynamic> substitutions = [];
  List<dynamic> availableFaculty = [];
  bool loading = true;
  String error = '';
  int selectedDay = 0;
  int selectedPeriod = 1;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try {
      substitutions = await widget.api.getSubstitutions();
      availableFaculty = await widget.api.getAvailableFaculty(selectedDay, selectedPeriod);
    } catch (e) { error = e.toString(); }
    setState(() => loading = false);
  }

  Future<void> _assignSubstitute(String facultyId) async {
    // Need timetable_entry_id - for demo, use first available
    try {
      await widget.api.createSubstitution({
        'timetable_entry_id': '00000000-0000-0000-0000-000000000000',
        'substitute_faculty_id': facultyId,
        'substitution_date': DateTime.now().toIso8601String(),
        'reason': 'Faculty unavailable',
      });
      _load();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    }
  }

  Color _statusColor(String s) {
    switch (s) {
      case 'Approved': return Colors.green;
      case 'Rejected': return Colors.red;
      case 'Completed': return Colors.blue;
      default: return Colors.orange;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Substitutions'), backgroundColor: const Color(0xFF1E3A5F), foregroundColor: Colors.white,
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _load)]),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : error.isNotEmpty
              ? Center(child: Text(error))
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Available Faculty', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Expanded(
                            child: DropdownButton<int>(
                              value: selectedDay,
                              isExpanded: true,
                              items: List.generate(6, (i) => DropdownMenuItem(value: i, child: Text(['Mon','Tue','Wed','Thu','Fri','Sat'][i]))),
                              onChanged: (v) { setState(() => selectedDay = v!); _load(); },
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: DropdownButton<int>(
                              value: selectedPeriod,
                              isExpanded: true,
                              items: List.generate(7, (i) => DropdownMenuItem(value: i + 1, child: Text('Period ${i + 1}'))),
                              onChanged: (v) { setState(() => selectedPeriod = v!); _load(); },
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      if (availableFaculty.isEmpty)
                        const Text('No available faculty', style: TextStyle(color: Colors.grey))
                      else
                        ...availableFaculty.map((f) => Card(
                              child: ListTile(
                                leading: const Icon(Icons.person, color: Color(0xFF1E3A5F)),
                                title: Text(f['name'] ?? ''),
                                subtitle: Text('${f['department'] ?? ''} | ${f['designation'] ?? ''}'),
                                trailing: ElevatedButton(
                                  onPressed: () => _assignSubstitute(f['id']),
                                  child: const Text('Assign'),
                                ),
                              ),
                            )),
                      const SizedBox(height: 16),
                      const Text('Substitution History', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 8),
                      if (substitutions.isEmpty)
                        const Text('No substitutions', style: TextStyle(color: Colors.grey))
                      else
                        ...substitutions.map((s) => Card(
                              child: ListTile(
                                leading: CircleAvatar(backgroundColor: _statusColor(s['status'] ?? ''), child: Text((s['status'] ?? 'P')[0], style: const TextStyle(color: Colors.white))),
                                title: Text('${s['original'] ?? ''} → ${s['substitute'] ?? ''}'),
                                subtitle: Text('Status: ${s['status']} | ${s['date'] ?? ''}'),
                              ),
                            )),
                    ],
                  ),
                ),
    );
  }
}

