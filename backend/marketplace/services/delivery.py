from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from ..models.order import DeliveryOrder, DeliveryTracking
import math

class DeliveryService:
    """
    Service for managing delivery operations
    """
    def __init__(self, order: DeliveryOrder):
        self.order = order
    
    def calculate_delivery_time(self) -> timezone.datetime:
        """Calculate estimated delivery time based on type and distance"""
        if self.order.delivery_type == 'instant':
            return timezone.now() + timedelta(hours=1)
        elif self.order.delivery_type == 'mail':
            return timezone.now() + timedelta(days=3)
        return timezone.now() + timedelta(hours=2)  # pickup
    
    def calculate_delivery_fee(self) -> float:
        """Calculate delivery fee based on type and distance"""
        base_fee = self.order.product.delivery_fee
        if self.order.delivery_type == 'instant':
            return float(base_fee) * 1.5  # 50% premium for instant
        elif self.order.delivery_type == 'mail':
            return float(base_fee)
        return float(base_fee) * 0.5  # 50% discount for pickup
    
    def update_tracking(self, latitude: float, longitude: float, status: str):
        """Update delivery tracking information"""
        DeliveryTracking.objects.create(
            order=self.order,
            latitude=latitude,
            longitude=longitude,
            status_update=status
        )
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon/2) * math.sin(delta_lon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def is_within_delivery_range(self, customer_lat: float, customer_lon: float,
                               vendor_lat: float, vendor_lon: float) -> bool:
        """Check if delivery address is within vendor's delivery range"""
        distance = self.calculate_distance(
            customer_lat, customer_lon,
            vendor_lat, vendor_lon
        )
        return distance <= float(self.order.product.max_delivery_distance)
