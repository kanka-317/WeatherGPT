import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../core/constants.dart';
import '../models/alert_model.dart';

class WebSocketService {
  static final WebSocketService _instance = WebSocketService._internal();
  factory WebSocketService() => _instance;
  WebSocketService._internal();

  WebSocketChannel? _channel;
  final StreamController<AlertModel> _alertStreamController = StreamController<AlertModel>.broadcast();
  final StreamController<List<AlertModel>> _snapshotStreamController = StreamController<List<AlertModel>>.broadcast();
  final ValueNotifier<bool> isConnected = ValueNotifier<bool>(false);

  Stream<AlertModel> get onNewAlert => _alertStreamController.stream;
  Stream<List<AlertModel>> get onSnapshot => _snapshotStreamController.stream;

  Timer? _reconnectTimer;
  bool _isDisposed = false;

  void connect({String? wsUrl}) {
    _isDisposed = false;
    final url = wsUrl ?? AppConstants.defaultWsUrl;

    try {
      _channel?.sink.close();
      _channel = WebSocketChannel.connect(Uri.parse(url));

      _channel!.stream.listen(
        (message) {
          isConnected.value = true;
          try {
            final data = jsonDecode(message);
            final event = data['event'];

            if (event == 'INIT_SNAPSHOT') {
              final list = (data['alerts'] as List?)?.map((e) => AlertModel.fromJson(e)).toList() ?? [];
              _snapshotStreamController.add(list);
            } else if (event == 'NEW_ALERT') {
              final alertData = data['alert'];
              if (alertData != null) {
                final alert = AlertModel.fromJson(alertData);
                _alertStreamController.add(alert);
              }
            }
          } catch (e) {
            debugPrint('[WebSocketService] Parse error: $e');
          }
        },
        onDone: () {
          isConnected.value = false;
          _scheduleReconnect(url);
        },
        onError: (err) {
          isConnected.value = false;
          debugPrint('[WebSocketService] Error: $err');
          _scheduleReconnect(url);
        },
        cancelOnError: true,
      );
    } catch (e) {
      isConnected.value = false;
      _scheduleReconnect(url);
    }
  }

  void _scheduleReconnect(String url) {
    if (_isDisposed) return;
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(const Duration(seconds: 5), () {
      debugPrint('[WebSocketService] Attempting to reconnect...');
      connect(wsUrl: url);
    });
  }

  void disconnect() {
    _isDisposed = true;
    _reconnectTimer?.cancel();
    _channel?.sink.close();
    isConnected.value = false;
  }
}
