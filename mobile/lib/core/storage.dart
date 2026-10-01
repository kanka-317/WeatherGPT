import 'dart:convert';
import 'dart:math';
import 'package:shared_preferences/shared_preferences.dart';

class LocalStorageService {
  static SharedPreferences? _prefs;

  static Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  // Session ID matching Web's getOrCreateSessionId()
  static String getSessionId() {
    final existing = _prefs?.getString('weathergpt_session_id');
    if (existing != null && existing.isNotEmpty) {
      return existing;
    }
    final randId = 'session-${Random().nextInt(999999).toString().padLeft(6, '0')}';
    _prefs?.setString('weathergpt_session_id', randId);
    return randId;
  }

  // Selected Language code (en, bn, hi)
  static String getLanguage() {
    return _prefs?.getString('weathergpt_language') ?? 'en';
  }

  static Future<void> setLanguage(String code) async {
    await _prefs?.setString('weathergpt_language', code);
  }

  // Selected User Persona / Role (citizen, farmer, fisherman, disaster_manager)
  static String getUserRole() {
    return _prefs?.getString('weathergpt_role') ?? 'citizen';
  }

  static Future<void> setUserRole(String role) async {
    await _prefs?.setString('weathergpt_role', role);
  }

  // User Profile & JWT Token
  static Map<String, dynamic>? getUserProfile() {
    final raw = _prefs?.getString('weathergpt_user');
    if (raw == null) return null;
    try {
      return jsonDecode(raw) as Map<String, dynamic>;
    } catch (_) {
      return null;
    }
  }

  static Future<void> setUserProfile(Map<String, dynamic>? profile) async {
    if (profile == null) {
      await _prefs?.remove('weathergpt_user');
    } else {
      await _prefs?.setString('weathergpt_user', jsonEncode(profile));
    }
  }

  // Cached Location (lat, lon, name, state)
  static Map<String, dynamic> getLocation() {
    final raw = _prefs?.getString('weathergpt_location');
    if (raw != null) {
      try {
        return jsonDecode(raw) as Map<String, dynamic>;
      } catch (_) {}
    }
    return {
      'name': 'Kolkata',
      'lat': 22.5726,
      'lon': 88.3639,
      'state': 'West Bengal',
    };
  }

  static Future<void> setLocation(Map<String, dynamic> loc) async {
    await _prefs?.setString('weathergpt_location', jsonEncode(loc));
  }

  // Persistent Chat History
  static List<Map<String, dynamic>> getChatHistory() {
    final raw = _prefs?.getString('weathergpt_chat_history');
    if (raw == null) return [];
    try {
      final list = jsonDecode(raw) as List;
      return list.map((e) => Map<String, dynamic>.from(e)).toList();
    } catch (_) {
      return [];
    }
  }

  static Future<void> saveChatHistory(List<Map<String, dynamic>> messages) async {
    await _prefs?.setString('weathergpt_chat_history', jsonEncode(messages));
  }

  static Future<void> clearChatHistory() async {
    await _prefs?.remove('weathergpt_chat_history');
  }
}
