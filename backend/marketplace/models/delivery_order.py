from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class DeliveryOrder(models.Model):
    """Model for delivery orders"""
    vendor = models.ForeignKey(
        'VendorProfile',
        on_delete=models.PROTECT,
        related_name='delivery_orders'
    )
    customer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='received_orders'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', _('Pending')),
            ('on_way', _('On the Way')),
            ('arrived', _('Arrived at Location')),
            ('close', _('Delivery Complete')),
            ('cancelled', _('Cancelled'))
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Delivery Order')
        verbose_name_plural = _('Delivery Orders')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Order #{self.id} - {self.status}"
        
    def set_status(self, status, changed_by=None, notes=None):
        """Update order status and create status history entry"""
        if status not in dict(self._meta.get_field('status').choices):
            raise ValueError(_('Invalid status'))
            
        self.status = status
        self.save()
        
        # Create status history entry
        OrderStatusHistory.objects.create(
            order=self,
            status=status,
            changed_by=changed_by,
            notes=notes
        )

class OrderStatusHistory(models.Model):
    """Model for tracking order status changes"""
    order = models.ForeignKey(
        DeliveryOrder,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='status_changes'
    )
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Order Status History')
        verbose_name_plural = _('Order Status History')
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.order} - {self.status} at {self.timestamp}"
