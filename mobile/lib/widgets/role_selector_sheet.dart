import 'package:flutter/material.dart';
import '../core/constants.dart';
import '../core/storage.dart';

class RoleSelectorSheet extends StatelessWidget {
  final String currentRole;
  final ValueChanged<String> onRoleSelected;

  const RoleSelectorSheet({
    super.key,
    required this.currentRole,
    required this.onRoleSelected,
  });

  static void show(BuildContext context, {required String currentRole, required ValueChanged<String> onRoleSelected}) {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.surfaceCard,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => RoleSelectorSheet(
        currentRole: currentRole,
        onRoleSelected: onRoleSelected,
      ),
    );
  }

  IconData _getRoleIcon(String id) {
    switch (id) {
      case 'farmer':
        return Icons.agriculture_rounded;
      case 'fisherman':
        return Icons.sailing_rounded;
      case 'disaster_manager':
        return Icons.shield_rounded;
      default:
        return Icons.person_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: AppColors.surfaceBorder,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Select User Persona & Advisory Role',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
            ),
            const SizedBox(height: 4),
            const Text(
              'Personalizes AI advice, irrigation recommendations, and maritime warning thresholds.',
              style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
            ),
            const SizedBox(height: 16),
            ...AppConstants.userRoles.map((role) {
              final isSelected = role['id'] == currentRole;
              return Container(
                margin: const EdgeInsets.only(bottom: 8),
                decoration: BoxDecoration(
                  color: isSelected ? AppColors.primaryCyan.withValues(alpha: 0.12) : AppColors.surfaceElevated,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(
                    color: isSelected ? AppColors.primaryCyan : AppColors.surfaceBorder,
                    width: isSelected ? 1.5 : 1.0,
                  ),
                ),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: isSelected ? AppColors.primaryCyan : AppColors.background,
                    child: Icon(
                      _getRoleIcon(role['id']!),
                      color: isSelected ? Colors.black : AppColors.primaryCyan,
                      size: 20,
                    ),
                  ),
                  title: Text(
                    role['title']!,
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.bold,
                      color: isSelected ? AppColors.primaryCyan : AppColors.textPrimary,
                    ),
                  ),
                  subtitle: Text(
                    role['desc']!,
                    style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
                  ),
                  trailing: isSelected
                      ? const Icon(Icons.check_circle_rounded, color: AppColors.primaryCyan)
                      : null,
                  onTap: () {
                    LocalStorageService.setUserRole(role['id']!);
                    onRoleSelected(role['id']!);
                    Navigator.pop(context);
                  },
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}
