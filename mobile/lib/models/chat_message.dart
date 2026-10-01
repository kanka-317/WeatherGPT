import 'package:intl/intl.dart';

class ChatMessageModel {
  final String id;
  final String role; // 'user' | 'assistant'
  final String content;
  final DateTime timestamp;
  final List<String> toolsCalled;
  final Map<String, dynamic>? weatherData;
  final String? explainabilitySummary;
  final String? dataSource;
  final String? dataTimestamp;
  final String? userRole;

  ChatMessageModel({
    required this.id,
    required this.role,
    required this.content,
    required this.timestamp,
    this.toolsCalled = const [],
    this.weatherData,
    this.explainabilitySummary,
    this.dataSource,
    this.dataTimestamp,
    this.userRole,
  });

  factory ChatMessageModel.fromJson(Map<String, dynamic> json) {
    DateTime ts;
    try {
      ts = DateTime.tryParse(json['timestamp']?.toString() ?? '') ?? DateTime.now();
    } catch (_) {
      ts = DateTime.now();
    }

    return ChatMessageModel(
      id: json['id']?.toString() ?? DateTime.now().millisecondsSinceEpoch.toString(),
      role: json['role'] ?? 'user',
      content: json['content'] ?? '',
      timestamp: ts,
      toolsCalled: (json['tools_called'] as List?)?.map((e) => e.toString()).toList() ?? [],
      weatherData: json['weather_data'] as Map<String, dynamic>?,
      explainabilitySummary: json['explainability_summary'] as String?,
      dataSource: json['data_source'] as String?,
      dataTimestamp: json['data_timestamp'] as String?,
      userRole: json['user_role'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'role': role,
    'content': content,
    'timestamp': timestamp.toIso8601String(),
    'tools_called': toolsCalled,
    'weather_data': weatherData,
    'explainability_summary': explainabilitySummary,
    'data_source': dataSource,
    'data_timestamp': dataTimestamp,
    'user_role': userRole,
  };

  String get formattedTime {
    return DateFormat('hh:mm a').format(timestamp.toLocal());
  }
}
