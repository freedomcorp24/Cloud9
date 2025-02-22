import 'package:flutter/material.dart';
import '../../models/product.dart';
import '../../services/api_service.dart';
import 'package:provider/provider.dart';
import '../../providers/product_provider.dart';

class ProductDetailScreen extends StatefulWidget {
  final String productId;

  const ProductDetailScreen({Key? key, required this.productId}) : super(key: key);

  @override
  _ProductDetailScreenState createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends State<ProductDetailScreen> {
  late Future<Product?> _productFuture;

  @override
  void initState() {
    super.initState();
    _productFuture = Provider.of<ProductProvider>(context, listen: false)
        .getProductDetails(widget.productId);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Product Details'),
      ),
      body: FutureBuilder<Product?>(
        future: _productFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return Center(child: CircularProgressIndicator());
          }
          
          if (snapshot.hasError) {
            return Center(
              child: Text('Error loading product: ${snapshot.error}'),
            );
          }
          
          final product = snapshot.data;
          if (product == null) {
            return Center(child: Text('Product not found'));
          }
          
          return SingleChildScrollView(
            child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (product.images.isNotEmpty)
              SizedBox(
                height: 300,
                child: PageView.builder(
                  itemCount: product.images.length,
                  itemBuilder: (context, index) {
                    return Image.network(
                      product.images[index],
                      fit: BoxFit.cover,
                    );
                  },
                ),
              ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    product.title,
                    style: Theme.of(context).textTheme.headlineMedium,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${product.price} USD',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          color: Theme.of(context).colorScheme.primary,
                        ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Description',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  Text(product.description),
                  const SizedBox(height: 16),
                  Text(
                    'Payment Methods',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    children: [
                      if (product.acceptBtc)
                        Chip(label: Text('BTC')),
                      if (product.acceptXmr)
                        Chip(label: Text('XMR')),
                      if (product.acceptUsdt)
                        Chip(label: Text('USDT')),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Shipping',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  ListView.builder(
                    shrinkWrap: true,
                    physics: NeverScrollableScrollPhysics(),
                    itemCount: product.postageOptions.length,
                    itemBuilder: (context, index) {
                      final option = product.postageOptions[index];
                      return ListTile(
                        title: Text(option['name']),
                        subtitle: Text(option['description'] ?? ''),
                        trailing: Text('${option['price']} USD'),
                      );
                    },
                  ),
                  const SizedBox(height: 24),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () {
                        // TODO: Implement purchase flow
                      },
                      child: const Text('Purchase'),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ));
        },
      ),
    );
  }
}
