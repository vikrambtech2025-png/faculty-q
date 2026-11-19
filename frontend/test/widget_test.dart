import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:faculty_q/main.dart';

void main() {
  testWidgets('App builds', (WidgetTester tester) async {
    await tester.pumpWidget(const FacultyQApp());
    expect(find.text('FACULTY Q'), findsOneWidget);
  });
}