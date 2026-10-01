import 'package:flutter/material.dart';

class AppConstants {
  // Production Render Backend URL (reused exactly as requested)
  static const String defaultBackendUrl = 'https://weathergpt-backend-g6ds.onrender.com';
  
  // WebSocket live alert feed URL
  static const String defaultWsUrl = 'wss://weathergpt-backend-g6ds.onrender.com/ws/alerts';

  // Fallback / Initial coordinates (Kolkata, West Bengal)
  static const String defaultLocationName = 'Kolkata';
  static const String defaultLocationState = 'West Bengal';
  static const double defaultLat = 22.5726;
  static const double defaultLon = 88.3639;

  // Supported Languages matching Web Client
  static const List<Map<String, String>> supportedLanguages = [
    {'code': 'en', 'label': 'English', 'native': 'English'},
    {'code': 'bn', 'label': 'Bengali', 'native': 'বাংলা'},
    {'code': 'hi', 'label': 'Hindi', 'native': 'हिन्दी'},
  ];

  // User Personas matching Web JWT Auth
  static const List<Map<String, String>> userRoles = [
    {
      'id': 'citizen',
      'title': 'Citizen',
      'desc': 'General daily forecasts & commute advisories',
      'icon': 'user',
    },
    {
      'id': 'farmer',
      'title': 'Farmer / Krishi',
      'desc': 'Agro-weather, irrigation timing & crop protection',
      'icon': 'sprout',
    },
    {
      'id': 'fisherman',
      'title': 'Fisherman / Coastal',
      'desc': 'Sea surge, squally wind & safe return windows',
      'icon': 'anchor',
    },
    {
      'id': 'disaster_manager',
      'title': 'Disaster Manager',
      'desc': 'NDRF/SDRF war room, live alerts & spatial radius filters',
      'icon': 'shield',
    },
  ];
}

class AppColors {
  static const Color background = Color(0xFF090E1A);
  static const Color surfaceCard = Color(0xFF131B2E);
  static const Color surfaceElevated = Color(0xFF1B2640);
  static const Color surfaceBorder = Color(0xFF233252);
  static const Color primaryCyan = Color(0xFF06B6D4);
  static const Color accentEmerald = Color(0xFF10B981);
  static const Color warningAmber = Color(0xFFF59E0B);
  static const Color dangerRed = Color(0xFFEF4444);
  
  static const Color textPrimary = Color(0xFFF8FAFC);
  static const Color textSecondary = Color(0xFF94A3B8);
  static const Color textMuted = Color(0xFF64748B);

  // Severity to Color matching RiskMap on Web
  static Color severityColor(String severity) {
    final s = severity.toLowerCase();
    if (s.contains('extreme') || s.contains('emergency') || s.contains('red')) {
      return dangerRed;
    } else if (s.contains('severe') || s.contains('warning') || s.contains('orange')) {
      return const Color(0xFFF97316); // Bright Orange
    } else if (s.contains('moderate') || s.contains('watch') || s.contains('yellow')) {
      return warningAmber;
    }
    return accentEmerald; // Green / Low / Advisory
  }
}
