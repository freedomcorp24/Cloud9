from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from typing import Optional, Dict, Any, Tuple
from ..models.user_profile import UserProfile
from ..services.pgp import PGPService

User = get_user_model()

class AuthenticationService:
    """Service for handling authentication across platforms"""
    
    @classmethod
    def authenticate_user(cls, private_username: str, password: str) -> Optional[User]:
        """Authenticate user with private username"""
        try:
            profile = UserProfile.objects.get(private_username=private_username)
            user = profile.user
            
            if user.check_password(password):
                # Update last login
                user.last_login = timezone.now()
                user.save()
                return user
                
        except UserProfile.DoesNotExist:
            pass
            
        return None
    
    @classmethod
    def verify_pgp(cls, user: User, verification_code: str) -> bool:
        """Verify PGP key ownership"""
        profile = user.user_profile
        
        if not profile.pgp_verification_code:
            return False
            
        if profile.pgp_verification_expires and timezone.now() > profile.pgp_verification_expires:
            return False
            
        if profile.pgp_verification_code != verification_code:
            return False
            
        profile.pgp_verified = True
        profile.pgp_verification_code = ''
        profile.pgp_verification_expires = None
        profile.save()
        
        return True
    
    @classmethod
    def start_pgp_verification(cls, user: User) -> Optional[str]:
        """Start PGP verification process"""
        profile = user.user_profile
        
        if not profile.pgp_key:
            raise ValidationError(_('No PGP key provided'))
            
        return profile.start_pgp_verification()
    
    @classmethod
    def verify_transaction_pin(cls, user: User, pin: str) -> bool:
        """Verify transaction PIN"""
        profile = user.user_profile
        return profile.verify_pin(pin)
    
    @classmethod
    def requires_pgp_verification(cls, user: User) -> bool:
        """Check if user requires PGP verification"""
        profile = user.user_profile
        return bool(profile.pgp_key and not profile.pgp_verified)
    
    @classmethod
    def requires_pin_verification(cls, user: User, action: str) -> bool:
        """Check if action requires PIN verification"""
        PROTECTED_ACTIONS = {
            'purchase': True,
            'withdraw': True,
            'release_funds': True,
            'change_security': True
        }
        return PROTECTED_ACTIONS.get(action, False)
    
    @classmethod
    def get_auth_status(cls, user: User) -> Dict[str, Any]:
        """Get user's authentication status"""
        profile = user.user_profile
        
        return {
            'username': profile.public_username,
            'pgp_enabled': bool(profile.pgp_key),
            'pgp_verified': profile.pgp_verified,
            'pin_set': bool(profile.transaction_pin),
            'pin_locked': bool(profile.pin_locked_until and timezone.now() < profile.pin_locked_until),
            'last_active': profile.last_active.isoformat() if profile.last_active else None
        }
