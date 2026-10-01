import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../core/constants.dart';
import '../core/storage.dart';
import '../models/weather_models.dart';
import '../models/alert_model.dart';
import '../models/chat_message.dart';
import '../models/user_model.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  String baseUrl = AppConstants.defaultBackendUrl;

  // Notifier for Render Cold Start "Waking up server..." UI banner
  final ValueNotifier<bool> isWakingServer = ValueNotifier<bool>(false);

  // Helper with 1 automatic retry for Render cold starts
  Future<http.Response> _executeWithRetry(
    Future<http.Response> Function() requestFn, {
    String endpointName = 'API',
  }) async {
    try {
      final response = await requestFn().timeout(const Duration(seconds: 15));
      if (isWakingServer.value) isWakingServer.value = false;
      return response;
    } on TimeoutException {
      // Server is likely sleeping on Render free tier; trigger waking indicator
      debugPrint('[ApiService] $endpointName timed out. Server might be waking up... Retrying once.');
      isWakingServer.value = true;
      try {
        final retryResponse = await requestFn().timeout(const Duration(seconds: 45));
        isWakingServer.value = false;
        return retryResponse;
      } catch (e) {
        isWakingServer.value = false;
        rethrow;
      }
    } catch (e) {
      if (isWakingServer.value) isWakingServer.value = false;
      rethrow;
    }
  }

  // 1. Health Probe
  Future<bool> checkHealth() async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/health')).timeout(const Duration(seconds: 5));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // 2. Real-time Weather
  Future<CurrentWeatherResponse> getCurrentWeather({required double lat, required double lon}) async {
    final response = await _executeWithRetry(
      () => http.get(Uri.parse('$baseUrl/weather/current?lat=$lat&lon=$lon')),
      endpointName: 'getCurrentWeather',
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return CurrentWeatherResponse.fromJson(data);
    } else {
      throw Exception('Failed to fetch weather: ${response.statusCode}');
    }
  }

  // 3. Multi-Day Forecast (5-day slots)
  Future<ForecastResponse> getForecast({required double lat, required double lon, int days = 5}) async {
    final response = await _executeWithRetry(
      () => http.get(Uri.parse('$baseUrl/weather/forecast?lat=$lat&lon=$lon&days=$days')),
      endpointName: 'getForecast',
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return ForecastResponse.fromJson(data);
    } else {
      throw Exception('Failed to fetch forecast: ${response.statusCode}');
    }
  }

  // 4. Location Autocomplete Search
  Future<List<LocationModel>> searchLocations(String query) async {
    if (query.trim().isEmpty) return [];
    try {
      final response = await _executeWithRetry(
        () => http.get(Uri.parse('$baseUrl/locations/search?q=${Uri.encodeComponent(query)}')),
        endpointName: 'searchLocations',
      );

      if (response.statusCode == 200) {
        final List data = jsonDecode(response.body);
        return data.map((e) => LocationModel.fromJson(e)).toList();
      }
    } catch (e) {
      debugPrint('[ApiService] Location search error: $e');
    }
    return [];
  }

  // 5. Conversational Chat with Role & Location Grounding
  Future<ChatMessageModel> sendChat({
    required String message,
    String? sessionId,
    // ignore: non_constant_identifier_names
    String? session_id,
    double? lat,
    double? lon,
    String language = 'en',
    String? role,
  }) async {
    final effectiveRole = role ?? LocalStorageService.getUserRole();
    final effectiveSessionId = sessionId ?? session_id ?? LocalStorageService.getSessionId();
    
    // Enrich message with user role persona context matching web client
    String enrichedMessage = message;
    if (effectiveRole != 'citizen') {
      enrichedMessage = '[$effectiveRole persona] $message';
    }

    final payload = {
      'message': enrichedMessage,
      'session_id': effectiveSessionId,
      if (lat != null) 'lat': lat,
      if (lon != null) 'lon': lon,
      'language': language,
    };

    final response = await _executeWithRetry(
      () => http.post(
        Uri.parse('$baseUrl/chat'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(payload),
      ),
      endpointName: 'sendChat',
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final replyText = data['reply'] ?? '';

      // Extract explainability reasoning
      String? source;
      String? dataTimestamp;
      String? summary;

      if (replyText.contains('(Source:')) {
        final match = RegExp(r'\(Source:\s*([^,)]+)(?:,\s*as\s+of\s*([^)]+))?\)').firstMatch(replyText);
        if (match != null) {
          source = match.group(1)?.trim();
          dataTimestamp = match.group(2)?.trim();
        }
      }

      // Generate explainability summary matching web
      if (effectiveRole == 'farmer') {
        summary = 'Synthesized from precipitation probability and agricultural thresholds for field advisory.';
      } else if (effectiveRole == 'fisherman') {
        summary = 'Derived from coastal gale wind speed, sea surge telemetry, and return-to-harbor margins.';
      } else {
        summary = 'Grounded in live meteorological observations with 15-minute PostgreSQL spatial cache.';
      }

      return ChatMessageModel(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        role: 'assistant',
        content: replyText,
        timestamp: DateTime.now(),
        toolsCalled: (data['tools_called'] as List?)?.map((e) => e.toString()).toList() ?? [],
        explainabilitySummary: summary,
        dataSource: source ?? 'OpenWeather / IMD Doppler',
        dataTimestamp: dataTimestamp,
        userRole: effectiveRole,
      );
    } else {
      throw Exception('Chat failed: ${response.statusCode}');
    }
  }

  // 6. Chat History
  Future<List<ChatMessageModel>> getChatHistory(String sessionId) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/chat/history?session_id=$sessionId'));
      if (response.statusCode == 200) {
        final List data = jsonDecode(response.body);
        return data
            .where((m) => m['role'] == 'user' || m['role'] == 'assistant')
            .map((m) => ChatMessageModel.fromJson(m))
            .toList();
      }
    } catch (e) {
      debugPrint('[ApiService] Chat history fetch error: $e');
    }
    return [];
  }

  // 7. Active Alerts Feed with PostGIS Spatial Filter
  Future<List<AlertModel>> getActiveAlerts({double? lat, double? lon, double radiusKm = 50.0}) async {
    try {
      String url = '$baseUrl/alerts/active';
      if (lat != null && lon != null) {
        url += '?lat=$lat&lon=$lon&radius_km=$radiusKm';
      }

      final response = await _executeWithRetry(
        () => http.get(Uri.parse(url)),
        endpointName: 'getActiveAlerts',
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List list = data['alerts'] ?? [];
        return list.map((e) => AlertModel.fromJson(e)).toList();
      }
    } catch (e) {
      debugPrint('[ApiService] Active alerts fetch error: $e');
    }
    return [];
  }

  // 8. Ingest Alert (Disaster Manager War Room trigger)
  Future<AlertModel?> ingestAlert(Map<String, dynamic> payload) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/alerts/ingest'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(payload),
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        return AlertModel.fromJson(jsonDecode(response.body));
      }
    } catch (e) {
      debugPrint('[ApiService] Ingest alert error: $e');
    }
    return null;
  }

  // 9. Dismiss Alert
  Future<bool> dismissAlert(int alertId) async {
    try {
      final response = await http.delete(Uri.parse('$baseUrl/alerts/$alertId'));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // 10. Clear Demo Alerts
  Future<bool> clearDemoAlerts() async {
    try {
      final response = await http.post(Uri.parse('$baseUrl/alerts/clear-demo'));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // 11. Authentication
  Future<UserModel> signIn({required String email, required String password}) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/signin'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final user = UserModel.fromJson(data);
      await LocalStorageService.setUserProfile(user.toJson());
      await LocalStorageService.setUserRole(user.role);
      return user;
    } else {
      throw Exception('Invalid email or password');
    }
  }

  Future<UserModel> signUp({
    required String email,
    required String password,
    required String fullName,
    required String role,
    String? institution,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/signup'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
        'full_name': fullName,
        'role': role,
        'institution': institution ?? 'Citizen',
      }),
    );

    if (response.statusCode == 200 || response.statusCode == 201) {
      final data = jsonDecode(response.body);
      final user = UserModel.fromJson(data);
      await LocalStorageService.setUserProfile(user.toJson());
      await LocalStorageService.setUserRole(user.role);
      return user;
    } else {
      throw Exception('Sign up failed: ${response.statusCode}');
    }
  }

  // 12. Voice Services
  Future<String?> transcribeVoiceAudio(List<int> bytes, String language) async {
    try {
      final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/voice/transcribe'));
      request.files.add(http.MultipartFile.fromBytes('audio', bytes, filename: 'voice.wav'));
      request.fields['language'] = language;

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['transcript'] ?? data['text'];
      }
    } catch (e) {
      debugPrint('[ApiService] Voice transcription fallback: $e');
    }
    return null;
  }
}
