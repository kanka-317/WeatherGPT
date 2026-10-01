import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../core/constants.dart';
import '../models/weather_models.dart';
import '../services/api_service.dart';

class ClimateAnalyticsScreen extends StatefulWidget {
  final Map<String, dynamic> location;

  const ClimateAnalyticsScreen({
    super.key,
    required this.location,
  });

  @override
  State<ClimateAnalyticsScreen> createState() => _ClimateAnalyticsScreenState();
}

class _ClimateAnalyticsScreenState extends State<ClimateAnalyticsScreen> {
  final ApiService _apiService = ApiService();
  ForecastResponse? _forecast;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchTrendData();
  }

  Future<void> _fetchTrendData() async {
    final lat = (widget.location['lat'] as num).toDouble();
    final lon = (widget.location['lon'] as num).toDouble();

    try {
      final f = await _apiService.getForecast(lat: lat, lon: lon, days: 5);
      if (mounted) {
        setState(() {
          _forecast = f;
          _isLoading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final slots = _forecast?.forecast ?? [];

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surfaceCard,
        elevation: 0,
        title: const Text(
          'Climate Trends & Forecast Analytics',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primaryCyan))
          : RefreshIndicator(
              color: AppColors.primaryCyan,
              backgroundColor: AppColors.surfaceCard,
              onRefresh: _fetchTrendData,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  // KPI Overview Cards
                  Row(
                    children: [
                      _buildKpiCard('Peak Temp', '${slots.isNotEmpty ? slots.map((s) => s.temperature).reduce((a, b) => a > b ? a : b).round() : 32}°C', Icons.thermostat, Colors.orangeAccent),
                      const SizedBox(width: 10),
                      _buildKpiCard('Total Rain', '${slots.isNotEmpty ? slots.map((s) => s.rainfall).reduce((a, b) => a + b).toStringAsFixed(1) : 4.5} mm', Icons.water_drop, AppColors.primaryCyan),
                      const SizedBox(width: 10),
                      _buildKpiCard('Max Wind', '${slots.isNotEmpty ? slots.map((s) => s.windSpeed).reduce((a, b) => a > b ? a : b).toStringAsFixed(1) : 6.2} m/s', Icons.air, AppColors.accentEmerald),
                    ],
                  ),

                  const SizedBox(height: 18),

                  // Temperature Trend Line Chart
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppColors.surfaceCard,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: AppColors.surfaceBorder),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.show_chart, color: AppColors.primaryCyan, size: 20),
                            SizedBox(width: 8),
                            Text('5-Day Temperature Trajectory (°C)', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                          ],
                        ),
                        const SizedBox(height: 20),
                        SizedBox(
                          height: 200,
                          child: slots.isEmpty
                              ? const Center(child: Text('No data', style: TextStyle(color: AppColors.textMuted)))
                              : LineChart(
                                  LineChartData(
                                    gridData: const FlGridData(show: false),
                                    titlesData: FlTitlesData(
                                      topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                                      rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                                      bottomTitles: AxisTitles(
                                        sideTitles: SideTitles(
                                          showTitles: true,
                                          reservedSize: 22,
                                          interval: 2,
                                          getTitlesWidget: (val, meta) {
                                            final idx = val.toInt();
                                            if (idx >= 0 && idx < slots.length) {
                                              return Text(slots[idx].formattedHour, style: const TextStyle(fontSize: 9, color: AppColors.textMuted));
                                            }
                                            return const SizedBox();
                                          },
                                        ),
                                      ),
                                    ),
                                    borderData: FlBorderData(show: false),
                                    lineBarsData: [
                                      LineChartBarData(
                                        spots: slots.asMap().entries.take(12).map((e) => FlSpot(e.key.toDouble(), e.value.temperature)).toList(),
                                        isCurved: true,
                                        color: AppColors.primaryCyan,
                                        barWidth: 3,
                                        dotData: const FlDotData(show: true),
                                        belowBarData: BarAreaData(
                                          show: true,
                                          color: AppColors.primaryCyan.withValues(alpha: 0.15),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 18),

                  // Precipitation Bar Distribution
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppColors.surfaceCard,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: AppColors.surfaceBorder),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.bar_chart_rounded, color: Colors.blueAccent, size: 20),
                            SizedBox(width: 8),
                            Text('Precipitation Forecast Volume (mm)', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                          ],
                        ),
                        const SizedBox(height: 20),
                        SizedBox(
                          height: 180,
                          child: slots.isEmpty
                              ? const Center(child: Text('No data', style: TextStyle(color: AppColors.textMuted)))
                              : BarChart(
                                  BarChartData(
                                    gridData: const FlGridData(show: false),
                                    borderData: FlBorderData(show: false),
                                    titlesData: FlTitlesData(
                                      topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                                      rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                                      bottomTitles: AxisTitles(
                                        sideTitles: SideTitles(
                                          showTitles: true,
                                          reservedSize: 22,
                                          interval: 1,
                                          getTitlesWidget: (val, meta) {
                                            final idx = val.toInt();
                                            if (idx >= 0 && idx < slots.length) {
                                              return Text(slots[idx].formattedHour, style: const TextStyle(fontSize: 9, color: AppColors.textMuted));
                                            }
                                            return const SizedBox();
                                          },
                                        ),
                                      ),
                                    ),
                                    barGroups: slots.asMap().entries.take(8).map((e) {
                                      return BarChartGroupData(
                                        x: e.key,
                                        barRods: [
                                          BarChartRodData(
                                            toY: e.value.rainfall > 0 ? e.value.rainfall : 0.2,
                                            color: e.value.rainfall > 0 ? Colors.blueAccent : AppColors.surfaceElevated,
                                            width: 14,
                                            borderRadius: BorderRadius.circular(4),
                                          ),
                                        ],
                                      );
                                    }).toList(),
                                  ),
                                ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildKpiCard(String label, String value, IconData icon, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 10),
        decoration: BoxDecoration(
          color: AppColors.surfaceCard,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.surfaceBorder),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 22),
            const SizedBox(height: 6),
            Text(label, style: const TextStyle(fontSize: 10, color: AppColors.textMuted)),
            const SizedBox(height: 2),
            Text(value, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
          ],
        ),
      ),
    );
  }
}
