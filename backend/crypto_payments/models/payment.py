from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class PaymentBatch(models.Model):
    """Model for managing batched cryptocurrency payments"""
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    currency = models.CharField(max_length=10)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('frozen', 'Frozen')
        ],
        default='pending'
    )
    total_amount = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    transaction_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Payment Batch')
        verbose_name_plural = _('Payment Batches')
        ordering = ['-created_at']

    def __str__(self):
        return f"Batch {self.id} - {self.currency} ({self.status})"

class BatchTransaction(models.Model):
    """Model for tracking transactions within a batch"""
    batch = models.ForeignKey(PaymentBatch, on_delete=models.CASCADE)
    transaction = models.ForeignKey('crypto_payments.CryptoTransaction', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Batch Transaction')
        verbose_name_plural = _('Batch Transactions')
        unique_together = ('batch', 'transaction')
