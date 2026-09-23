import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const WeatherGPTApp());
}

class WeatherGPTApp extends StatelessWidget {
  const WeatherGPTApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'WeatherGPT Mobile',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0B1120),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF06B6D4),
          secondary: Color(0xFF10B981),
          surface: Color(0xFF1E293B),
        ),
        useMaterial3: true,
      ),
      home: const ChatScreen(),
    );
  }
}

class MessageItem {
  final String role;
  final String content;
  final List<String> tools;
  final DateTime timestamp;
  final Map<String, dynamic>? weatherData;

  MessageItem({
    required this.role,
    required this.content,
    this.tools = const [],
    required this.timestamp,
    this.weatherData,
  });
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<MessageItem> _messages = [];
  bool _isLoading = false;
  String _currentLocation = 'Kolkata';
  double _lat = 22.5726;
  double _lon = 88.3639;
  // Configurable backend URL: uses compile-time BACKEND_URL or defaults to deployed Render cloud service
  String _backendUrl = const String.fromEnvironment(
    'BACKEND_URL',
    defaultValue: 'https://weathergpt-backend.onrender.com',
  );

  @override
  void initState() {
    super.initState();
    _fetchInitialWeather();
  }

  Future<void> _fetchInitialWeather() async {
    try {
      final res = await http.get(Uri.parse('$_backendUrl/weather/current?lat=$_lat&lon=$_lon'));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        setState(() {
          _messages.add(
            MessageItem(
              role: 'assistant',
              content: 'Welcome to WeatherGPT (SIH PS 26068). Live weather loaded for $_currentLocation.',
              timestamp: DateTime.now(),
              weatherData: data,
            ),
          );
        });
      }
    } catch (_) {
      // Offline fallback welcome
      setState(() {
        _messages.add(
          MessageItem(
            role: 'assistant',
            content: 'Welcome to WeatherGPT. Ask me anything about current weather, 5-day forecasts, or farming advisories.',
            timestamp: DateTime.now(),
          ),
        );
      });
    }
  }

  Future<void> _sendMessage([String? prompt]) async {
    final text = prompt ?? _controller.text.trim();
    if (text.isEmpty || _isLoading) return;

    setState(() {
      _messages.add(MessageItem(role: 'user', content: text, timestamp: DateTime.now()));
      _isLoading = true;
    });
    _controller.clear();
    _scrollToBottom();

    try {
      final res = await http.post(
        Uri.parse('$_backendUrl/chat'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'message': text,
          'session_id': 'flutter-session-01',
          'lat': _lat,
          'lon': _lon,
        }),
      );

      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        setState(() {
          _messages.add(
            MessageItem(
              role: 'assistant',
              content: data['reply'] ?? '',
              tools: List<String>.from(data['tools_called'] ?? []),
              timestamp: DateTime.now(),
            ),
          );
        });
      } else {
        throw Exception('Server error: ${res.statusCode}');
      }
    } catch (e) {
      setState(() {
        _messages.add(
          MessageItem(
            role: 'assistant',
            content: 'Could not connect to the WeatherGPT backend. Please verify the server is running.',
            timestamp: DateTime.now(),
          ),
        );
      });
    } finally {
      setState(() => _isLoading = false);
      _scrollToBottom();
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('WeatherGPT', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
            Text('SIH PS 26068 · $_currentLocation', style: const TextStyle(fontSize: 12, color: Colors.cyanAccent)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.location_on, color: Colors.cyanAccent),
            onPressed: () {
              setState(() {
                if (_currentLocation == 'Kolkata') {
                  _currentLocation = 'Nadia';
                  _lat = 23.4710;
                  _lon = 88.5565;
                } else {
                  _currentLocation = 'Kolkata';
                  _lat = 22.5726;
                  _lon = 88.3639;
                }
              });
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Switched demo location to $_currentLocation')),
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Message list
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(12),
              itemCount: _messages.length,
              itemBuilder: (context, idx) {
                final m = _messages[idx];
                final isUser = m.role == 'user';
                return Align(
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    padding: const EdgeInsets.all(12),
                    constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.8),
                    decoration: BoxDecoration(
                      color: isUser ? const Color(0xFF0891B2) : const Color(0xFF1E293B),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: isUser ? Colors.transparent : const Color(0xFF334155),
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        if (m.tools.isNotEmpty)
                          Wrap(
                            spacing: 4,
                            children: m.tools
                                .map((t) => Chip(
                                      label: Text(t, style: const TextStyle(fontSize: 10, color: Colors.cyanAccent)),
                                      backgroundColor: const Color(0xFF0F172A),
                                      padding: EdgeInsets.zero,
                                    ))
                                .toList(),
                          ),
                        Text(m.content, style: const TextStyle(fontSize: 14)),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: LinearProgressIndicator(color: Colors.cyanAccent),
            ),
          // Input bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
            color: const Color(0xFF0F172A),
            child: Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.mic, color: Colors.cyanAccent),
                  onPressed: () {
                    _sendMessage("Will it rain in Kolkata tomorrow?");
                  },
                ),
                Expanded(
                  child: TextField(
                    controller: _controller,
                    onSubmitted: (_) => _sendMessage(),
                    decoration: const InputDecoration(
                      hintText: 'Ask WeatherGPT...',
                      border: InputBorder.none,
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.send, color: Colors.cyanAccent),
                  onPressed: () => _sendMessage(),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
