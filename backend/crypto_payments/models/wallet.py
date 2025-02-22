from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal

class CryptoWallet(models.Model):
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('suspended', _('Suspended'))
    ]
    
    WALLET_TYPES = [
        ('hot', _('Hot Wallet')),
        ('cold', _('Cold Storage')),
        ('deposit', _('Deposit Address')),
        ('withdrawal', _('Withdrawal Address'))
    ]
    
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='crypto_wallets'
    )
    wallet_id = models.CharField(max_length=64, unique=True)
    wallet_type = models.CharField(max_length=20, choices=WALLET_TYPES, default='deposit')
    currency_type = models.CharField(max_length=10)
    address = models.CharField(max_length=100)
    deposit_address = models.CharField(max_length=100, blank=True, null=True)
    deposit_address_expires = models.DateTimeField(null=True, blank=True)
    balance = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        default=Decimal('0')
    )
    
    # Hot/cold wallet specific fields
    hot_wallet_threshold = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        null=True,
        blank=True,
        help_text=_("Maximum amount to keep in hot wallet")
    )
    last_rebalance = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Crypto Wallet')
        verbose_name_plural = _('Crypto Wallets')
        unique_together = ['user', 'currency_type']
        indexes = [
            models.Index(fields=['wallet_type', 'currency_type']),
            models.Index(fields=['address']),
        ]

    def __str__(self):
        return f"{self.user.username}'s {self.currency_type} wallet"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES)[self.status]
        
    def is_deposit_address_expired(self):
        """Check if deposit address has expired."""
        if not self.deposit_address_expires:
            return True
        return timezone.now() > self.deposit_address_expires
        
    def needs_rebalancing(self) -> bool:
        """Check if hot wallet needs rebalancing"""
        if self.wallet_type != 'hot' or not self.hot_wallet_threshold:
            return False
        return self.balance > self.hot_wallet_threshold
    
    def get_excess_amount(self) -> Decimal:
        """Calculate excess amount for rebalancing"""
        if not self.needs_rebalancing():
            return Decimal('0')
        return self.balance - self.hot_wallet_threshold
        
    def get_cold_wallet(self):
        """Get corresponding cold wallet for this currency"""
        return CryptoWallet.objects.filter(
            wallet_type='cold',
            currency_type=self.currency_type,
            is_active=True
        ).first()
        
    def clean(self):
        """Validate wallet configuration"""
        if self.wallet_type in ['hot', 'cold']:
            if not self.hot_wallet_threshold and self.wallet_type == 'hot':
                raise ValidationError(_('Hot wallet requires threshold configuration'))
        if self.wallet_type in ['deposit', 'withdrawal'] and self.hot_wallet_threshold:
            raise ValidationError(_('Deposit/withdrawal addresses should not have threshold configuration'))
