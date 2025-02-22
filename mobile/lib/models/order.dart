import 'package:json_annotation/json_annotation.dart';
import 'product.dart';

part 'order.g.dart';

@JsonSerializable()
class Order {
  final String id;
  final String status;
  final DateTime createdAt;
  final String buyerUsername;
  final String vendorUsername;
  final Product product;
  final double quantity;
  final String currency;
  final double amount;
  final String paymentStatus;
  final String? shippingAddress;
  final String? trackingNumber;
  final DateTime? estimatedDelivery;
  final Map<String, dynamic>? deliveryDetails;
  final bool isInstantDelivery;

  Order({
    required this.id,
    required this.status,
    required this.createdAt,
    required this.buyerUsername,
    required this.vendorUsername,
    required this.product,
    required this.quantity,
    required this.currency,
    required this.amount,
    required this.paymentStatus,
    this.shippingAddress,
    this.trackingNumber,
    this.estimatedDelivery,
    this.deliveryDetails,
    required this.isInstantDelivery,
  });

  factory Order.fromJson(Map<String, dynamic> json) => _$OrderFromJson(json);
  Map<String, dynamic> toJson() => _$OrderToJson(this);
}

@JsonSerializable()
class DeliveryUpdate {
  final String orderId;
  final String status;
  final DateTime timestamp;
  final Map<String, dynamic>? location;
  final String? message;

  DeliveryUpdate({
    required this.orderId,
    required this.status,
    required this.timestamp,
    this.location,
    this.message,
  });

  factory DeliveryUpdate.fromJson(Map<String, dynamic> json) =>
      _$DeliveryUpdateFromJson(json);
  Map<String, dynamic> toJson() => _$DeliveryUpdateToJson(this);
}
