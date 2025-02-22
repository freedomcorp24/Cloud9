from django.utils import timezone
from django.conf import settings
from django.utils.translation import get_language
from typing import Dict, Any, Optional
from datetime import timedelta
from ..models.user_profile import UserProfile
from ..services.synchronization import DataSynchronizationService

class UserExperienceService:
    """Service for maintaining consistent user experience across platforms"""
    
    @staticmethod
    def get_online_status(last_active: Optional[timezone.datetime]) -> str:
        """Get user's online status in broad time buckets"""
        if not last_active:
            return 'never'
            
        now = timezone.now()
        delta = now - last_active
        
        if delta < timedelta(minutes=15):
            return 'recently'
        elif delta < timedelta(hours=24):
            return 'today'
        elif delta < timedelta(days=7):
            return 'this week'
        else:
            return 'long ago'
    
    @classmethod
    def get_user_preferences(cls, user_id: int) -> Dict[str, Any]:
        """Get user preferences for UI customization"""
        return DataSynchronizationService.sync_user_preferences(user_id)
    
    @classmethod
    def get_display_currency(cls, user_id: int) -> str:
        """Get user's preferred display currency"""
        profile = UserProfile.objects.get(user_id=user_id)
        return profile.preferred_currency
    
    @classmethod
    def get_interface_language(cls, request) -> str:
        """Get user's interface language"""
        if request.user.is_authenticated:
            profile = request.user.user_profile
            if profile.language:
                return profile.language
        return get_language()
    
    @classmethod
    def get_platform_specific_features(cls, request) -> Dict[str, bool]:
        """Get available features based on platform"""
        is_tor = getattr(request, 'is_tor', False)
        is_mobile = getattr(request, 'is_mobile', False)
        
        return {
            'map_view': not is_tor,  # No maps in Tor version
            'real_time_updates': not is_tor,  # No WebSocket in Tor version
            'location_tracking': is_mobile,  # Only in mobile app
            'push_notifications': is_mobile,  # Only in mobile app
        }
    
    @classmethod
    def get_ui_configuration(cls, request) -> Dict[str, Any]:
        """Get UI configuration based on user preferences and platform"""
        config = {
            'theme': 'dark',  # Default theme
            'layout': 'list',  # Default layout
            'currency_position': 'before',  # Default currency position
            'date_format': 'relative',  # Use relative dates for privacy
        }
        
        if request.user.is_authenticated:
            profile = request.user.user_profile
            user_config = profile.ui_preferences or {}
            config.update(user_config)
            
        # Platform-specific overrides
        if getattr(request, 'is_tor', False):
            config.update({
                'javascript_enabled': False,
                'animations_enabled': False,
                'image_loading': 'lazy',
            })
            
        return config
