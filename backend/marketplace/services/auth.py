from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from ..models.user_profile import UserProfile

class TransactionPINService:
    """Service for handling transaction PIN operations"""
    MAX_ATTEMPTS = 3
    LOCKOUT_DURATION = timedelta(minutes=30)
    
    @staticmethod
    def verify_pin(user_profile: UserProfile, pin: str) -> bool:
        """Verify transaction PIN and handle lockouts"""
        # Check if PIN is locked
        if user_profile.pin_locked_until and user_profile.pin_locked_until > timezone.now():
            return False
            
        # Reset lockout if expired
        if user_profile.pin_locked_until and user_profile.pin_locked_until <= timezone.now():
            user_profile.pin_attempts = 0
            user_profile.pin_locked_until = None
            user_profile.save()
            
        # Verify PIN
        if user_profile.transaction_pin != pin:
            user_profile.pin_attempts += 1
            
            # Lock PIN if max attempts exceeded
            if user_profile.pin_attempts >= TransactionPINService.MAX_ATTEMPTS:
                user_profile.pin_locked_until = timezone.now() + TransactionPINService.LOCKOUT_DURATION
                
            user_profile.save()
            return False
            
        # Reset attempts on successful verification
        user_profile.pin_attempts = 0
        user_profile.save()
        return True
        
    @staticmethod
    def set_pin(user_profile: UserProfile, new_pin: str) -> bool:
        """Set or update transaction PIN"""
        if not new_pin.isdigit() or len(new_pin) != 6:
            return False
            
        user_profile.transaction_pin = new_pin
        user_profile.pin_attempts = 0
        user_profile.pin_locked_until = None
        user_profile.save()
        return True
