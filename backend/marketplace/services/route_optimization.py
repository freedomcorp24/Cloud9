from django.db import models
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from decimal import Decimal
import math
from typing import List, Dict, Tuple
from ..models.order import DeliveryOrder
from ..models.driver_tracking import DriverLocation

class RouteOptimizationService:
    """Service for optimizing delivery routes"""
    
    @staticmethod
    def calculate_distance(lat1: Decimal, lon1: Decimal, lat2: Decimal, lon2: Decimal) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(float(lat2 - lat1))
        dlon = math.radians(float(lon2 - lon1))
        lat1 = math.radians(float(lat1))
        lat2 = math.radians(float(lat2))
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c
    
    @classmethod
    def get_optimal_route(cls, driver_location: DriverLocation, orders: List[DeliveryOrder]) -> List[DeliveryOrder]:
        """Get optimal route for given orders using nearest neighbor algorithm"""
        if not orders:
            return []
            
        # Start from driver location
        current_lat = driver_location.latitude
        current_lon = driver_location.longitude
        
        unvisited = orders.copy()
        route = []
        
        while unvisited:
            # Find nearest unvisited order
            nearest = min(
                unvisited,
                key=lambda o: cls.calculate_distance(
                    current_lat,
                    current_lon,
                    o.delivery_latitude,
                    o.delivery_longitude
                )
            )
            
            route.append(nearest)
            unvisited.remove(nearest)
            
            # Update current position
            current_lat = nearest.delivery_latitude
            current_lon = nearest.delivery_longitude
            
        return route
    
    @classmethod
    def validate_timeframes(cls, orders: List[DeliveryOrder]) -> Dict[str, List[str]]:
        """Validate order timeframes"""
        now = timezone.now()
        violations = {
            'early_completion': [],
            'late_delivery': []
        }
        
        for order in orders:
            # Check mail/pickup minimum timeframe
            if order.delivery_type in ['mail', 'pickup']:
                min_completion = order.date_placed + timedelta(days=DeliveryOrder.MAIL_PICKUP_MIN_DAYS)
                if order.status == 'completed' and order.actual_delivery < min_completion:
                    violations['early_completion'].append(
                        f"Order {order.id} completed before minimum timeframe"
                    )
            
            # Check instant delivery maximum timeframe
            elif order.delivery_type == 'instant':
                max_delivery = order.date_placed + timedelta(hours=DeliveryOrder.INSTANT_DELIVERY_MAX_HOURS)
                if order.status not in ['completed', 'cancelled', 'disputed'] and now > max_delivery:
                    violations['late_delivery'].append(
                        f"Order {order.id} not completed within maximum timeframe"
                    )
                    
        return violations
    
    @classmethod
    def estimate_delivery_time(cls, route: List[DeliveryOrder], avg_speed: float = 30.0) -> Dict[int, timedelta]:
        """Estimate delivery times for orders in route"""
        if not route:
            return {}
            
        estimates = {}
        current_time = timezone.now()
        
        # Start from first order's pickup location
        current_lat = route[0].pickup_latitude
        current_lon = route[0].pickup_longitude
        
        for order in route:
            # Calculate distance and time to delivery location
            distance = cls.calculate_distance(
                current_lat,
                current_lon,
                order.delivery_latitude,
                order.delivery_longitude
            )
            
            # Estimate time based on distance and average speed
            travel_time = distance / avg_speed  # hours
            estimates[order.id] = timedelta(hours=travel_time)
            
            # Update current position
            current_lat = order.delivery_latitude
            current_lon = order.delivery_longitude
            
        return estimates
