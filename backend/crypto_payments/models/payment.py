from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class CryptoWallet(models.Model):
    """Model for storing cryptocurrency wallets"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    currency = models.CharField(max_length=10)
    address = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'currency')
        verbose_name = _('Crypto Wallet')
        verbose_name_plural = _('Crypto Wallets')

    def __str__(self):
        return f"{self.currency} wallet for {self.user.username}"

class CryptoTransaction(models.Model):
    """Model for tracking cryptocurrency transactions"""
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal')
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]
    
    wallet = models.ForeignKey(CryptoWallet, on_delete=models.CASCADE)
    tx_hash = models.CharField(max_length=100)
    amount_crypto = models.DecimalField(max_digits=18, decimal_places=8)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    destination_address = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Crypto Transaction')
        verbose_name_plural = _('Crypto Transactions')
        
    def __str__(self):
        return f"{self.transaction_type} - {self.amount_crypto} {self.wallet.currency}"
