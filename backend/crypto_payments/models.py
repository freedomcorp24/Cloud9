from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from oscar.apps.payment.abstract_models import AbstractTransaction

class CryptoWallet(models.Model):
    """
    Market-controlled cryptocurrency wallet for users
    """
    CURRENCY_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('XMR', 'Monero'),
        ('USDT', 'Tether'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('disabled', 'Disabled'),
        ('suspended', 'Suspended'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES)
    address = models.CharField(max_length=100, unique=True)
    private_key = models.CharField(max_length=100)  # Encrypted
    public_key = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0.00000000'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'currency')
        verbose_name = _('Crypto Wallet')
        verbose_name_plural = _('Crypto Wallets')
    
    def __str__(self):
        return f"{self.user}'s {self.currency} Wallet ({self.address})"

class CryptoTransaction(models.Model):
    """
    Cryptocurrency transaction with confirmation tracking
    """
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('payment', 'Payment'),
        ('refund', 'Refund'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirming', 'Confirming'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    wallet = models.ForeignKey(CryptoWallet, on_delete=models.CASCADE)
    tx_hash = models.CharField(max_length=100, unique=True)
    confirmations = models.IntegerField(default=0)
    required_confirmations = models.IntegerField(default=6)  # BTC default
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount_crypto = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0.00000000'))
    fee = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0.00000000'))
    memo = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'crypto_payments'
        verbose_name = _('Crypto Transaction')
        verbose_name_plural = _('Crypto Transactions')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} - {self.tx_hash} ({self.status})"

    @property
    def is_confirmed(self):
        return self.confirmations >= self.required_confirmations

class TransactionConfirmation(models.Model):
    """
    Track individual confirmations for transactions
    """
    transaction = models.ForeignKey(CryptoTransaction, on_delete=models.CASCADE)
    block_height = models.IntegerField()
    block_hash = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('transaction', 'block_height')
        ordering = ['block_height']
    
    def __str__(self):
        return f"Confirmation at block {self.block_height} for {self.transaction.tx_hash}"
