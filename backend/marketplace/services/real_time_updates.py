from django.db import models
from django.utils import timezone
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from typing import Dict, Any
from ..models.order import DeliveryOrder
from ..models.driver_tracking import DriverLocation, DeliveryStatus

class RealTimeUpdateService:
    """Service for handling real-time updates"""
    
    @classmethod
    def send_order_update(cls, order_id: int, update_type: str, data: Dict[str, Any]) -> None:
        """Send real-time update for order"""
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"order_{order_id}",
            {
                "type": "order.update",
                "update_type": update_type,
                "data": data
            }
        )
    
    @classmethod
    def send_location_update(cls, order_id: int, latitude: float, longitude: float) -> None:
        """Send real-time location update"""
        cls.send_order_update(
            order_id,
            "location_update",
            {
                "latitude": latitude,
                "longitude": longitude,
                "timestamp": timezone.now().isoformat()
            }
        )
    
    @classmethod
    def send_status_update(cls, order_id: int, status: str, notes: str = "") -> None:
        """Send real-time status update"""
        cls.send_order_update(
            order_id,
            "status_update",
            {
                "status": status,
                "notes": notes,
                "timestamp": timezone.now().isoformat()
            }
        )
    
    @classmethod
    def send_timeframe_update(cls, order_id: int, estimated_delivery: str) -> None:
        """Send real-time timeframe update"""
        cls.send_order_update(
            order_id,
            "timeframe_update",
            {
                "estimated_delivery": estimated_delivery,
                "timestamp": timezone.now().isoformat()
            }
        )
