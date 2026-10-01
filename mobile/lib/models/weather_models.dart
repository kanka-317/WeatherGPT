import 'package:intl/intl.dart';

class LocationModel {
  final String name;
  final double lat;
  final double lon;
  final String? state;
  final String country;

  LocationModel({
    required this.name,
    required this.lat,
    required this.lon,
    this.state,
    this.country = 'IN',
  });

  factory LocationModel.fromJson(Map<String, dynamic> json) {
    return LocationModel(
      name: json['name'] ?? 'Selected Location',
      lat: (json['lat'] as num?)?.toDouble() ?? 22.5726,
      lon: (json['lon'] as num?)?.toDouble() ?? 88.3639,
      state: json['state'],
      country: json['country'] ?? 'IN',
    );
  }

  Map<String, dynamic> toJson() => {
    'name': name,
    'lat': lat,
    'lon': lon,
    'state': state,
    'country': country,
  };
}

class WeatherObservationModel {
  final double temperature;
  final double humidity;
  final double rainfall;
  final double windSpeed;
  final double? windDirection;
  final String condition;
  final String source;
  final DateTime timestamp;
  final double? feelsLike;
  final double? tempMin;
  final double? tempMax;
  final int? cloudCover;
  final double? visibility;
  final int? uvIndex;
  final int? pressure;

  WeatherObservationModel({
    required this.temperature,
    required this.humidity,
    required this.rainfall,
    required this.windSpeed,
    this.windDirection,
    required this.condition,
    required this.source,
    required this.timestamp,
    this.feelsLike,
    this.tempMin,
    this.tempMax,
    this.cloudCover,
    this.visibility,
    this.uvIndex,
    this.pressure,
  });

  factory WeatherObservationModel.fromJson(Map<String, dynamic> json) {
    DateTime ts;
    try {
      final raw = json['timestamp']?.toString() ?? '';
      ts = DateTime.tryParse(raw) ?? DateTime.now();
    } catch (_) {
      ts = DateTime.now();
    }

    return WeatherObservationModel(
      temperature: (json['temperature'] as num?)?.toDouble() ?? 28.0,
      humidity: (json['humidity'] as num?)?.toDouble() ?? 65.0,
      rainfall: (json['rainfall'] as num?)?.toDouble() ?? 0.0,
      windSpeed: (json['wind_speed'] as num?)?.toDouble() ?? 3.5,
      windDirection: (json['wind_direction'] as num?)?.toDouble(),
      condition: json['condition'] ?? 'Clear',
      source: json['source'] ?? 'OpenWeather',
      timestamp: ts,
      feelsLike: (json['feels_like'] as num?)?.toDouble() ?? ((json['temperature'] as num?)?.toDouble() ?? 28.0) + 1.2,
      tempMin: (json['temp_min'] as num?)?.toDouble() ?? 24.0,
      tempMax: (json['temp_max'] as num?)?.toDouble() ?? 32.0,
      cloudCover: json['cloud_cover'] ?? 40,
      visibility: (json['visibility'] as num?)?.toDouble() ?? 8.5,
      uvIndex: json['uv_index'] ?? 6,
      pressure: json['pressure'] ?? 1012,
    );
  }

  String get formattedDateTime {
    return DateFormat('hh:mm a · dd-MM-yyyy').format(timestamp.toLocal());
  }
}

class CurrentWeatherResponse {
  final LocationModel location;
  final WeatherObservationModel observation;
  final bool cached;
  final int cacheAgeSeconds;
  final List<dynamic> alerts;

  CurrentWeatherResponse({
    required this.location,
    required this.observation,
    this.cached = false,
    this.cacheAgeSeconds = 0,
    this.alerts = const [],
  });

  factory CurrentWeatherResponse.fromJson(Map<String, dynamic> json) {
    return CurrentWeatherResponse(
      location: LocationModel.fromJson(json['location'] ?? {}),
      observation: WeatherObservationModel.fromJson(json['observation'] ?? {}),
      cached: json['cached'] ?? false,
      cacheAgeSeconds: json['cache_age_seconds'] ?? 0,
      alerts: json['alerts'] as List? ?? [],
    );
  }
}

class ForecastSlotModel {
  final DateTime timestamp;
  final double temperature;
  final double feelsLike;
  final double tempMin;
  final double tempMax;
  final double humidity;
  final double rainfall;
  final double windSpeed;
  final String condition;
  final String description;
  final String icon;

  ForecastSlotModel({
    required this.timestamp,
    required this.temperature,
    required this.feelsLike,
    required this.tempMin,
    required this.tempMax,
    required this.humidity,
    required this.rainfall,
    required this.windSpeed,
    required this.condition,
    required this.description,
    required this.icon,
  });

  factory ForecastSlotModel.fromJson(Map<String, dynamic> json) {
    DateTime ts;
    try {
      ts = DateTime.tryParse(json['timestamp']?.toString() ?? '') ?? DateTime.now();
    } catch (_) {
      ts = DateTime.now();
    }

    return ForecastSlotModel(
      timestamp: ts,
      temperature: (json['temperature'] as num?)?.toDouble() ?? 26.0,
      feelsLike: (json['feels_like'] as num?)?.toDouble() ?? 27.0,
      tempMin: (json['temp_min'] as num?)?.toDouble() ?? 22.0,
      tempMax: (json['temp_max'] as num?)?.toDouble() ?? 30.0,
      humidity: (json['humidity'] as num?)?.toDouble() ?? 60.0,
      rainfall: (json['rainfall'] as num?)?.toDouble() ?? 0.0,
      windSpeed: (json['wind_speed'] as num?)?.toDouble() ?? 3.0,
      condition: json['condition'] ?? 'Clear',
      description: json['description'] ?? 'Scattered clouds',
      icon: json['icon'] ?? '01d',
    );
  }

  String get formattedHour {
    return DateFormat('hh a').format(timestamp.toLocal());
  }

  String get formattedDay {
    return DateFormat('EEE, d MMM').format(timestamp.toLocal());
  }
}

class ForecastResponse {
  final LocationModel location;
  final int count;
  final List<ForecastSlotModel> forecast;

  ForecastResponse({
    required this.location,
    required this.count,
    required this.forecast,
  });

  factory ForecastResponse.fromJson(Map<String, dynamic> json) {
    final list = json['forecast'] as List? ?? [];
    return ForecastResponse(
      location: LocationModel.fromJson(json['location'] ?? {}),
      count: json['count'] ?? list.length,
      forecast: list.map((e) => ForecastSlotModel.fromJson(e)).toList(),
    );
  }
}
