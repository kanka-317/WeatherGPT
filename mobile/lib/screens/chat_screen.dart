import 'dart:async';
import 'package:flutter/material.dart';
import '../core/constants.dart';
import '../core/storage.dart';
import '../models/chat_message.dart';
import '../models/weather_models.dart';
import '../services/api_service.dart';
import '../widgets/chat_bubble_widget.dart';
import '../widgets/role_selector_sheet.dart';
import '../widgets/weather_summary_card.dart';

class ChatScreen extends StatefulWidget {
  final Map<String, dynamic> location;
  final ValueChanged<Map<String, dynamic>> onLocationChanged;

  const ChatScreen({
    super.key,
    required this.location,
    required this.onLocationChanged,
  });

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _inputController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final ApiService _apiService = ApiService();

  List<ChatMessageModel> _messages = [];
  bool _isLoading = false;
  bool _isListening = false;
  String _currentLanguage = 'en';
  String _currentRole = 'citizen';
  CurrentWeatherResponse? _currentWeather;
  ForecastResponse? _forecastData;

  // Suggested prompts matching web client
  final List<String> _suggestedPrompts = [
    'Will it rain in the next 24 hours?',
    'Should I irrigate my crops tomorrow?',
    'Is it safe to go out to sea today?',
    'What is the 5-day weather forecast?',
    'Are there any cyclone or heatwave alerts?',
  ];

  @override
  void initState() {
    super.initState();
    _currentLanguage = LocalStorageService.getLanguage();
    _currentRole = LocalStorageService.getUserRole();
    _loadChatHistory();
    _loadInitialWeather();
  }

  void _loadChatHistory() {
    final cached = LocalStorageService.getChatHistory();
    if (cached.isNotEmpty) {
      setState(() {
        _messages = cached.map((e) => ChatMessageModel.fromJson(e)).toList();
      });
      _scrollToBottom();
    } else {
      // Default welcome message matching website
      final welcome = ChatMessageModel(
        id: 'welcome',
        role: 'assistant',
        content: 'Welcome to WeatherGPT (SIH PS 26068). I provide real-time meteorological intelligence, agro-weather advisories, and disaster early-warnings grounded in live IMD & OpenWeather telemetry.',
        timestamp: DateTime.now(),
        explainabilitySummary: 'Initialized session with live geospatial grounding.',
        dataSource: 'IMD & OpenWeather Ground Radar',
        userRole: _currentRole,
      );
      setState(() => _messages = [welcome]);
    }
  }

  Future<void> _loadInitialWeather() async {
    final lat = (widget.location['lat'] as num).toDouble();
    final lon = (widget.location['lon'] as num).toDouble();

    try {
      final weather = await _apiService.getCurrentWeather(lat: lat, lon: lon);
      final forecast = await _apiService.getForecast(lat: lat, lon: lon, days: 5);
      if (mounted) {
        setState(() {
          _currentWeather = weather;
          _forecastData = forecast;
        });
      }
    } catch (e) {
      debugPrint('[ChatScreen] Initial weather load error: $e');
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _sendMessage([String? textOverride]) async {
    final text = textOverride ?? _inputController.text.trim();
    if (text.isEmpty || _isLoading) return;

    _inputController.clear();
    final userMsg = ChatMessageModel(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      role: 'user',
      content: text,
      timestamp: DateTime.now(),
      userRole: _currentRole,
    );

    setState(() {
      _messages.add(userMsg);
      _isLoading = true;
    });
    _scrollToBottom();

    final sessionId = LocalStorageService.getSessionId();
    final lat = (widget.location['lat'] as num).toDouble();
    final lon = (widget.location['lon'] as num).toDouble();

    try {
      final assistantMsg = await _apiService.sendChat(
        message: text,
        sessionId: sessionId,
        lat: lat,
        lon: lon,
        language: _currentLanguage,
        role: _currentRole,
      );

      if (mounted) {
        setState(() {
          _messages.add(assistantMsg);
          _isLoading = false;
        });
        _scrollToBottom();
        // Persist to local storage
        await LocalStorageService.saveChatHistory(_messages.map((m) => m.toJson()).toList());
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _messages.add(ChatMessageModel(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            role: 'assistant',
            content: 'Unable to connect to WeatherGPT server. Please check your internet connection or verify the backend is running.',
            timestamp: DateTime.now(),
          ));
          _isLoading = false;
        });
        _scrollToBottom();
      }
    }
  }

