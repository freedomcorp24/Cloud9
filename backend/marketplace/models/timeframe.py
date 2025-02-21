from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class OrderTimeframe(models.Model):
    """Model for managing order completion timeframes"""
    DELIVERY_TYPES = [
        ('mail', _('Mail Delivery')),
        ('pickup', _('Pickup')),
        ('instant', _('Instant Delivery'))
    ]
    
    order = models.OneToOneField(
        'DeliveryOrder',
        on_delete=models.CASCADE,
        related_name='timeframe'
    )
    delivery_type = models.CharField(
        max_length=20,
        choices=DELIVERY_TYPES,
        help_text=_('Type of delivery')
    )
    base_days = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text=_('Base number of days for order completion')
    )
    extended_days = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_('Additional days requested by buyer')
    )
    auto_finalize_at = models.DateTimeField(
        help_text=_('When this order will automatically finalize')
    )
    last_extended = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When the timeframe was last extended')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Order Timeframe')
        verbose_name_plural = _('Order Timeframes')
        
    def __str__(self):
        return f"Timeframe for Order {self.order.id}"
        
    def clean(self):
        """Validate timeframe constraints"""
        if self.delivery_type in ['mail', 'pickup'] and self.base_days < 7:
            raise ValidationError({
                'base_days': _('Mail and pickup orders require minimum 7 days')
            })
            
        if self.delivery_type == 'instant' and self.base_days > 1:
            raise ValidationError({
                'base_days': _('Instant delivery cannot exceed 24 hours')
            })
            
    def save(self, *args, **kwargs):
        """Update auto finalize date when saving"""
        self.clean()
        
        # Calculate total days
        total_days = self.base_days + self.extended_days
        
        # Convert to hours for instant delivery
        if self.delivery_type == 'instant':
            total_hours = total_days * 24
            if total_hours > 24:
                total_hours = 24
            self.auto_finalize_at = timezone.now() + timedelta(hours=total_hours)
        else:
            self.auto_finalize_at = timezone.now() + timedelta(days=total_days)
            
        super().save(*args, **kwargs)
        
    def extend_timeframe(self, additional_days):
        """Extend the timeframe if order is in escrow"""
        if not self.order.status in ['pending', 'accepted', 'shipped']:
            raise ValidationError(_('Cannot extend timeframe for finalized orders'))
            
        self.extended_days += additional_days
        self.last_extended = timezone.now()
        self.save()
        
    @property
    def total_days(self):
        """Get total days including extensions"""
        return self.base_days + self.extended_days
        
    @property
    def days_remaining(self):
        """Get days remaining until auto-finalization"""
        if self.auto_finalize_at <= timezone.now():
            return 0
            
        delta = self.auto_finalize_at - timezone.now()
        return max(0, delta.days)
        
    @property
    def is_expired(self):
        """Check if timeframe has expired"""
        return timezone.now() >= self.auto_finalize_at
