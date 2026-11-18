import 'package:flutter/material.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const FacultyQApp());
}

class FacultyQApp extends StatelessWidget {
  const FacultyQApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FACULTY Q',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1E3A5F)),
      ),
      home: const LoginScreen(),
    );
  }
}