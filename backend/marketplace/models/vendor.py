from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from oscar.apps.partner.abstract_models import AbstractPartner, AbstractStockRecord
class VendorProfile(AbstractPartner):
    """
    Vendor profile model for marketplace, inheriting from Oscar's AbstractPartner
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_profile')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='marketplace_partners', blank=True)
    business_name = models.CharField(max_length=100)
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('verified', 'Verified'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    bond_paid = models.BooleanField(default=False)
    bond_waived = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))
    total_ratings = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(AbstractPartner.Meta):
        app_label = 'marketplace'
        verbose_name = _('Vendor Profile')
        verbose_name_plural = _('Vendor Profiles')

    def __str__(self):
        return f"{self.business_name} ({self.user.username})"

class VendorProduct(AbstractStockRecord):
    """
    Vendor's product listing with delivery options, inheriting from Oscar's AbstractStockRecord
    """
    partner = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='vendor_stockrecords', default=1)
    product = models.ForeignKey('catalogue.Product', on_delete=models.CASCADE, related_name='vendor_stockrecords')
    partner_sku = models.CharField(max_length=128, default=lambda: 'SKU-' + timezone.now().strftime('%Y%m%d-%H%M%S'))
    instant_delivery = models.BooleanField(default=False)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    pickup_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    max_delivery_distance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('10.00')
    )
    min_order_quantity = models.IntegerField(default=1)
    max_order_quantity = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(AbstractStockRecord.Meta):
        app_label = 'marketplace'
        verbose_name = _('Vendor Product')
        verbose_name_plural = _('Vendor Products')
        unique_together = ('partner', 'partner_sku')

    def __str__(self):
        return f"{self.product.title} by {self.vendor.business_name}"
