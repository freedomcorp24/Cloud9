from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

class OrderStatus(models.Model):
    """Model for tracking order status changes"""
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('accepted', _('Accepted')),
        ('shipped', _('Shipped')),
        ('finalized', _('Finalized')),
        ('disputed', _('Disputed')),
        ('cancelled', _('Cancelled'))
    ]
    
    order = models.ForeignKey(
        'DeliveryOrder',
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        help_text=_('Current status of the order')
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text=_('User who changed the status')
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When this status was set')
    )
    notes = models.TextField(
        blank=True,
        help_text=_('Optional notes about this status change')
    )
    
    class Meta:
        verbose_name = _('Order Status')
        verbose_name_plural = _('Order Statuses')
        ordering = ['-changed_at']
        get_latest_by = 'changed_at'
        
    def __str__(self):
        return f"{self.order} - {self.get_status_display()}"
        
    @property
    def is_final(self):
        """Check if this is a final status that can't be changed"""
        return self.status in ['finalized', 'cancelled']
