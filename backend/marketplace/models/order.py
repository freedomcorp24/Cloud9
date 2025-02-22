from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from oscar.apps.order.abstract_models import AbstractOrder
from .vendor import VendorProfile, VendorProduct
from .order_status import OrderStatus
from decimal import Decimal

class DeliveryOrder(AbstractOrder):
    """
    Order model for tracking deliveries, inheriting from Oscar's AbstractOrder
    """
    # Order completion timeframe constants
    MAIL_PICKUP_MIN_DAYS = 7  # Minimum days for mail/pickup orders
    INSTANT_DELIVERY_MAX_HOURS = 24  # Maximum hours for instant delivery
    
    date_placed = models.DateTimeField(auto_now_add=True)
    number = models.CharField(max_length=128, unique=True)
    total_excl_tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_incl_tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    DELIVERY_TYPES = [
        ('instant', 'Instant Delivery'),
        ('mail', 'Mail Delivery'),
        ('pickup', 'Pickup')
    ]
    
    # Real-time tracking settings
    enable_real_time_tracking = models.BooleanField(
        default=False,
        help_text=_('Enable real-time location tracking for this delivery')
    )
    driver_location_permission = models.BooleanField(
        default=False,
        help_text=_('Driver has granted permission for location tracking')
    )
    last_location_update = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Timestamp of last location update')
    )
    
    class Meta:
        app_label = 'marketplace'
        verbose_name = _('Delivery Order')
        verbose_name_plural = _('Delivery Orders')
        ordering = ['-created_at']
    
    # Status is now tracked through OrderStatus model
    
    # Inheriting core fields from AbstractOrder
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE)
    product = models.ForeignKey(VendorProduct, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='marketplace_orders')
    quantity = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100)
        ]
    )
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPES)
    @property
    def status(self):
        """Get current order status"""
        try:
            return self.status_history.latest().status
        except OrderStatus.DoesNotExist:
            return 'pending'
            
    def set_status(self, new_status, changed_by=None, notes='', location=None):
        """Set new order status with tracking and optional location"""
        if new_status not in dict(OrderStatus.STATUS_CHOICES):
            raise ValueError(f"Invalid status: {new_status}")
            
        # Validate completion timeframes
        if new_status == 'completed':
            if self.delivery_type in ['mail', 'pickup']:
                min_completion = self.date_placed + timedelta(days=self.MAIL_PICKUP_MIN_DAYS)
                if timezone.now() < min_completion:
                    raise ValueError(f'Cannot complete {self.delivery_type} orders before {self.MAIL_PICKUP_MIN_DAYS} days')
            elif self.delivery_type == 'instant':
                max_completion = self.date_placed + timedelta(hours=self.INSTANT_DELIVERY_MAX_HOURS)
                if timezone.now() > max_completion:
                    raise ValueError(f'Instant delivery orders must be completed within {self.INSTANT_DELIVERY_MAX_HOURS} hours')
        
        status = OrderStatus.objects.create(
            order=self,
            status=new_status,
            changed_by=changed_by,
            notes=notes
        )
        
        # Update location if provided
        if location and isinstance(location, dict):
            DeliveryTracking.objects.create(
                order=self,
                latitude=location.get('latitude'),
                longitude=location.get('longitude'),
                status_update=new_status
            )
            
            if self.enable_real_time_tracking and self.driver_location_permission:
                self.last_location_update = timezone.now()
                self.save()
    delivery_address = models.TextField(max_length=500)
    delivery_instructions = models.TextField(max_length=500, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    
    def __str__(self):
        return f"Order {self.id} - {self.delivery_type} ({self.status})"

class OrderDispute(models.Model):
    """
    Model for handling order disputes
    """
    DISPUTE_TYPES = [
        ('quality', 'Product Quality'),
        ('delivery', 'Delivery Issues'),
        ('other', 'Other Issues')
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ]
    
    order = models.ForeignKey(DeliveryOrder, on_delete=models.CASCADE)
    dispute_type = models.CharField(max_length=20, choices=DISPUTE_TYPES)
    description = models.TextField(max_length=1000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    resolution = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'marketplace'
        verbose_name = _('Order Dispute')
        verbose_name_plural = _('Order Disputes')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Dispute for Order {self.order.id} - {self.dispute_type}"

class DeliveryTracking(models.Model):
    """
    Real-time and manual tracking for deliveries
    """
    order = models.ForeignKey(DeliveryOrder, on_delete=models.CASCADE, related_name='tracking_updates')
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
    status_update = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_manual_update = models.BooleanField(
        default=True,
        help_text=_('Whether this is a manual status update vs real-time tracking')
    )
    driver_notes = models.TextField(
        blank=True,
        help_text=_('Additional notes from driver for manual updates')
    )
    
    class Meta:
        app_label = 'marketplace'
        verbose_name = _('Delivery Tracking')
        verbose_name_plural = _('Delivery Tracking')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Tracking for Order {self.order.id} at {self.timestamp}"
