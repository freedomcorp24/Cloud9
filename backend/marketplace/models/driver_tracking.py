from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class DriverLocation(models.Model):
    """Real-time driver location tracking"""
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='locations',
        help_text=_('Driver being tracked')
    )
    
    # Location data
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(Decimal('-90')),
            MaxValueValidator(Decimal('90'))
        ],
        help_text=_('Latitude coordinate')
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(Decimal('-180')),
            MaxValueValidator(Decimal('180'))
        ],
        help_text=_('Longitude coordinate')
    )
    accuracy = models.FloatField(
        null=True,
        blank=True,
        help_text=_('Location accuracy in meters')
    )
    
    # Tracking status
    TRACKING_CHOICES = [
        ('enabled', _('Enabled')),
        ('paused', _('Paused')),
        ('disabled', _('Disabled'))
    ]
    tracking_status = models.CharField(
        max_length=20,
        choices=TRACKING_CHOICES,
        default='disabled',
        help_text=_('Current tracking status')
    )
    last_update = models.DateTimeField(
        auto_now=True,
        help_text=_('When location was last updated')
    )
    
    class Meta:
        verbose_name = _('Driver Location')
        verbose_name_plural = _('Driver Locations')
        ordering = ['-last_update']
        
    def __str__(self):
        return f"{self.driver.username} at ({self.latitude}, {self.longitude})"

class DeliveryStatus(models.Model):
    """Manual delivery status updates"""
    order = models.ForeignKey(
        'marketplace.DeliveryOrder',
        on_delete=models.CASCADE,
        related_name='status_updates',
        help_text=_('Order being delivered')
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='status_updates',
        help_text=_('Driver making the delivery')
    )
    
    # Status information
    STATUS_CHOICES = [
        ('assigned', _('Assigned to Driver')),
        ('pickup', _('At Pickup Location')),
        ('in_transit', _('In Transit')),
        ('nearby', _('Nearby Delivery Location')),
        ('arrived', _('Arrived at Delivery Location')),
        ('completed', _('Delivery Completed')),
        ('failed', _('Delivery Failed'))
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        help_text=_('Current delivery status')
    )
    notes = models.TextField(
        blank=True,
        help_text=_('Additional status notes')
    )
    
    # Location data (optional)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal('-90')),
            MaxValueValidator(Decimal('90'))
        ],
        help_text=_('Optional latitude coordinate')
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal('-180')),
            MaxValueValidator(Decimal('180'))
        ],
        help_text=_('Optional longitude coordinate')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When status was created')
    )
    
    class Meta:
        verbose_name = _('Delivery Status')
        verbose_name_plural = _('Delivery Statuses')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Order {self.order.id} - {self.get_status_display()}"
