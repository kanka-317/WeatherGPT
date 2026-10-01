import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../core/constants.dart';
import '../models/alert_model.dart';
import '../services/api_service.dart';
import '../services/websocket_service.dart';

class RiskMapScreen extends StatefulWidget {
  final Map<String, dynamic> location;

  const RiskMapScreen({
    super.key,
    required this.location,
  });

  @override
  State<RiskMapScreen> createState() => _RiskMapScreenState();
}

class _RiskMapScreenState extends State<RiskMapScreen> {
  final ApiService _apiService = ApiService();
  final WebSocketService _wsService = WebSocketService();
  final MapController _mapController = MapController();

  List<AlertModel> _alerts = [];
  bool _isLoading = true;
  StreamSubscription? _alertSub;

  // Pre-configured district focal points matching website
  final List<Map<String, dynamic>> _monitoringDistricts = [
    {'name': 'Kolkata', 'lat': 22.5726, 'lon': 88.3639, 'severity': 'Advisory'},
    {'name': 'Nadia', 'lat': 23.4710, 'lon': 88.5565, 'severity': 'Severe'},
    {'name': 'South 24 Parganas', 'lat': 22.1645, 'lon': 88.6189, 'severity': 'Extreme'},
    {'name': 'Darjeeling', 'lat': 27.0410, 'lon': 88.2663, 'severity': 'Moderate'},
    {'name': 'Delhi', 'lat': 28.6139, 'lon': 77.2090, 'severity': 'Advisory'},
    {'name': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777, 'severity': 'Moderate'},
  ];

  @override
  void initState() {
    super.initState();
    _fetchAlerts();
    _alertSub = _wsService.onNewAlert.listen((newAlert) {
      if (mounted) {
        setState(() {
          _alerts.insert(0, newAlert);
        });
      }
    });
  }

  @override
  void dispose() {
    _alertSub?.cancel();
    super.dispose();
  }

  Future<void> _fetchAlerts() async {
    final list = await _apiService.getActiveAlerts();
    if (mounted) {
      setState(() {
        _alerts = list;
        _isLoading = false;
      });
    }
  }

  void _showDistrictDetails(String districtName, double lat, double lon) {
    final matchingAlerts = _alerts.where((a) => a.locationName.toLowerCase().contains(districtName.toLowerCase())).toList();

    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.surfaceCard,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) {
        return Container(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '$districtName War Room',
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                  ),
                  Text(
                    '${lat.toStringAsFixed(2)}°, ${lon.toStringAsFixed(2)}°',
                    style: const TextStyle(fontSize: 12, color: AppColors.primaryCyan),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              if (matchingAlerts.isEmpty) ...[
                const Row(
                  children: [
                    Icon(Icons.check_circle_outline, color: AppColors.accentEmerald, size: 20),
                    SizedBox(width: 8),
                    Text('No severe weather bulletins active in this zone.', style: TextStyle(color: AppColors.textSecondary, fontSize: 13)),
                  ],
                ),
              ] else ...[
                ...matchingAlerts.map((a) {
                  return Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: a.color.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: a.color),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(a.type, style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: a.color)),
                        const SizedBox(height: 4),
                        Text(a.message, style: const TextStyle(fontSize: 12, color: AppColors.textPrimary)),
                      ],
                    ),
                  );
                }),
              ],
              const SizedBox(height: 16),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final centerLat = (widget.location['lat'] as num).toDouble();
    final centerLon = (widget.location['lon'] as num).toDouble();

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surfaceCard,
        elevation: 0,
        title: const Text(
          'GIS Disaster Operations Map',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.my_location, color: AppColors.primaryCyan),
            onPressed: () {
              _mapController.move(LatLng(centerLat, centerLon), 8.0);
            },
          ),
        ],
        bottom: _isLoading
            ? const PreferredSize(
                preferredSize: Size.fromHeight(2),
                child: LinearProgressIndicator(minHeight: 2, color: AppColors.primaryCyan, backgroundColor: Colors.transparent),
              )
            : null,
      ),
      body: Stack(
        children: [
          // Map Canvas
          FlutterMap(
            mapController: _mapController,
            options: MapOptions(
              initialCenter: LatLng(centerLat, centerLon),
              initialZoom: 7.0,
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.weathergpt.app',
              ),
              MarkerLayer(
                markers: _monitoringDistricts.map((d) {
                  final color = AppColors.severityColor(d['severity'] as String);
                  final lat = (d['lat'] as num).toDouble();
                  final lon = (d['lon'] as num).toDouble();

                  return Marker(
                    point: LatLng(lat, lon),
                    width: 50,
                    height: 50,
                    child: GestureDetector(
                      onTap: () => _showDistrictDetails(d['name'], lat, lon),
                      child: Container(
                        decoration: BoxDecoration(
                          color: color.withOpacity(0.3),
                          shape: BoxShape.circle,
                          border: Border.all(color: color, width: 2.5),
                          boxShadow: [
                            BoxShadow(color: color.withOpacity(0.4), blurRadius: 10),
                          ],
                        ),
                        child: Center(
                          child: Icon(Icons.shield_rounded, color: color, size: 24),
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ],
          ),

          // Top Legend Bar
          Positioned(
            top: 12,
            left: 16,
            right: 16,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              decoration: BoxDecoration(
                color: AppColors.surfaceCard.withOpacity(0.92),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.surfaceBorder),
                boxShadow: const [BoxShadow(color: Colors.black45, blurRadius: 10)],
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildLegendItem('Extreme', AppColors.dangerRed),
                  _buildLegendItem('Severe', const Color(0xFFF97316)),
                  _buildLegendItem('Moderate', AppColors.warningAmber),
                  _buildLegendItem('Advisory', AppColors.accentEmerald),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLegendItem(String label, Color color) {
    return Row(
      children: [
        CircleAvatar(radius: 4, backgroundColor: color),
        const SizedBox(width: 4),
        Text(label, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
      ],
    );
  }
}
