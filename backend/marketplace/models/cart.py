from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from oscar.apps.basket.abstract_models import AbstractBasket
from .product import ProductListing
from .vendor import VendorProfile

class Cart(AbstractBasket):
    """
    Shopping cart model extending Oscar's AbstractBasket
    with additional marketplace-specific features
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts'
    )
    vendor = models.ForeignKey(
        VendorProfile,
        on_delete=models.CASCADE,
        related_name='customer_carts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'marketplace'
        verbose_name = _('Shopping Cart')
        verbose_name_plural = _('Shopping Carts')
        unique_together = ['user', 'vendor']

class CartItem(models.Model):
    """
    Individual item in shopping cart with quantity and price tracking
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        ProductListing,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100)
        ],
        default=1
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=_('Price at time of adding to cart')
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'marketplace'
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
        ordering = ['-added_at']
        
    @property
    def total_price(self):
        """Calculate total price for this item"""
        return self.quantity * self.unit_price
        
    def __str__(self):
        return f"{self.quantity}x {self.product.title}"
