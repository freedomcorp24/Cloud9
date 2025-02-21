from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

class LiveDeliveryTracking(models.Model):
    """Real-time tracking for instant deliveries"""
    TRACKING_MODES = [
        ('realtime', _('Real-time GPS')),
        ('manual', _('Manual Updates'))
    ]
    
    order = models.OneToOneField(
        'DeliveryOrder',
        on_delete=models.CASCADE,
        related_name='live_tracking',
        help_text=_('The order being tracked')
    )
    
    tracking_mode = models.CharField(
        max_length=10,
        choices=TRACKING_MODES,
        default='manual',
        help_text=_('Current tracking mode')
    )
    driver_name = models.CharField(
        max_length=100,
        help_text=_('Name of delivery driver')
    )
    driver_photo = models.ImageField(
        upload_to='driver_photos/',
        null=True,
        blank=True,
        help_text=_('Photo of delivery driver')
    )
    current_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ],
        help_text=_('Current latitude of driver')
    )
    current_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ],
        help_text=_('Current longitude of driver')
    )
    estimated_arrival = models.DateTimeField(
        help_text=_('Estimated time of arrival')
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text=_('When location was last updated')
    )
    delivery_notes = models.TextField(
        blank=True,
        help_text=_('Any special delivery instructions')
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this tracking is currently active')
    )
    
    class Meta:
        verbose_name = _('Live Delivery Tracking')
        verbose_name_plural = _('Live Delivery Tracking')
        
    def __str__(self):
        return f"Live tracking for Order {self.order.id}"

class DeliveryLocation(models.Model):
    """Historical location points for delivery tracking"""
    tracking = models.ForeignKey(
        LiveDeliveryTracking,
        on_delete=models.CASCADE,
        related_name='location_history',
        help_text=_('The tracking record this location belongs to')
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ]
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ]
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When this location was recorded')
    )
    
    class Meta:
        verbose_name = _('Delivery Location')
        verbose_name_plural = _('Delivery Locations')
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"Location for Order {self.tracking.order.id} at {self.timestamp}"
