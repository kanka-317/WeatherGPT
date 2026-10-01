import 'package:flutter/material.dart';
import '../core/constants.dart';
import '../models/alert_model.dart';
import '../services/api_service.dart';

class DisasterManagerScreen extends StatefulWidget {
  const DisasterManagerScreen({super.key});

  @override
  State<DisasterManagerScreen> createState() => _DisasterManagerScreenState();
}

class _DisasterManagerScreenState extends State<DisasterManagerScreen> {
  final ApiService _apiService = ApiService();
  List<AlertModel> _alerts = [];
  bool _isLoading = true;
  bool _isTriggering = false;

  // Quick Pre-configured Multi-District Demo Scenarios matching website DisasterDashboard.jsx
  final List<Map<String, dynamic>> _quickDemoScenarios = [
    {
      'district': 'Nadia',
      'lat': 23.4710,
      'lon': 88.5565,
      'type': 'Heavy Rain & Flash Flood Warning',
      'severity': 'Severe',
      'icon': Icons.thunderstorm_rounded,
      'message': 'IMD Doppler Radar detected severe storm cloud clusters converging over Nadia. High risk of waterlogging across agricultural lands.',
      'source': 'IMD Doppler Radar Network',
    },
    {
      'district': 'South 24 Parganas',
      'lat': 22.1645,
      'lon': 88.6189,
      'type': 'Sundarbans Coastal Cyclone Surge Warning',
      'severity': 'Extreme',
      'icon': Icons.cyclone_rounded,
      'message': 'Bay of Bengal deep depression intensifying. Gale wind speeds of 85-105 km/h with 2.5m tidal storm surge expected in coastal Sundarbans.',
      'source': 'IMD Cyclone Warning Centre',
    },
    {
      'district': 'Darjeeling',
      'lat': 27.0410,
      'lon': 88.2663,
      'type': 'High-Altitude Landslide & Cloudburst Advisory',
      'severity': 'Moderate',
      'icon': Icons.terrain_rounded,
      'message': 'Continuous downpour triggering slope instability along NH-10. High risk of debris flow in hill sub-divisions.',
      'source': 'GSI & IMD Hill Station Ops',
    },
  ];

  @override
  void initState() {
    super.initState();
    _fetchAlerts();
  }

  Future<void> _fetchAlerts() async {
    setState(() => _isLoading = true);
    final list = await _apiService.getActiveAlerts();
    if (mounted) {
      setState(() {
        _alerts = list;
        _isLoading = false;
      });
    }
  }

