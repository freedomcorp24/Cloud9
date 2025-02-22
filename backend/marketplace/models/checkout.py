from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from .cart import Cart
from .order import DeliveryOrder

class CheckoutSession(models.Model):
    """
    Model for tracking checkout process and enforcing PIN verification
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='checkout_sessions'
    )
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='checkout_sessions'
    )
    pin_verified = models.BooleanField(
        default=False,
        help_text=_('Indicates if transaction PIN has been verified')
    )
    pin_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Timestamp of PIN verification')
    )
    delivery_type = models.CharField(
        max_length=20,
        choices=DeliveryOrder.DELIVERY_TYPES,
        null=True,
        blank=True
    )
    completion_window = models.IntegerField(
        validators=[MinValueValidator(1)],
        null=True,
        blank=True,
        help_text=_('Order completion window in days')
    )
    delivery_address = models.TextField(
        max_length=500,
        blank=True,
        help_text=_('Delivery address for mail/instant delivery')
    )
    delivery_instructions = models.TextField(
        max_length=500,
        blank=True,
        help_text=_('Additional delivery instructions')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'marketplace'
        verbose_name = _('Checkout Session')
        verbose_name_plural = _('Checkout Sessions')
        
    def verify_pin(self, pin):
        """Verify transaction PIN and update session"""
        if self.user.user_profile.verify_pin(pin):
            self.pin_verified = True
            self.pin_verified_at = timezone.now()
            self.save()
            return True
        return False
        
    def is_pin_verification_valid(self):
        """Check if PIN verification is still valid (within 15 minutes)"""
        if not self.pin_verified or not self.pin_verified_at:
            return False
            
        return timezone.now() - self.pin_verified_at < timedelta(minutes=15)
        
    def validate_completion_window(self):
        """Validate completion window based on delivery type"""
        if not self.delivery_type or not self.completion_window:
            return False
            
        if self.delivery_type == 'mail':
            return self.completion_window >= DeliveryOrder.MAIL_PICKUP_MIN_DAYS
        elif self.delivery_type == 'pickup':
            return self.completion_window >= DeliveryOrder.MAIL_PICKUP_MIN_DAYS
        elif self.delivery_type == 'instant':
            return self.completion_window <= 1  # Max 24 hours
            
        return False
        
    def create_order(self):
        """Create order from checkout session"""
        if not self.is_pin_verification_valid():
            raise ValueError(_('PIN verification required'))
            
        if not self.validate_completion_window():
            raise ValueError(_('Invalid completion window'))
            
        with transaction.atomic():
            order = DeliveryOrder.objects.create(
                user=self.user,
                vendor=self.cart.vendor,
                delivery_type=self.delivery_type,
                completion_window=self.completion_window,
                delivery_address=self.delivery_address,
                delivery_instructions=self.delivery_instructions
            )
            
            # Create order items from cart
            for item in self.cart.items.all():
                order.items.create(
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.unit_price
                )
                
            # Clear cart
            self.cart.delete()
            
            return order
