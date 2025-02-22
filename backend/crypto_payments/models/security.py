from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal

class SecurityThreshold(models.Model):
    """Configurable security thresholds for cryptocurrency operations"""
    
    THRESHOLD_TYPES = [
        ('withdrawal_daily', _('Daily Withdrawal Limit')),
        ('withdrawal_monthly', _('Monthly Withdrawal Limit')),
        ('hot_wallet_max', _('Hot Wallet Maximum')),
        ('suspicious_amount', _('Suspicious Transaction Amount')),
        ('max_failed_attempts', _('Maximum Failed Attempts')),
        ('address_risk_score', _('Address Risk Score Threshold'))
    ]
    
    threshold_type = models.CharField(max_length=50, choices=THRESHOLD_TYPES, unique=True)
    value = models.DecimalField(max_digits=18, decimal_places=8)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='security_thresholds'
    )

    class Meta:
        verbose_name = _('Security Threshold')
        verbose_name_plural = _('Security Thresholds')
        
    def __str__(self):
        return f"{self.get_threshold_type_display()}: {self.value}"

class AccountFreeze(models.Model):
    """Record of account freezes, both automated and manual"""
    
    FREEZE_TYPES = [
        ('automated', _('Automated Freeze')),
        ('manual', _('Manual Admin Freeze')),
        ('suspicious', _('Suspicious Activity'))
    ]
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('expired', _('Expired')),
        ('lifted', _('Manually Lifted'))
    ]
    
    wallet = models.ForeignKey(
        'crypto_payments.CryptoWallet',
        on_delete=models.CASCADE,
        related_name='freezes'
    )
    freeze_type = models.CharField(max_length=20, choices=FREEZE_TYPES)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    lifted_at = models.DateTimeField(null=True, blank=True)
    lifted_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='lifted_freezes'
    )
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_freezes'
    )

    class Meta:
        verbose_name = _('Account Freeze')
        verbose_name_plural = _('Account Freezes')
        
    def __str__(self):
        return f"{self.wallet} - {self.get_freeze_type_display()}"
        
    def is_active(self) -> bool:
        """Check if freeze is currently active"""
        if self.status != 'active':
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            self.status = 'expired'
            self.save()
            return False
        return True

class WithdrawalAutomation(models.Model):
    """Configuration for automated withdrawal processing"""
    
    AUTOMATION_TYPES = [
        ('instant', _('Instant Processing')),
        ('scheduled', _('Scheduled Processing')),
        ('manual', _('Manual Review Required'))
    ]
    
    currency_type = models.CharField(max_length=10)
    automation_type = models.CharField(max_length=20, choices=AUTOMATION_TYPES)
    min_amount = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        help_text=_("Minimum amount for this automation rule")
    )
    max_amount = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        help_text=_("Maximum amount for this automation rule")
    )
    is_active = models.BooleanField(default=True)
    requires_2fa = models.BooleanField(
        default=True,
        help_text=_("Require 2FA verification for automated withdrawals")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Withdrawal Automation')
        verbose_name_plural = _('Withdrawal Automations')
        unique_together = ['currency_type', 'automation_type']
        
    def __str__(self):
        return f"{self.currency_type} - {self.get_automation_type_display()}"
