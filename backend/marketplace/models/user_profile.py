from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from oscar.apps.customer.abstract_models import AbstractUser

class UserProfile(models.Model):
    """
    User profile model for marketplace
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_profile'
    )
    preferred_currency = models.CharField(
        max_length=4,  # Increased to accommodate 4-char currencies like 'USDT'
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
    pgp_key = models.TextField(blank=True)
    pgp_verified = models.BooleanField(default=False)
    transaction_pin = models.CharField(max_length=6, blank=True)
    pin_last_changed = models.DateTimeField(null=True)
    
    class Meta:
        app_label = 'marketplace'
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