  Future<void> _triggerScenario(Map<String, dynamic> scenario) async {
    setState(() => _isTriggering = true);
    final payload = {
      'location_name': scenario['district'],
      'lat': scenario['lat'],
      'lon': scenario['lon'],
      'type': scenario['type'],
      'severity': scenario['severity'],
      'message': scenario['message'],
      'source': scenario['source'],
      'valid_until': DateTime.now().add(const Duration(hours: 24)).toIso8601String(),
    };

    final result = await _apiService.ingestAlert(payload);
    if (mounted) {
      setState(() => _isTriggering = false);
      if (result != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: AppColors.accentEmerald,
            content: Text('Disaster alert broadcast to ${scenario['district']}!'),
          ),
        );
        _fetchAlerts();
      }
    }
  }

  Future<void> _clearAllAlerts() async {
    final success = await _apiService.clearDemoAlerts();
    if (mounted && success) {
      setState(() => _alerts = []);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          backgroundColor: AppColors.surfaceElevated,
          content: Text('All demo alerts cleared successfully.'),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    // Summary calculations
    final totalAlerts = _alerts.length;
    final extremeAlerts = _alerts.where((a) => a.severity.toLowerCase().contains('extreme') || a.severity.toLowerCase().contains('emergency')).length;
    final affectedDistricts = _alerts.map((a) => a.locationName).toSet().length;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surfaceCard,
        elevation: 0,
        title: Row(
          children: [
            const Icon(Icons.shield_rounded, color: AppColors.dangerRed, size: 22),
            const SizedBox(width: 8),
            const Text('Disaster Operations War Room', style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_sweep_rounded, color: AppColors.textMuted),
            tooltip: 'Clear Demo Alerts',
            onPressed: _clearAllAlerts,
          ),
          IconButton(
            icon: const Icon(Icons.refresh, color: AppColors.primaryCyan),
            onPressed: _fetchAlerts,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primaryCyan))
          : RefreshIndicator(
              color: AppColors.primaryCyan,
              backgroundColor: AppColors.surfaceCard,
              onRefresh: _fetchAlerts,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  // KPI Overview Header (Mobile Adapted Table Summary)
                  Row(
                    children: [
                      _buildSummaryCard('Active Warnings', '$totalAlerts', Icons.warning_rounded, AppColors.warningAmber),
                      const SizedBox(width: 10),
                      _buildSummaryCard('Critical (Red)', '$extremeAlerts', Icons.error_outline_rounded, AppColors.dangerRed),
                      const SizedBox(width: 10),
                      _buildSummaryCard('Districts', '$affectedDistricts', Icons.map_rounded, AppColors.primaryCyan),
                    ],
                  ),

                  const SizedBox(height: 18),

                  // Quick Simulation Trigger for SIH Judges
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppColors.surfaceCard,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: AppColors.primaryCyan.withOpacity(0.3)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Row(
                              children: [
                                Icon(Icons.bolt, color: AppColors.primaryCyan, size: 20),
                                SizedBox(width: 8),
                                Text('Simulate Emergency Scenarios', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                              ],
                            ),
                            if (_isTriggering)
                              const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primaryCyan)),
                          ],
                        ),
                        const SizedBox(height: 6),
                        const Text(
                          'Broadcast live emergency bulletins to test WebSocket and radar triggers.',
                          style: TextStyle(fontSize: 11, color: AppColors.textMuted),
                        ),
                        const SizedBox(height: 14),
                        ..._quickDemoScenarios.map((sc) {
                          final color = AppColors.severityColor(sc['severity']);
                          return Container(
                            margin: const EdgeInsets.only(bottom: 8),
                            decoration: BoxDecoration(
                              color: AppColors.surfaceElevated,
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: color.withOpacity(0.4)),
                            ),
                            child: ListTile(
                              dense: true,
                              leading: Icon(sc['icon'] as IconData, color: color, size: 22),
                              title: Text(sc['district']!, style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary, fontSize: 13)),
                              subtitle: Text(sc['type']!, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary), maxLines: 1),
                              trailing: ElevatedButton.icon(
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: color.withOpacity(0.18),
                                  foregroundColor: color,
                                  elevation: 0,
                                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8), side: BorderSide(color: color.withOpacity(0.6))),
                                ),
                                icon: const Icon(Icons.send_rounded, size: 12),
                                label: const Text('Broadcast', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                                onPressed: _isTriggering ? null : () => _triggerScenario(sc),
                              ),
                            ),
                          );
                        }),
                      ],
                    ),
                  ),

                  const SizedBox(height: 18),

                  // Mobile Adapted Table -> Card List
                  const Text('Active District Bulletins (Mobile Adapted Table)', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                  const SizedBox(height: 10),

                  if (_alerts.isEmpty)
                    Container(
                      padding: const EdgeInsets.all(24),
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        color: AppColors.surfaceCard,
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: const Text('No active disaster bulletins in database.', style: TextStyle(color: AppColors.textMuted, fontSize: 13)),
                    )
                  else
                    ..._alerts.map((al) {
                      final color = al.color;
                      return Container(
                        margin: const EdgeInsets.only(bottom: 10),
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: AppColors.surfaceCard,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: color.withOpacity(0.5)),
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
                                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                      decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(4)),
                                      child: Text(al.severity.toUpperCase(), style: const TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Colors.black)),
                                    ),
                                    const SizedBox(width: 8),
                                    Text(al.locationName, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                                  ],
                                ),
                                IconButton(
                                  icon: const Icon(Icons.close, size: 16, color: AppColors.textMuted),
                                  onPressed: () async {
                                    if (al.id != null) {
                                      await _apiService.dismissAlert(al.id!);
                                      _fetchAlerts();
                                    }
                                  },
                                  constraints: const BoxConstraints(),
                                  padding: EdgeInsets.zero,
                                ),
                              ],
                            ),
                            const SizedBox(height: 6),
                            Text(al.type, style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: color)),
                            const SizedBox(height: 2),
                            Text(al.message, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                          ],
                        ),
                      );
                    }),
                ],
              ),
            ),
    );
  }

  Widget _buildSummaryCard(String title, String count, IconData icon, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: AppColors.surfaceCard,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.surfaceBorder),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 20),
            const SizedBox(height: 4),
            Text(count, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
            const SizedBox(height: 2),
            Text(title, style: const TextStyle(fontSize: 10, color: AppColors.textMuted), textAlign: TextAlign.center, maxLines: 1),
          ],
        ),
      ),
    );
  }
}
