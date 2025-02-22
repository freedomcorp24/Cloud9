from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
import re
from django.core.validators import MinLengthValidator, RegexValidator
from datetime import timedelta
from ..services.pgp import PGPService

def validate_username(value):
    """Validate username format"""
    if not re.match(r'^[a-zA-Z0-9_-]{3,30}$', value):
        raise ValidationError(
            _('Username must be 3-30 characters and contain only letters, numbers, underscores and hyphens')
        )

class UserProfile(models.Model):
    """
    User profile model for marketplace with dual username system and enhanced security features
    including PGP-based 2FA and transaction PIN protection.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_profile'
    )
    
    # Dual username system
    public_username = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            MinLengthValidator(3),
            RegexValidator(
                regex=r'^[a-zA-Z0-9_-]+$',
                message='Username can only contain letters, numbers, underscores and hyphens'
            )
        ],
        help_text=_('Public username visible to other users')
    )
    private_username = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            MinLengthValidator(8),
            RegexValidator(
                regex=r'^[a-zA-Z0-9_-]+$',
                message='Username can only contain letters, numbers, underscores and hyphens'
            )
        ],
        help_text=_('Private username used for login')
    )
    
    # PGP authentication
    pgp_key = models.TextField(
        blank=True,
        help_text=_('PGP public key for 2FA and secure communications')
    )
    pgp_verified = models.BooleanField(
        default=False,
        help_text=_('Indicates if PGP key ownership has been verified')
    )
    pgp_verification_code = models.CharField(
        max_length=64,
        blank=True,
        help_text=_('Temporary code for PGP key verification')
    )
    pgp_verification_expires = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Expiration time for PGP verification code')
    )
    
    # Transaction security
    transaction_pin = models.CharField(
        max_length=6,
        validators=[
            MinLengthValidator(6),
            RegexValidator(
                regex=r'^\d{6}$',
                message='PIN must be exactly 6 digits'
            )
        ],
        help_text=_('6-digit PIN required for financial operations')
    )
    pin_last_changed = models.DateTimeField(
        null=True,
        help_text=_('Timestamp of last PIN change')
    )
    failed_pin_attempts = models.PositiveIntegerField(
        default=0,
        help_text=_('Count of consecutive failed PIN attempts')
    )
    pin_locked_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Timestamp until PIN entry is locked')
    )
    
    # Activity tracking
    last_active = models.DateTimeField(
        auto_now=True,
        help_text=_('Last activity timestamp')
    )
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text=_('IP address of last login')
    )
    
    # Preferences
    preferred_currency = models.CharField(
        max_length=4,
        choices=[
            ('USD', 'US Dollar'),
            ('EUR', 'Euro'),
            ('GBP', 'British Pound'),
            ('BTC', 'Bitcoin'),
            ('XMR', 'Monero'),
            ('USDT', 'Tether')
        ],
        default='USD'
    )
    country = models.CharField(
        max_length=2,
        choices=[
            ('US', 'United States'),
            ('GB', 'United Kingdom'),
            ('EU', 'European Union'),
            ('CA', 'Canada'),
            ('AU', 'Australia')
        ],
        blank=True
    )
    
    class Meta:
        app_label = 'marketplace'
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
        
    def get_online_status(self):
        """Return user's online status in broad time buckets"""
        if not self.last_active:
            return 'never'
            
        now = timezone.now()
        delta = now - self.last_active
        
        if delta < timedelta(minutes=15):
            return 'recently'
        elif delta < timedelta(hours=24):
            return 'today'
        elif delta < timedelta(days=7):
            return 'this week'
        else:
            return 'long ago'
            
    def verify_pin(self, pin):
        """Verify transaction PIN with security measures"""
        if self.pin_locked_until and timezone.now() < self.pin_locked_until:
            return False
            
        if self.transaction_pin != pin:
            self.failed_pin_attempts += 1
            if self.failed_pin_attempts >= 3:
                self.pin_locked_until = timezone.now() + timedelta(minutes=30)
            self.save()
            return False
            
        self.failed_pin_attempts = 0
        self.save()
        return True
        
    def start_pgp_verification(self):
        """Start PGP key verification process"""
        pgp_service = PGPService()
        code = pgp_service.generate_verification_code()
        success, encrypted_message = pgp_service.encrypt_verification_message(
            self.pgp_key,
            code
        )
        
        if success:
            self.pgp_verification_code = code
            self.pgp_verification_expires = timezone.now() + timedelta(hours=24)
            self.save()
            return encrypted_message
            
        return None
