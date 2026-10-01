import 'package:flutter/material.dart';
import '../core/constants.dart';
import '../models/weather_models.dart';

class WeatherSummaryCard extends StatefulWidget {
  final CurrentWeatherResponse currentWeather;
  final ForecastResponse? forecast;
  final VoidCallback? onRefresh;

  const WeatherSummaryCard({
    super.key,
    required this.currentWeather,
    this.forecast,
    this.onRefresh,
  });

  @override
  State<WeatherSummaryCard> createState() => _WeatherSummaryCardState();
}

class _WeatherSummaryCardState extends State<WeatherSummaryCard> {
  bool _showForecast = false;

  IconData _getWeatherIcon(String condition) {
    final c = condition.toLowerCase();
    if (c.contains('thunder') || c.contains('lightning')) {
      return Icons.thunderstorm_rounded;
    } else if (c.contains('rain') || c.contains('shower') || c.contains('drizzle')) {
      return Icons.water_drop_rounded;
    } else if (c.contains('cloud') || c.contains('overcast') || c.contains('haze')) {
      return Icons.cloud_rounded;
    }
    return Icons.wb_sunny_rounded;
  }

  @override
  Widget build(BuildContext context) {
    final obs = widget.currentWeather.observation;
    final loc = widget.currentWeather.location;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.primaryCyan.withValues(alpha: 0.2)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.3),
            blurRadius: 16,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        children: [
          // Header Bar
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: AppColors.primaryCyan.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: AppColors.primaryCyan.withValues(alpha: 0.3)),
                  ),
                  child: Icon(_getWeatherIcon(obs.condition), color: AppColors.primaryCyan, size: 28),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        loc.name,
                        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 2),
                      Row(
                        children: [
                          Icon(Icons.schedule, size: 12, color: AppColors.primaryCyan.withValues(alpha: 0.8)),
                          const SizedBox(width: 4),
                          Text(
                            obs.formattedDateTime,
                            style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
                          ),
                          if (widget.currentWeather.cached) ...[
                            const SizedBox(width: 6),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: AppColors.accentEmerald.withValues(alpha: 0.15),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text(
                                'Cached ${widget.currentWeather.cacheAgeSeconds}s ago',
                                style: const TextStyle(fontSize: 9, color: AppColors.accentEmerald, fontWeight: FontWeight.bold),
                              ),
                            ),
                          ],
                        ],
                      ),
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${obs.temperature.round()}',
                          style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w800, color: AppColors.textPrimary),
                        ),
                        const Padding(
                          padding: EdgeInsets.only(top: 4),
                          child: Text('°C', style: TextStyle(fontSize: 16, color: AppColors.primaryCyan, fontWeight: FontWeight.bold)),
                        ),
                      ],
                    ),
                    Text(
                      obs.condition,
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.textSecondary),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Primary Metrics Grid
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            decoration: BoxDecoration(
              color: AppColors.background.withValues(alpha: 0.5),
              border: Border(
                top: BorderSide(color: AppColors.surfaceBorder.withValues(alpha: 0.6)),
                bottom: BorderSide(color: AppColors.surfaceBorder.withValues(alpha: 0.6)),
              ),
            ),
            child: Row(
              children: [
                _buildMetricItem(Icons.water_drop, 'Humidity', '${obs.humidity.round()}%', Colors.blueAccent),
                _buildMetricItem(Icons.air, 'Wind', '${obs.windSpeed} m/s', AppColors.primaryCyan),
                _buildMetricItem(Icons.cloud_queue, 'Rainfall', '${obs.rainfall} mm', Colors.lightBlueAccent),
              ],
            ),
          ),

          // Secondary Extended Metrics (UV, Visibility, Pressure)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildMiniMetric('Feels like', '${obs.feelsLike?.round() ?? obs.temperature.round()}°C'),
                _buildMiniMetric('UV Index', '${obs.uvIndex ?? 5} (Mod)'),
                _buildMiniMetric('Visibility', '${obs.visibility ?? 8.0} km'),
                _buildMiniMetric('Pressure', '${obs.pressure ?? 1012} hPa'),
              ],
            ),
          ),

          // Forecast Toggle Button
          if (widget.forecast != null && widget.forecast!.forecast.isNotEmpty) ...[
            InkWell(
              onTap: () => setState(() => _showForecast = !_showForecast),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 8),
                alignment: Alignment.center,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      _showForecast ? 'Hide 5-Day Forecast' : 'View 5-Day Forecast Slots',
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.primaryCyan),
                    ),
                    Icon(_showForecast ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down, color: AppColors.primaryCyan, size: 18),
                  ],
                ),
              ),
            ),

            if (_showForecast) ...[
              Container(
                height: 110,
                padding: const EdgeInsets.only(left: 12, right: 12, bottom: 12),
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: widget.forecast!.forecast.take(8).length,
                  itemBuilder: (context, index) {
                    final slot = widget.forecast!.forecast[index];
                    return Container(
                      width: 76,
                      margin: const EdgeInsets.only(right: 8),
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: AppColors.surfaceElevated,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: AppColors.surfaceBorder),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(slot.formattedHour, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                          const SizedBox(height: 4),
                          Icon(_getWeatherIcon(slot.condition), size: 20, color: AppColors.primaryCyan),
                          const SizedBox(height: 4),
                          Text('${slot.temperature.round()}°C', style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                          if (slot.rainfall > 0)
                            Text('${slot.rainfall}mm', style: const TextStyle(fontSize: 9, color: Colors.blueAccent)),
                        ],
                      ),
                    );
                  },
                ),
              ),
            ],
          ],
        ],
      ),
    );
  }

  Widget _buildMetricItem(IconData icon, String label, String value, Color iconColor) {
    return Expanded(
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 14, color: iconColor),
              const SizedBox(width: 4),
              Text(label, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
            ],
          ),
          const SizedBox(height: 4),
          Text(value, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
        ],
      ),
    );
  }

  Widget _buildMiniMetric(String label, String value) {
    return Column(
      children: [
        Text(label, style: const TextStyle(fontSize: 10, color: AppColors.textMuted)),
        const SizedBox(height: 2),
        Text(value, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary)),
      ],
    );
  }
}
