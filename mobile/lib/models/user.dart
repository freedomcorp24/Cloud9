import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

@JsonSerializable()
class User {
  final String id;
  final String publicUsername;
  final String? pgpKey;
  final bool isTwoFactorEnabled;
  final String displayCurrency;
  final String language;
  final bool autoDetectLanguage;
  final bool autoDetectCurrency;

  User({
    required this.id,
    required this.publicUsername,
    this.pgpKey,
    required this.isTwoFactorEnabled,
    required this.displayCurrency,
    required this.language,
    required this.autoDetectLanguage,
    required this.autoDetectCurrency,
  });

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  Map<String, dynamic> toJson() => _$UserToJson(this);
}
