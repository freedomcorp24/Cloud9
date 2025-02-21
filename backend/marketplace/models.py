from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from oscar.core.loading import get_class, get_model

Product = get_model('catalogue', 'Product')

class VendorProfile(models.Model):
    """
    Extended profile for vendors with additional verification and settings
    """
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('suspended', 'Suspended'),
        ('banned', 'Banned'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=100, help_text=_('Business name (max 100 characters)'))
    description = models.TextField(max_length=2000, blank=True, help_text=_('Business description (max 2000 characters)'))
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    bond_amount = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    bond_paid = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_ratings = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Vendor Profile')
        verbose_name_plural = _('Vendor Profiles')

    def __str__(self):
        return f"{self.business_name} ({self.user.username})"

class VendorProduct(models.Model):
    """
    Links products to vendors with additional vendor-specific details
    """
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2, help_text=_('Product price'))
    stock = models.IntegerField(default=0, help_text=_('Available stock'))
    instant_delivery = models.BooleanField(default=False, help_text=_('Available for instant delivery'))
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text=_('Fee for instant delivery'))
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text=_('Fee for standard shipping'))
    pickup_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text=_('Fee for in-person pickup'))
    max_delivery_distance = models.DecimalField(max_digits=5, decimal_places=2, default=50.00, help_text=_('Maximum delivery distance in km'))
    min_order_quantity = models.IntegerField(default=1, help_text=_('Minimum order quantity'))
    max_order_quantity = models.IntegerField(default=100, help_text=_('Maximum order quantity'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Vendor Product')
        verbose_name_plural = _('Vendor Products')
        unique_together = ('vendor', 'product')

    def __str__(self):
        return f"{self.vendor.business_name} - {self.product.title}"
