import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/user.dart';
import '../models/product.dart';
import '../models/wallet.dart';

class ApiService {
  final String baseUrl;
  final http.Client client;
  String? _authToken;

  ApiService({
    required this.baseUrl,
    http.Client? client,
  }) : client = client ?? http.Client();

  Future<String> login(String username, String password, String pin) async {
    final response = await client.post(
      Uri.parse('$baseUrl/api/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'username': username,
        'password': password,
        'pin': pin,
      }),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      _authToken = data['token'];
      return _authToken!;
    } else {
      throw Exception('Failed to login');
    }
  }

  Future<User> getCurrentUser() async {
    final response = await _authenticatedGet('/api/user/me');
    return User.fromJson(json.decode(response.body));
  }

  Future<List<Product>> getProducts({
    String? category,
    String? search,
    int page = 1,
  }) async {
    final queryParams = {
      if (category != null) 'category': category,
      if (search != null) 'search': search,
      'page': page.toString(),
    };

    final response = await _authenticatedGet(
      '/api/products',
      queryParams: queryParams,
    );

    final List<dynamic> data = json.decode(response.body);
    return data.map((json) => Product.fromJson(json)).toList();
  }

  Future<Wallet> getWallet(String currency) async {
    final response = await _authenticatedGet('/api/wallet/$currency');
    return Wallet.fromJson(json.decode(response.body));
  }

  Future<String> generateDepositAddress(String currency) async {
    final response = await _authenticatedPost(
      '/api/wallet/$currency/deposit-address',
    );
    final data = json.decode(response.body);
    return data['address'];
  }

  Future<void> withdraw({
    required String currency,
    required double amount,
    required String address,
  }) async {
    await _authenticatedPost(
      '/api/wallet/$currency/withdraw',
      body: {
        'amount': amount,
        'address': address,
      },
    );
  }

  Future<http.Response> _authenticatedGet(
    String path, {
    Map<String, String>? queryParams,
  }) async {
    if (_authToken == null) {
      throw Exception('Not authenticated');
    }

    final uri = Uri.parse(baseUrl + path).replace(
      queryParameters: queryParams,
    );

    return await client.get(
      uri,
      headers: {
        'Authorization': 'Bearer $_authToken',
        'Content-Type': 'application/json',
      },
    );
  }

  Future<http.Response> _authenticatedPost(
    String path, {
    Map<String, dynamic>? body,
  }) async {
    if (_authToken == null) {
      throw Exception('Not authenticated');
    }

    return await client.post(
      Uri.parse(baseUrl + path),
      headers: {
        'Authorization': 'Bearer $_authToken',
        'Content-Type': 'application/json',
      },
      body: body != null ? json.encode(body) : null,
    );
  }
}
