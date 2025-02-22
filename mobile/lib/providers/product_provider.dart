import 'package:flutter/foundation.dart';
import '../models/product.dart';
import '../services/api_service.dart';

class ProductProvider with ChangeNotifier {
  final ApiService _apiService;
  List<Product> _products = [];
  bool _isLoading = false;
  String? _error;

  ProductProvider(this._apiService);

  List<Product> get products => _products;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadProducts({String? search, String? category}) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      _products = await _apiService.getProducts(
        search: search,
        category: category,
      );
      
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<Product?> getProductDetails(String productId) async {
    try {
      return await _apiService.getProductDetails(productId);
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return null;
    }
  }
}
