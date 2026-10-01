import 'package:flutter/material.dart';
import '../core/constants.dart';
import '../services/api_service.dart';

class WakingServerIndicator extends StatelessWidget {
  const WakingServerIndicator({super.key});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<bool>(
      valueListenable: ApiService().isWakingServer,
      builder: (context, isWaking, child) {
        if (!isWaking) return const SizedBox.shrink();

        return Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          color: AppColors.warningAmber.withOpacity(0.9),
          child: const Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              SizedBox(
                width: 14,
                height: 14,
                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black),
              ),
              SizedBox(width: 10),
              Text(
                'Waking up backend server on Render cloud... Please wait',
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.black),
              ),
            ],
          ),
        );
      },
    );
  }
}
