from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from marketplace.models import VendorProfile, VendorProduct

class DeliveryOrder(models.Model):
    """
    Order model for tracking deliveries
    """
    DELIVERY_TYPES = [
        ('instant', 'Instant Delivery'),
        ('mail', 'Mail Delivery'),
        ('pickup', 'Pickup')
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed')
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE)
    product = models.ForeignKey(VendorProduct, on_delete=models.CASCADE)
    quantity = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100)
        ]
    )
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_address = models.TextField(max_length=500)
    delivery_instructions = models.TextField(max_length=500, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Delivery Order')
        verbose_name_plural = _('Delivery Orders')
        ordering = ['-created_at']
    
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
        verbose_name = _('Order Dispute')
        verbose_name_plural = _('Order Disputes')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Dispute for Order {self.order.id} - {self.dispute_type}"

class DeliveryTracking(models.Model):
    """
    Real-time tracking for deliveries
    """
    order = models.ForeignKey(DeliveryOrder, on_delete=models.CASCADE)
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
    
    class Meta:
        verbose_name = _('Delivery Tracking')
        verbose_name_plural = _('Delivery Tracking')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Tracking for Order {self.order.id} at {self.timestamp}"
