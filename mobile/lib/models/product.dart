import 'package:json_annotation/json_annotation.dart';

part 'product.g.dart';

@JsonSerializable()
class Product {
  final String id;
  final String title;
  final String description;
  final String vendor;
  final String category;
  final String originCountry;
  final double price;
  final List<String> images;
  final bool escrowEnabled;
  final bool feEnabled;
  final bool acceptBtc;
  final bool acceptXmr;
  final bool acceptUsdt;
  final String refundPolicy;
  final List<String> tags;
  final String? autoMessage;
  final bool unlimitedQuantity;
  final Map<String, dynamic>? bulkPricing;
  final List<String> shipsTo;
  final List<Map<String, dynamic>> postageOptions;
  final String visibility;
  final bool restrictBuyers;
  final int cancelHours;
  final int autoCancelHours;
  final int autoFinalizeDays;

  Product({
    required this.id,
    required this.title,
    required this.description,
    required this.vendor,
    required this.category,
    required this.originCountry,
    required this.price,
    required this.images,
    required this.escrowEnabled,
    required this.feEnabled,
    required this.acceptBtc,
    required this.acceptXmr,
    required this.acceptUsdt,
    required this.refundPolicy,
    required this.tags,
    this.autoMessage,
    required this.unlimitedQuantity,
    this.bulkPricing,
    required this.shipsTo,
    required this.postageOptions,
    required this.visibility,
    required this.restrictBuyers,
    required this.cancelHours,
    required this.autoCancelHours,
    required this.autoFinalizeDays,
  });

  factory Product.fromJson(Map<String, dynamic> json) => _$ProductFromJson(json);
  Map<String, dynamic> toJson() => _$ProductToJson(this);
}
