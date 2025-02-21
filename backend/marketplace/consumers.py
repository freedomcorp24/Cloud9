from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils.translation import gettext_lazy as _
from .models import LiveDeliveryTracking, DeliveryLocation

class LocationConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for handling delivery location updates"""
    
    async def connect(self):
        """Handle new WebSocket connection"""
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        await self.channel_layer.group_add(
            f"order_{self.order_id}",
            self.channel_name
        )
        await self.accept()
        
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            f"order_{self.order_id}",
            self.channel_name
        )
        
    async def receive_json(self, content):
        """Handle incoming WebSocket messages"""
        message_type = content.get('type')
        
        if message_type == 'location_update':
            # Handle real-time GPS updates
            await self.update_location(
                content.get('latitude'),
                content.get('longitude')
            )
        elif message_type == 'status_update':
            # Handle manual status updates
            await self.update_status(content.get('status'))
            
    @database_sync_to_async
    def update_location(self, lat, lng):
        """Update driver location in database"""
        if not all([lat, lng]):
            return
            
        tracking = LiveDeliveryTracking.objects.get(order_id=self.order_id)
        if tracking.tracking_mode == 'realtime':
            # Update current location
            tracking.current_latitude = lat
            tracking.current_longitude = lng
            tracking.save()
            
            # Store in location history
            DeliveryLocation.objects.create(
                tracking=tracking,
                latitude=lat,
                longitude=lng
            )
            
    @database_sync_to_async
    def update_status(self, status):
        """Update delivery status manually"""
        if not status:
            return
            
        tracking = LiveDeliveryTracking.objects.get(order_id=self.order_id)
        if tracking.tracking_mode == 'manual':
            if status in ['on_way', 'close', 'arrived']:
                tracking.order.set_status(
                    status,
                    notes=_('Driver marked as {}').format(status)
                )
                
    async def location_update(self, event):
        """Send location update to WebSocket"""
        await self.send_json(event)
        
    async def status_update(self, event):
        """Send status update to WebSocket"""
        await self.send_json(event)
