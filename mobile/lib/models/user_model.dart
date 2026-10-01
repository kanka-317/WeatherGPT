class UserModel {
  final int? id;
  final String email;
  final String fullName;
  final String role; // 'citizen' | 'farmer' | 'fisherman' | 'disaster_manager'
  final String? institution;
  final String? token;

  UserModel({
    this.id,
    required this.email,
    required this.fullName,
    required this.role,
    this.institution,
    this.token,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as int?,
      email: json['email'] ?? '',
      fullName: json['full_name'] ?? json['username'] ?? 'User',
      role: (json['role'] ?? 'citizen').toString().toLowerCase(),
      institution: json['institution'],
      token: json['token'] ?? json['access_token'],
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'email': email,
    'full_name': fullName,
    'role': role,
    'institution': institution,
    'token': token,
  };
}
