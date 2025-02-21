from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class CryptoWallet(models.Model):
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('suspended', _('Suspended'))
    ]
    
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='crypto_wallets'
    )
    currency = models.CharField(max_length=10)
    address = models.CharField(max_length=100)
    balance = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        default=0
    )
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
        unique_together = ['user', 'currency']

    def __str__(self):
        return f"{self.user.username}'s {self.currency} wallet"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES)[self.status]
