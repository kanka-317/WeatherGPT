import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'core/constants.dart';
import 'core/storage.dart';
import 'models/user_model.dart';
import 'services/websocket_service.dart';
import 'widgets/waking_server_indicator.dart';
import 'screens/chat_screen.dart';
import 'screens/real_time_weather_screen.dart';
import 'screens/alerts_screen.dart';
import 'screens/risk_map_screen.dart';
import 'screens/climate_analytics_screen.dart';
import 'screens/disaster_manager_screen.dart';
import 'screens/auth_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await LocalStorageService.init();
  WebSocketService().connect();
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
        scaffoldBackgroundColor: AppColors.background,
        textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme),
        colorScheme: const ColorScheme.dark(
          primary: AppColors.primaryCyan,
          secondary: AppColors.accentEmerald,
          surface: AppColors.surfaceCard,
          error: AppColors.dangerRed,
        ),
        useMaterial3: true,
      ),
      home: const MainNavigationShell(),
    );
  }
}

class MainNavigationShell extends StatefulWidget {
  const MainNavigationShell({super.key});

  @override
  State<MainNavigationShell> createState() => _MainNavigationShellState();
}

class _MainNavigationShellState extends State<MainNavigationShell> {
  int _currentIndex = 0;
  Map<String, dynamic> _location = {
    'name': 'Kolkata',
    'lat': 22.5726,
    'lon': 88.3639,
    'state': 'West Bengal',
  };
  UserModel? _currentUser;
  String _userRole = 'citizen';

  @override
  void initState() {
    super.initState();
    _location = LocalStorageService.getLocation();
    _userRole = LocalStorageService.getUserRole();
    final profile = LocalStorageService.getUserProfile();
    if (profile != null) {
      _currentUser = UserModel.fromJson(profile);
      _userRole = _currentUser!.role;
    }
  }

  void _onLocationChanged(Map<String, dynamic> newLoc) {
    setState(() => _location = newLoc);
    LocalStorageService.setLocation(newLoc);
  }

  void _openAuthDialog() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (ctx) => AuthScreen(
          onAuthSuccess: (user) {
            setState(() {
              _currentUser = user;
              _userRole = user.role;
            });
          },
        ),
      ),
    );
  }

  void _signOut() async {
    await LocalStorageService.setUserProfile(null);
    await LocalStorageService.setUserRole('citizen');
    setState(() {
      _currentUser = null;
      _userRole = 'citizen';
      if (_currentIndex >= 5) _currentIndex = 0;
    });
  }

  @override
  Widget build(BuildContext context) {
    final isDisasterManager = _userRole == 'disaster_manager';

    // Screens list (matching all 9 modules requested)
    final screens = [
      ChatScreen(location: _location, onLocationChanged: _onLocationChanged),
      RealTimeWeatherScreen(location: _location, onLocationChanged: _onLocationChanged),
      AlertsScreen(location: _location),
      RiskMapScreen(location: _location),
      ClimateAnalyticsScreen(location: _location),
      if (isDisasterManager) const DisasterManagerScreen(),
    ];

    // Bottom Navigation Bar items
    final navItems = [
      const BottomNavigationBarItem(
        icon: Icon(Icons.chat_bubble_outline_rounded),
        activeIcon: Icon(Icons.chat_bubble_rounded),
        label: 'AI Chat',
      ),
      const BottomNavigationBarItem(
        icon: Icon(Icons.cloud_outlined),
        activeIcon: Icon(Icons.cloud_rounded),
        label: 'Weather',
      ),
      const BottomNavigationBarItem(
        icon: Icon(Icons.notifications_none_rounded),
        activeIcon: Icon(Icons.notifications_active_rounded),
        label: 'Alerts',
      ),
      const BottomNavigationBarItem(
        icon: Icon(Icons.map_outlined),
        activeIcon: Icon(Icons.map_rounded),
        label: 'GIS Map',
      ),
      const BottomNavigationBarItem(
        icon: Icon(Icons.analytics_outlined),
        activeIcon: Icon(Icons.analytics_rounded),
        label: 'Analytics',
      ),
      if (isDisasterManager)
        const BottomNavigationBarItem(
          icon: Icon(Icons.shield_outlined),
          activeIcon: Icon(Icons.shield_rounded),
          label: 'War Room',
        ),
    ];

    return Scaffold(
      body: Column(
        children: [
          // Cold-start indicator for Render free tier
          const WakingServerIndicator(),

          // Active Screen
          Expanded(
            child: IndexedStack(
              index: _currentIndex < screens.length ? _currentIndex : 0,
              children: screens,
            ),
          ),
        ],
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: AppColors.surfaceCard,
          border: Border(top: BorderSide(color: AppColors.surfaceBorder)),
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex < navItems.length ? _currentIndex : 0,
          onTap: (index) => setState(() => _currentIndex = index),
          backgroundColor: AppColors.surfaceCard,
          selectedItemColor: AppColors.primaryCyan,
          unselectedItemColor: AppColors.textMuted,
          selectedFontSize: 11,
          unselectedFontSize: 10,
          type: BottomNavigationBarType.fixed,
          items: navItems,
        ),
      ),
    );
  }
}
