import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../core/constants.dart';

class AlertModel {
  final int? id;
  final int? locationId;
  final String locationName;
  final double lat;
  final double lon;
  final String type;
  final String severity; // Extreme, Severe, Moderate, Advisory
  final String message;
  final String source;
  final DateTime validFrom;
  final DateTime validUntil;
  final double? distanceKm;

  AlertModel({
    this.id,
    this.locationId,
    required this.locationName,
    required this.lat,
    required this.lon,
    required this.type,
    required this.severity,
    required this.message,
    required this.source,
    required this.validFrom,
    required this.validUntil,
    this.distanceKm,
  });

  factory AlertModel.fromJson(Map<String, dynamic> json) {
    DateTime parseDt(dynamic val) {
      if (val == null) return DateTime.now();
      try {
        return DateTime.tryParse(val.toString()) ?? DateTime.now();
      } catch (_) {
        return DateTime.now();
      }
    }

    return AlertModel(
      id: json['id'] as int?,
      locationId: json['location_id'] as int?,
      locationName: json['location_name'] ?? 'Target Area',
      lat: (json['lat'] as num?)?.toDouble() ?? 22.5726,
      lon: (json['lon'] as num?)?.toDouble() ?? 88.3639,
      type: json['type'] ?? 'Weather Alert',
      severity: json['severity'] ?? 'Moderate',
      message: json['message'] ?? 'Stay informed and follow local directives.',
      source: json['source'] ?? 'IMD Doppler Radar',
      validFrom: parseDt(json['valid_from']),
      validUntil: parseDt(json['valid_until']),
      distanceKm: (json['distance_km'] as num?)?.toDouble(),
    );
  }

  Color get color => AppColors.severityColor(severity);

  String get formattedExpiry {
    return DateFormat('hh:mm a · dd-MM-yyyy').format(validUntil.toLocal());
  }

  IconData get icon {
    final t = type.toLowerCase();
    if (t.contains('cyclone') || t.contains('surge')) {
      return Icons.cyclone;
    } else if (t.contains('rain') || t.contains('flood')) {
      return Icons.thunderstorm;
    } else if (t.contains('heat') || t.contains('fire')) {
      return Icons.local_fire_department;
    } else if (t.contains('landslide') || t.contains('mountain')) {
      return Icons.terrain;
    }
    return Icons.warning_amber_rounded;
  }
}
