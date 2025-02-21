from django.db import models
from django.utils.translation import gettext_lazy as _

class CryptoTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', _('Deposit')),
        ('withdrawal', _('Withdrawal')),
        ('transfer', _('Transfer'))
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('failed', _('Failed'))
    ]
    
    wallet = models.ForeignKey(
        'CryptoWallet',
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    tx_hash = models.CharField(max_length=100, unique=True)
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES
    )
    amount_crypto = models.DecimalField(
        max_digits=18,
        decimal_places=8
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Crypto Transaction')
        verbose_name_plural = _('Crypto Transactions')
        
    def __str__(self):
        return f"{self.transaction_type} - {self.tx_hash}"
        
    def get_confirmation_count(self):
        return self.confirmations.count()
