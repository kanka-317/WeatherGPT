import 'package:flutter/material.dart';
import '../core/constants.dart';
import '../models/weather_models.dart';
import '../services/api_service.dart';

class RealTimeWeatherScreen extends StatefulWidget {
  final Map<String, dynamic> location;
  final ValueChanged<Map<String, dynamic>> onLocationChanged;

  const RealTimeWeatherScreen({
    super.key,
    required this.location,
    required this.onLocationChanged,
  });

  @override
  State<RealTimeWeatherScreen> createState() => _RealTimeWeatherScreenState();
}

class _RealTimeWeatherScreenState extends State<RealTimeWeatherScreen> with SingleTickerProviderStateMixin {
  final ApiService _apiService = ApiService();
  final TextEditingController _searchController = TextEditingController();

  CurrentWeatherResponse? _weather;
  ForecastResponse? _forecast;
  bool _isLoading = true;
  List<LocationModel> _searchResults = [];
  bool _isSearching = false;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _fetchWeatherData();
  }

  Future<void> _fetchWeatherData() async {
    setState(() => _isLoading = true);
    final lat = (widget.location['lat'] as num).toDouble();
    final lon = (widget.location['lon'] as num).toDouble();

    try {
      final w = await _apiService.getCurrentWeather(lat: lat, lon: lon);
      final f = await _apiService.getForecast(lat: lat, lon: lon, days: 5);
      if (mounted) {
        setState(() {
          _weather = w;
          _forecast = f;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _onSearchChanged(String query) async {
    if (query.trim().length < 2) {
      setState(() => _searchResults = []);
      return;
    }
    setState(() => _isSearching = true);
    final res = await _apiService.searchLocations(query);
    if (mounted) {
      setState(() {
        _searchResults = res;
        _isSearching = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final obs = _weather?.observation;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surfaceCard,
        elevation: 0,
        title: const Text(
          'Live Atmospheric Telemetry',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
        ),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: AppColors.primaryCyan,
          labelColor: AppColors.primaryCyan,
          unselectedLabelColor: AppColors.textMuted,
          tabs: const [
            Tab(text: 'Current & Hourly'),
            Tab(text: '5-Day Forecast'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primaryCyan))
          : RefreshIndicator(
              color: AppColors.primaryCyan,
              backgroundColor: AppColors.surfaceCard,
              onRefresh: _fetchWeatherData,
              child: ListView(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                children: [
                  // Location Search & GPS Override Bar
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    decoration: BoxDecoration(
                      color: AppColors.surfaceCard,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppColors.surfaceBorder),
                    ),
                    child: TextField(
                      controller: _searchController,
                      style: const TextStyle(color: AppColors.textPrimary, fontSize: 13),
                      decoration: InputDecoration(
                        hintText: 'Search city or district (e.g. Nadia, Darjeeling)...',
                        hintStyle: const TextStyle(color: AppColors.textMuted, fontSize: 12),
                        icon: const Icon(Icons.search, size: 20, color: AppColors.primaryCyan),
                        border: InputBorder.none,
                        suffixIcon: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            if (_isSearching)
                              const Padding(
                                padding: EdgeInsets.all(8.0),
                                child: SizedBox(
                                  width: 14,
                                  height: 14,
                                  child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primaryCyan),
                                ),
                              ),
                            IconButton(
                              icon: const Icon(Icons.my_location_rounded, size: 18, color: AppColors.primaryCyan),
                              onPressed: () {
                                _searchController.clear();
                                widget.onLocationChanged({
                                  'name': 'Kolkata (GPS)',
                                  'lat': 22.5726,
                                  'lon': 88.3639,
                                  'state': 'West Bengal',
                                });
                                _fetchWeatherData();
                              },
                            ),
                          ],
                        ),
                      ),
                      onChanged: _onSearchChanged,
                    ),
                  ),

                  // Search Results Dropdown List
                  if (_searchResults.isNotEmpty) ...[
                    Container(
                      margin: const EdgeInsets.only(top: 6),
                      decoration: BoxDecoration(
                        color: AppColors.surfaceElevated,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: AppColors.primaryCyan.withOpacity(0.3)),
                      ),
                      child: Column(
                        children: _searchResults.map((loc) {
                          return ListTile(
                            dense: true,
                            leading: const Icon(Icons.location_on, color: AppColors.primaryCyan, size: 18),
                            title: Text('${loc.name}, ${loc.state ?? loc.country}', style: const TextStyle(color: AppColors.textPrimary, fontSize: 13)),
                            onTap: () {
                              widget.onLocationChanged({
                                'name': loc.name,
                                'lat': loc.lat,
                                'lon': loc.lon,
                                'state': loc.state,
                              });
                              _searchController.clear();
                              setState(() => _searchResults = []);
                              _fetchWeatherData();
                            },
                          );
                        }).toList(),
                      ),
                    ),
                  ],

                  const SizedBox(height: 12),

                  if (obs != null) ...[
                    // Main Temp & Condition Hero Card
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [
                            AppColors.surfaceCard,
                            AppColors.surfaceElevated,
                          ],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(24),
                        border: Border.all(color: AppColors.primaryCyan.withOpacity(0.3)),
                      ),
                      child: Column(
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    widget.location['name'],
                                    style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    obs.formattedDateTime,
                                    style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                                  ),
                                ],
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                decoration: BoxDecoration(
                                  color: AppColors.primaryCyan.withOpacity(0.15),
                                  borderRadius: BorderRadius.circular(10),
                                  border: Border.all(color: AppColors.primaryCyan.withOpacity(0.3)),
                                ),
                                child: Text(
                                  obs.source.toUpperCase(),
                                  style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.primaryCyan),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 18),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        '${obs.temperature.round()}',
                                        style: const TextStyle(fontSize: 54, fontWeight: FontWeight.w900, color: AppColors.textPrimary),
                                      ),
                                      const Padding(
                                        padding: EdgeInsets.only(top: 8),
                                        child: Text('°C', style: TextStyle(fontSize: 22, color: AppColors.primaryCyan, fontWeight: FontWeight.bold)),
                                      ),
                                    ],
                                  ),
                                  Text(
                                    obs.condition,
                                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.accentEmerald),
                                  ),
                                ],
                              ),
                              Icon(
                                obs.condition.toLowerCase().contains('rain') ? Icons.thunderstorm_rounded : Icons.wb_sunny_rounded,
                                size: 64,
                                color: AppColors.primaryCyan,
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 14),

                    // Comprehensive Atmospheric Metrics Grid (Full Parity)
                    GridView.count(
                      crossAxisCount: 2,
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      crossAxisSpacing: 10,
                      mainAxisSpacing: 10,
                      childAspectRatio: 2.1,
                      children: [
                        _buildStatBox(Icons.water_drop, 'Humidity', '${obs.humidity.round()}%', Colors.blue),
                        _buildStatBox(Icons.air, 'Wind Speed', '${obs.windSpeed} m/s', AppColors.primaryCyan),
                        _buildStatBox(Icons.cloudy_snowing, 'Precipitation', '${obs.rainfall} mm', Colors.cyanAccent),
                        _buildStatBox(Icons.thermostat, 'Feels Like', '${obs.feelsLike?.round() ?? obs.temperature.round()}°C', AppColors.warningAmber),
                        _buildStatBox(Icons.wb_sunny, 'UV Index', '${obs.uvIndex ?? 6} of 10', Colors.orange),
                        _buildStatBox(Icons.visibility, 'Visibility', '${obs.visibility ?? 8.5} km', AppColors.accentEmerald),
                        _buildStatBox(Icons.speed, 'Atmospheric Pressure', '${obs.pressure ?? 1012} hPa', Colors.purpleAccent),
                        _buildStatBox(Icons.cloud, 'Cloud Coverage', '${obs.cloudCover ?? 40}%', Colors.blueGrey),
                      ],
                    ),

                    const SizedBox(height: 16),

                    // Hourly or 5-Day Forecast Slots
                    if (_forecast != null) ...[
                      const Text(
                        '5-Day / 3-Hour Forecast Intervals',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                      ),
                      const SizedBox(height: 10),
                      ..._forecast!.forecast.take(6).map((slot) {
                        return Container(
                          margin: const EdgeInsets.only(bottom: 8),
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                          decoration: BoxDecoration(
                            color: AppColors.surfaceCard,
                            borderRadius: BorderRadius.circular(14),
                            border: Border.all(color: AppColors.surfaceBorder),
                          ),
                          child: Row(
                            children: [
                              SizedBox(
                                width: 90,
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(slot.formattedDay, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                                    Text(slot.formattedHour, style: const TextStyle(fontSize: 10, color: AppColors.textMuted)),
                                  ],
                                ),
                              ),
                              Icon(
                                slot.condition.toLowerCase().contains('rain') ? Icons.water_drop : Icons.wb_sunny_rounded,
                                color: AppColors.primaryCyan,
                                size: 20,
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Text(slot.condition, style: const TextStyle(fontSize: 13, color: AppColors.textSecondary)),
                              ),
                              Text(
                                '${slot.temperature.round()}°C',
                                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                              ),
                            ],
                          ),
                        );
                      }),
                    ],
                  ],
                ],
              ),
            ),
    );
  }

  Widget _buildStatBox(IconData icon, String title, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.surfaceBorder),
      ),
      child: Row(
        children: [
          CircleAvatar(
            backgroundColor: color.withOpacity(0.15),
            radius: 18,
            child: Icon(icon, color: color, size: 18),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(title, style: const TextStyle(fontSize: 11, color: AppColors.textMuted), maxLines: 1),
                const SizedBox(height: 2),
                Text(value, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.textPrimary), maxLines: 1),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
