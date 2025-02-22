import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/api_service.dart';
import 'providers/theme_provider.dart';
import 'screens/product/product_list_screen.dart';
import 'screens/wallet/wallet_screen.dart';
import 'screens/order/order_tracking_screen.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => ThemeProvider(),
        ),
        Provider(
          create: (_) => ApiService(
            baseUrl: const String.fromEnvironment('API_BASE_URL',
                defaultValue: 'http://localhost:8000'),
          ),
        ),
        ChangeNotifierProxyProvider<ApiService, ProductProvider>(
          create: (context) => ProductProvider(
            Provider.of<ApiService>(context, listen: false),
          ),
          update: (context, apiService, previous) =>
              previous ?? ProductProvider(apiService),
        ),
      ],
      child: const Cloud9App(),
    ),
  );
}

class Cloud9App extends StatelessWidget {
  const Cloud9App({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        return MaterialApp(
          title: 'Cloud9 Marketplace',
          theme: ThemeData.light(useMaterial3: true),
          darkTheme: ThemeData.dark(useMaterial3: true),
          themeMode: themeProvider.themeMode,
          initialRoute: '/',
          routes: {
            '/': (context) => const MainScreen(),
            '/product/list': (context) => ProductListScreen(),
            '/product/detail': (context) {
              final productId = ModalRoute.of(context)!.settings.arguments as String;
              return ProductDetailScreen(productId: productId);
            },
            '/wallet': (context) => WalletScreen(),
            '/orders/tracking': (context) => OrderTrackingScreen(),
          },
        );
      },
    );
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({Key? key}) : super(key: key);

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;

  final List<Widget> _screens = [
    ProductListScreen(),
    WalletScreen(),
    OrderTrackingScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _selectedIndex,
        children: _screens,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.store),
            label: 'Products',
          ),
          NavigationDestination(
            icon: Icon(Icons.account_balance_wallet),
            label: 'Wallet',
          ),
          NavigationDestination(
            icon: Icon(Icons.local_shipping),
            label: 'Orders',
          ),
        ],
      ),
    );
  }
}
