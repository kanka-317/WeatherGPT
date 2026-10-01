import 'package:flutter/material.dart';
import '../core/constants.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';

class AuthScreen extends StatefulWidget {
  final ValueChanged<UserModel> onAuthSuccess;

  const AuthScreen({super.key, required this.onAuthSuccess});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final ApiService _apiService = ApiService();
  bool _isSignUp = false;
  bool _isLoading = false;
  String? _errorMessage;

  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _nameController = TextEditingController();
  String _selectedRole = 'citizen';

  Future<void> _submit() async {
    final email = _emailController.text.trim();
    final password = _passwordController.text.trim();
    final name = _nameController.text.trim();

    if (email.isEmpty || password.isEmpty || (_isSignUp && name.isEmpty)) {
      setState(() => _errorMessage = 'Please complete all required fields.');
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      UserModel user;
      if (_isSignUp) {
        user = await _apiService.signUp(
          email: email,
          password: password,
          fullName: name,
          role: _selectedRole,
        );
      } else {
        user = await _apiService.signIn(
          email: email,
          password: password,
        );
      }

      widget.onAuthSuccess(user);
      if (mounted) Navigator.pop(context);
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString().replaceAll('Exception:', '').trim();
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text(
          _isSignUp ? 'Create WeatherGPT Account' : 'Sign In to WeatherGPT',
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
        ),
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: AppColors.surfaceCard,
              borderRadius: BorderRadius.circular(24),
              border: Border.all(color: AppColors.surfaceBorder),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Center(
                  child: CircleAvatar(
                    radius: 30,
                    backgroundColor: AppColors.primaryCyan.withOpacity(0.15),
                    child: const Icon(Icons.cloud_sync_rounded, color: AppColors.primaryCyan, size: 32),
                  ),
                ),
                const SizedBox(height: 16),
                Center(
                  child: Text(
                    _isSignUp ? 'Join WeatherGPT Network' : 'Welcome Back',
                    style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                  ),
                ),
                const SizedBox(height: 6),
                const Center(
                  child: Text(
                    'Access personalized advisory, risk maps & disaster alerts',
                    style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                    textAlign: TextAlign.center,
                  ),
                ),
                const SizedBox(height: 20),

                if (_errorMessage != null) ...[
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: AppColors.dangerRed.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: AppColors.dangerRed),
                    ),
                    child: Text(_errorMessage!, style: const TextStyle(color: AppColors.dangerRed, fontSize: 12)),
                  ),
                  const SizedBox(height: 14),
                ],

                if (_isSignUp) ...[
                  TextField(
                    controller: _nameController,
                    style: const TextStyle(color: AppColors.textPrimary),
                    decoration: _inputDeco('Full Name', Icons.person_outline),
                  ),
                  const SizedBox(height: 14),
                  DropdownButtonFormField<String>(
                    value: _selectedRole,
                    dropdownColor: AppColors.surfaceElevated,
                    style: const TextStyle(color: AppColors.textPrimary),
                    decoration: _inputDeco('Persona Role', Icons.badge_outlined),
                    items: const [
                      DropdownMenuItem(value: 'citizen', child: Text('Citizen (Daily Forecasts)')),
                      DropdownMenuItem(value: 'farmer', child: Text('Farmer / Krishi (Crop Advisory)')),
                      DropdownMenuItem(value: 'fisherman', child: Text('Fisherman (Maritime Safety)')),
                      DropdownMenuItem(value: 'disaster_manager', child: Text('Disaster Manager (War Room)')),
                    ],
                    onChanged: (val) {
                      if (val != null) setState(() => _selectedRole = val);
                    },
                  ),
                  const SizedBox(height: 14),
                ],

                TextField(
                  controller: _emailController,
                  style: const TextStyle(color: AppColors.textPrimary),
                  keyboardType: TextInputType.emailAddress,
                  decoration: _inputDeco('Email Address', Icons.email_outlined),
                ),
                const SizedBox(height: 14),

                TextField(
                  controller: _passwordController,
                  obscureText: true,
                  style: const TextStyle(color: AppColors.textPrimary),
                  decoration: _inputDeco('Password', Icons.lock_outline),
                ),
                const SizedBox(height: 20),

                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primaryCyan,
                    foregroundColor: Colors.black,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  onPressed: _isLoading ? null : _submit,
                  child: _isLoading
                      ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black))
                      : Text(_isSignUp ? 'Create Account' : 'Sign In', style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                ),

                const SizedBox(height: 14),

                TextButton(
                  onPressed: () {
                    setState(() {
                      _isSignUp = !_isSignUp;
                      _errorMessage = null;
                    });
                  },
                  child: Text(
                    _isSignUp ? 'Already have an account? Sign In' : 'New to WeatherGPT? Create Account',
                    style: const TextStyle(color: AppColors.primaryCyan, fontSize: 13),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  InputDecoration _inputDeco(String hint, IconData icon) {
    return InputDecoration(
      labelText: hint,
      labelStyle: const TextStyle(color: AppColors.textMuted, fontSize: 13),
      prefixIcon: Icon(icon, size: 20, color: AppColors.primaryCyan),
      filled: true,
      fillColor: AppColors.background,
      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: AppColors.surfaceBorder)),
      enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: AppColors.surfaceBorder)),
      focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: AppColors.primaryCyan)),
    );
  }
}
