from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings

class DepositAddress(models.Model):
    """Model for managing one-time deposit addresses"""
    wallet = models.ForeignKey('CryptoWallet', on_delete=models.CASCADE)
    address = models.CharField(max_length=100, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('pending', 'Payment Pending'),
            ('completed', 'Completed'),
            ('expired', 'Expired')
        ],
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    payment_detected_at = models.DateTimeField(null=True)
    
    class Meta:
        verbose_name = _('Deposit Address')
        verbose_name_plural = _('Deposit Addresses')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.address} ({self.status})"
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Set expiry to 2 hours from creation by default
            self.expires_at = timezone.now() + timezone.timedelta(
                hours=settings.DEPOSIT_ADDRESS_EXPIRY
            )
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if address has expired"""
        if self.status == 'pending':
            # Keep checking pending payments even after expiry
            return False
        return timezone.now() > self.expires_at
    
    @property
    def required_confirmations(self):
        """Get required confirmations based on currency"""
        currency = self.wallet.currency.upper()
        if currency == 'BTC':
            return settings.BTC_MIN_CONFIRMATIONS
        elif currency == 'XMR':
            return settings.XMR_MIN_CONFIRMATIONS
        elif currency == 'USDT':
            return settings.USDT_MIN_CONFIRMATIONS
        return 0  # Should never happen as currency is validated at wallet level
