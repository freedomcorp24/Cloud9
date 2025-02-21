from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal

class UserWallet(models.Model):
    """Model for user cryptocurrency wallets"""
    user = models.OneToOneField(
        'UserProfile',
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    btc_balance = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        default=Decimal('0.0'),
        validators=[MinValueValidator(Decimal('0.0'))],
        help_text=_('BTC balance')
    )
    xmr_balance = models.DecimalField(
        max_digits=18,
        decimal_places=12,
        default=Decimal('0.0'),
        validators=[MinValueValidator(Decimal('0.0'))],
        help_text=_('XMR balance')
    )
    usdt_balance = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=Decimal('0.0'),
        validators=[MinValueValidator(Decimal('0.0'))],
        help_text=_('USDT balance')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User Wallet')
        verbose_name_plural = _('User Wallets')

    def __str__(self):
        return f"Wallet for {self.user}"

class WithdrawalAddress(models.Model):
    """Model for tracking withdrawal addresses"""
    CURRENCY_CHOICES = [
        ('btc', 'Bitcoin'),
        ('xmr', 'Monero'),
        ('usdt', 'USDT')
    ]
    
    wallet = models.ForeignKey(
        UserWallet,
        on_delete=models.CASCADE,
        related_name='withdrawal_addresses'
    )
    currency = models.CharField(
        max_length=4,
        choices=CURRENCY_CHOICES,
        help_text=_('Cryptocurrency type')
    )
    address = models.CharField(
        max_length=128,
        help_text=_('Withdrawal address')
    )
    is_flagged = models.BooleanField(
        default=False,
        help_text=_('Whether this address has been flagged for suspicious activity')
    )
    flag_reason = models.TextField(
        blank=True,
        help_text=_('Reason for flagging this address')
    )
    used_by_other_accounts = models.BooleanField(
        default=False,
        help_text=_('Whether this address has been used by other accounts')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Withdrawal Address')
        verbose_name_plural = _('Withdrawal Addresses')
        unique_together = ['wallet', 'currency', 'address']
        
    def __str__(self):
        return f"{self.get_currency_display()} address for {self.wallet.user}"
