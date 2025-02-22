from django.db import transaction
from django.utils import timezone
from django.conf import settings
from typing import Dict, Any, Optional
from ..models.user_profile import UserProfile
from ..models.order import DeliveryOrder
from ..models.driver_tracking import DriverLocation, DeliveryStatus
from ..models.wallet import UserWallet

class DataSynchronizationService:
    """Service for ensuring data consistency across platforms"""
    
    @classmethod
    def sync_user_preferences(cls, user_id: int) -> Dict[str, Any]:
        """Synchronize user preferences across platforms"""
        profile = UserProfile.objects.get(user_id=user_id)
        
        return {
            'currency': profile.preferred_currency,
            'country': profile.country,
            'language': profile.language,
            'public_username': profile.public_username,
            'pgp_verified': profile.pgp_verified,
            'last_active': profile.last_active.isoformat() if profile.last_active else None
        }
    
    @classmethod
    def sync_order_status(cls, order_id: int) -> Dict[str, Any]:
        """Synchronize order status across platforms"""
        order = DeliveryOrder.objects.select_related(
            'driver_location'
        ).prefetch_related(
            'status_updates'
        ).get(id=order_id)
        
        return {
            'status': order.status,
            'tracking_enabled': order.tracking_enabled,
            'driver_location': {
                'latitude': float(order.driver_location.latitude),
                'longitude': float(order.driver_location.longitude),
                'last_update': order.driver_location.last_update.isoformat()
            } if order.driver_location else None,
            'status_updates': [
                {
                    'status': update.status,
                    'notes': update.notes,
                    'created_at': update.created_at.isoformat()
                }
                for update in order.status_updates.all()
            ]
        }
    
    @classmethod
    def sync_wallet_balance(cls, user_id: int) -> Dict[str, Any]:
        """Synchronize wallet balance across platforms"""
        wallet = UserWallet.objects.get(user_id=user_id)
        
        return {
            'btc_balance': str(wallet.btc_balance),
            'xmr_balance': str(wallet.xmr_balance),
            'usdt_balance': str(wallet.usdt_balance),
            'last_updated': wallet.updated_at.isoformat()
        }
    
    @classmethod
    @transaction.atomic
    def sync_all_user_data(cls, user_id: int) -> Dict[str, Any]:
        """Synchronize all user data across platforms"""
        return {
            'preferences': cls.sync_user_preferences(user_id),
            'wallet': cls.sync_wallet_balance(user_id),
            'orders': [
                cls.sync_order_status(order.id)
                for order in DeliveryOrder.objects.filter(user_id=user_id)
            ]
        }
