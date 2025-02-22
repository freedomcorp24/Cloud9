import 'package:json_annotation/json_annotation.dart';

part 'wallet.g.dart';

@JsonSerializable()
class Wallet {
  final String id;
  final String currency;
  final double balance;
  final List<Transaction> transactions;
  final String? depositAddress;
  final DateTime? depositAddressExpiry;

  Wallet({
    required this.id,
    required this.currency,
    required this.balance,
    required this.transactions,
    this.depositAddress,
    this.depositAddressExpiry,
  });

  factory Wallet.fromJson(Map<String, dynamic> json) => _$WalletFromJson(json);
  Map<String, dynamic> toJson() => _$WalletToJson(this);
}

@JsonSerializable()
class Transaction {
  final String id;
  final String type;
  final double amount;
  final String currency;
  final String status;
  final DateTime timestamp;
  final String? txHash;
  final int? confirmations;

  Transaction({
    required this.id,
    required this.type,
    required this.amount,
    required this.currency,
    required this.status,
    required this.timestamp,
    this.txHash,
    this.confirmations,
  });

  factory Transaction.fromJson(Map<String, dynamic> json) => _$TransactionFromJson(json);
  Map<String, dynamic> toJson() => _$TransactionToJson(this);
}
