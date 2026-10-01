import 'dart:async';
import 'package:flutter/material.dart';
import '../core/constants.dart';
import '../models/alert_model.dart';
import '../services/api_service.dart';
import '../services/websocket_service.dart';
import '../widgets/alert_banner_widget.dart';

class AlertsScreen extends StatefulWidget {
  final Map<String, dynamic> location;

  const AlertsScreen({
    super.key,
    required this.location,
  });

  @override
  State<AlertsScreen> createState() => _AlertsScreenState();
}

class _AlertsScreenState extends State<AlertsScreen> {
  final ApiService _apiService = ApiService();
  final WebSocketService _wsService = WebSocketService();

  List<AlertModel> _alerts = [];
  bool _isLoading = true;
  String _selectedSeverityFilter = 'ALL';
  AlertModel? _liveToastAlert;
  StreamSubscription? _newAlertSub;
  StreamSubscription? _snapshotSub;

  @override
  void initState() {
    super.initState();
    _fetchAlerts();
    _initWebSocketSubscriptions();
  }

  void _initWebSocketSubscriptions() {
    _newAlertSub = _wsService.onNewAlert.listen((newAlert) {
      if (!mounted) return;
      setState(() {
        _alerts.insert(0, newAlert);
        _liveToastAlert = newAlert;
      });
      // Auto clear live toast after 8 seconds matching web
      Timer(const Duration(seconds: 8), () {
        if (mounted && _liveToastAlert == newAlert) {
          setState(() => _liveToastAlert = null);
        }
      });
    });

    _snapshotSub = _wsService.onSnapshot.listen((snapshot) {
      if (!mounted) return;
      setState(() {
        _alerts = snapshot;
        _isLoading = false;
      });
    });
  }

  @override
  void dispose() {
    _newAlertSub?.cancel();
    _snapshotSub?.cancel();
    super.dispose();
  }

  Future<void> _fetchAlerts() async {
    setState(() => _isLoading = true);
    final lat = (widget.location['lat'] as num).toDouble();
    final lon = (widget.location['lon'] as num).toDouble();

    final results = await _apiService.getActiveAlerts(lat: lat, lon: lon, radiusKm: 150.0);
    if (mounted) {
      setState(() {
        _alerts = results;
        _isLoading = false;
      });
    }
  }

  List<AlertModel> get _filteredAlerts {
    if (_selectedSeverityFilter == 'ALL') return _alerts;
    return _alerts.where((a) {
      final s = a.severity.toUpperCase();
      return s == _selectedSeverityFilter;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surfaceCard,
        elevation: 0,
        title: const Text(
          'Early Warning & Live Alert Feed',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
        ),
        actions: [
          // Live WebSocket Indicator Pill
          ValueListenableBuilder<bool>(
            valueListenable: _wsService.isConnected,
            builder: (context, connected, child) {
              return Container(
                margin: const EdgeInsets.symmetric(vertical: 14, horizontal: 12),
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: connected ? AppColors.accentEmerald.withOpacity(0.15) : AppColors.dangerRed.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: connected ? AppColors.accentEmerald : AppColors.dangerRed),
                ),
                child: Row(
                  children: [
                    CircleAvatar(
                      radius: 3,
                      backgroundColor: connected ? AppColors.accentEmerald : AppColors.dangerRed,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      connected ? 'LIVE WS' : 'RECONNECTING',
                      style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: connected ? AppColors.accentEmerald : AppColors.dangerRed),
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Live Pop-up Toast Banner
          if (_liveToastAlert != null)
            LiveAlertBannerWidget(
              alert: _liveToastAlert!,
              onDismiss: () => setState(() => _liveToastAlert = null),
            ),

          // Severity Filter Chips
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: ['ALL', 'EXTREME', 'SEVERE', 'MODERATE', 'ADVISORY'].map((sev) {
                  final isSelected = _selectedSeverityFilter == sev;
                  return Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: ChoiceChip(
                      label: Text(sev, style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: isSelected ? Colors.black : AppColors.textPrimary)),
                      selected: isSelected,
                      selectedColor: AppColors.primaryCyan,
                      backgroundColor: AppColors.surfaceCard,
                      side: BorderSide(color: isSelected ? AppColors.primaryCyan : AppColors.surfaceBorder),
                      onSelected: (val) {
                        if (val) setState(() => _selectedSeverityFilter = sev);
                      },
                    ),
                  );
                }).toList(),
              ),
            ),
          ),

          // Alerts List
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator(color: AppColors.primaryCyan))
                : _filteredAlerts.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.shield_outlined, size: 54, color: AppColors.accentEmerald.withOpacity(0.6)),
                            const SizedBox(height: 12),
                            const Text(
                              'No Active Severe Warnings',
                              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                            ),
                            const SizedBox(height: 4),
                            const Text(
                              'All regional monitoring zones are operating normally.',
                              style: TextStyle(fontSize: 12, color: AppColors.textMuted),
                            ),
                          ],
                        ),
                      )
                    : RefreshIndicator(
                        color: AppColors.primaryCyan,
                        backgroundColor: AppColors.surfaceCard,
                        onRefresh: _fetchAlerts,
                        child: ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          itemCount: _filteredAlerts.length,
                          itemBuilder: (context, index) {
                            final alert = _filteredAlerts[index];
                            final color = alert.color;

                            return Container(
                              margin: const EdgeInsets.only(bottom: 12),
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: AppColors.surfaceCard,
                                borderRadius: BorderRadius.circular(18),
                                border: Border.all(color: color.withOpacity(0.5), width: 1.2),
                                boxShadow: [
                                  BoxShadow(
                                    color: color.withOpacity(0.08),
                                    blurRadius: 10,
                                    offset: const Offset(0, 4),
                                  ),
                                ],
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Row(
                                        children: [
                                          Container(
                                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                            decoration: BoxDecoration(
                                              color: color,
                                              borderRadius: BorderRadius.circular(6),
                                            ),
                                            child: Text(
                                              alert.severity.toUpperCase(),
                                              style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.black),
                                            ),
                                          ),
                                          const SizedBox(width: 8),
                                          Text(
                                            alert.locationName,
                                            style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                                          ),
                                        ],
                                      ),
                                      if (alert.distanceKm != null)
                                        Text(
                                          '${alert.distanceKm!.round()} km away',
                                          style: const TextStyle(fontSize: 11, color: AppColors.primaryCyan, fontWeight: FontWeight.w600),
                                        ),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    alert.type,
                                    style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: color),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    alert.message,
                                    style: const TextStyle(fontSize: 13, color: AppColors.textSecondary, height: 1.3),
                                  ),
                                  const SizedBox(height: 12),
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Row(
                                        children: [
                                          const Icon(Icons.source, size: 12, color: AppColors.textMuted),
                                          const SizedBox(width: 4),
                                          Text(alert.source, style: const TextStyle(fontSize: 10, color: AppColors.textMuted)),
                                        ],
                                      ),
                                      Row(
                                        children: [
                                          const Icon(Icons.timer_outlined, size: 12, color: AppColors.textMuted),
                                          const SizedBox(width: 4),
                                          Text('Valid until: ${alert.formattedExpiry}', style: const TextStyle(fontSize: 10, color: AppColors.textMuted)),
                                        ],
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            );
                          },
                        ),
                      ),
          ),
        ],
      ),
    );
  }
}