  void _simulateVoiceInput() {
    setState(() => _isListening = !_isListening);
    if (_isListening) {
      // Simulate speech recognition input according to selected language
      Timer(const Duration(seconds: 2), () {
        if (!mounted || !_isListening) return;
        setState(() => _isListening = false);
        if (_currentLanguage == 'bn') {
          _sendMessage('আজ কি বৃষ্টি হবে?');
        } else if (_currentLanguage == 'hi') {
          _sendMessage('क्या कल बारिश होगी?');
        } else {
          _sendMessage('What is the weather today?');
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surfaceCard,
        elevation: 0,
        titleSpacing: 16,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Text(
                  'WeatherGPT',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: AppColors.primaryCyan.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: AppColors.primaryCyan.withValues(alpha: 0.3)),
                  ),
                  child: const Text('SIH PS 26068', style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: AppColors.primaryCyan)),
                ),
              ],
            ),
            const SizedBox(height: 2),
            Text(
              '${widget.location['name']} (${(widget.location['lat'] as num).toStringAsFixed(2)}°, ${(widget.location['lon'] as num).toStringAsFixed(2)}°)',
              style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
            ),
          ],
        ),
        actions: [
          // Persona / Role Badge Button
          InkWell(
            onTap: () {
              RoleSelectorSheet.show(
                context,
                currentRole: _currentRole,
                onRoleSelected: (newRole) {
                  setState(() => _currentRole = newRole);
                },
              );
            },
            borderRadius: BorderRadius.circular(10),
            child: Container(
              margin: const EdgeInsets.symmetric(vertical: 10, horizontal: 4),
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: AppColors.surfaceElevated,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: AppColors.primaryCyan.withValues(alpha: 0.4)),
              ),
              child: Row(
                children: [
                  Icon(
                    _currentRole == 'farmer'
                        ? Icons.agriculture
                        : _currentRole == 'fisherman'
                            ? Icons.sailing
                            : _currentRole == 'disaster_manager'
                                ? Icons.shield
                                : Icons.person,
                    size: 14,
                    color: AppColors.primaryCyan,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    _currentRole.toUpperCase(),
                    style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                  ),
                ],
              ),
            ),
          ),

          // Language Selector Dropdown
          PopupMenuButton<String>(
            icon: const Icon(Icons.language_rounded, color: AppColors.primaryCyan, size: 20),
            color: AppColors.surfaceCard,
            onSelected: (code) {
              setState(() => _currentLanguage = code);
              LocalStorageService.setLanguage(code);
            },
            itemBuilder: (context) => AppConstants.supportedLanguages.map((lang) {
              return PopupMenuItem<String>(
                value: lang['code'],
                child: Row(
                  children: [
                    Text(lang['native']!, style: const TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.w600)),
                    const SizedBox(width: 8),
                    Text('(${lang['label']})', style: const TextStyle(color: AppColors.textMuted, fontSize: 11)),
                  ],
                ),
              );
            }).toList(),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: Column(
        children: [
          // Active Weather Overview Card
          if (_currentWeather != null)
            WeatherSummaryCard(
              currentWeather: _currentWeather!,
              forecast: _forecastData,
              onRefresh: _loadInitialWeather,
            ),

          // Messages List
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.symmetric(vertical: 8),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                return ChatBubbleWidget(
                  message: msg,
                  onSpeak: () {
                    // Trigger speech synthesis
                  },
                );
              },
            ),
          ),

          // Typing Indicator
          if (_isLoading)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 6),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: AppColors.surfaceCard,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppColors.surfaceBorder),
                    ),
                    child: const Row(
                      children: [
                        SizedBox(
                          width: 12,
                          height: 12,
                          child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primaryCyan),
                        ),
                        SizedBox(width: 8),
                        Text('WeatherGPT is synthesizing grounded advice...', style: TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                      ],
                    ),
                  ),
                ],
              ),
            ),

          // Suggested Prompts Bar
          SizedBox(
            height: 38,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: _suggestedPrompts.length,
              itemBuilder: (context, index) {
                final prompt = _suggestedPrompts[index];
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ActionChip(
                    backgroundColor: AppColors.surfaceElevated,
                    side: const BorderSide(color: AppColors.surfaceBorder),
                    label: Text(prompt, style: const TextStyle(fontSize: 11, color: AppColors.textPrimary)),
                    onPressed: () => _sendMessage(prompt),
                  ),
                );
              },
            ),
          ),

          const SizedBox(height: 8),

          // Input Bar with Mic & Send
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: const BoxDecoration(
              color: AppColors.surfaceCard,
              border: const Border(top: const BorderSide(color: AppColors.surfaceBorder)),
            ),
            child: SafeArea(
              child: Row(
                children: [
                  // Mic button
                  IconButton(
                    icon: Icon(
                      _isListening ? Icons.mic_rounded : Icons.mic_none_rounded,
                      color: _isListening ? AppColors.dangerRed : AppColors.primaryCyan,
                    ),
                    onPressed: _simulateVoiceInput,
                  ),

                  // Text Field
                  Expanded(
                    child: TextField(
                      controller: _inputController,
                      style: const TextStyle(color: AppColors.textPrimary, fontSize: 14),
                      decoration: InputDecoration(
                        hintText: 'Ask WeatherGPT (${widget.location['name']})...',
                        hintStyle: const TextStyle(color: AppColors.textMuted, fontSize: 13),
                        filled: true,
                        fillColor: AppColors.background,
                        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(20),
                          borderSide: const BorderSide(color: AppColors.surfaceBorder),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(20),
                          borderSide: const BorderSide(color: AppColors.surfaceBorder),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(20),
                          borderSide: const BorderSide(color: AppColors.primaryCyan),
                        ),
                      ),
                      onSubmitted: (val) => _sendMessage(),
                    ),
                  ),

                  const SizedBox(width: 8),

                  // Send button
                  CircleAvatar(
                    backgroundColor: AppColors.primaryCyan,
                    radius: 20,
                    child: IconButton(
                      icon: const Icon(Icons.send_rounded, color: Colors.black, size: 18),
                      onPressed: () => _sendMessage(),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
