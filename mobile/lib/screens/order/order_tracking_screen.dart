import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:provider/provider.dart';
import '../../services/api_service.dart';

class OrderTrackingScreen extends StatefulWidget {
  const OrderTrackingScreen({Key? key}) : super(key: key);

  @override
  State<OrderTrackingScreen> createState() => _OrderTrackingScreenState();
}

class _OrderTrackingScreenState extends State<OrderTrackingScreen> {
  GoogleMapController? _mapController;
  Set<Marker> _markers = {};
  bool _locationEnabled = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Order Tracking'),
      ),
      body: Column(
        children: [
          if (!_locationEnabled)
            Container(
              padding: const EdgeInsets.all(16),
              color: Theme.of(context).colorScheme.error,
              child: Row(
                children: [
                  const Icon(Icons.location_off),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Location services are disabled. Enable location to track your order.',
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.onError,
                      ),
                    ),
                  ),
                  TextButton(
                    onPressed: _requestLocationPermission,
                    child: Text(
                      'Enable',
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.onError,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          Expanded(
            child: GoogleMap(
              initialCameraPosition: const CameraPosition(
                target: LatLng(0, 0),
                zoom: 15,
              ),
              markers: _markers,
              onMapCreated: (controller) {
                _mapController = controller;
              },
              myLocationEnabled: _locationEnabled,
              myLocationButtonEnabled: _locationEnabled,
            ),
          ),
          Container(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Active Orders',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 8),
                Consumer<ApiService>(
                  builder: (context, apiService, child) {
                    return FutureBuilder(
                      future: null, // TODO: Implement getActiveOrders
                      builder: (context, snapshot) {
                        if (snapshot.connectionState == ConnectionState.waiting) {
                          return const Center(
                            child: CircularProgressIndicator(),
                          );
                        }

                        return const Text('No active orders');
                      },
                    );
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _requestLocationPermission() async {
    // TODO: Implement location permission request
    setState(() {
      _locationEnabled = true;
    });
  }
}
