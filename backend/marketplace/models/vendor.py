from django.db import models
from django.utils.translation import gettext_lazy as _
from oscar.apps.partner.abstract_models import AbstractPartner, AbstractStockRecord

class VendorProfile(AbstractPartner):
    """
    Vendor profile model for marketplace, inheriting from Oscar's AbstractPartner
    """
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    business_name = models.CharField(max_length=100)
    description = models.TextField(max_length=2000)
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
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_ratings = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.business_name} ({self.user.username})"

class VendorProduct(AbstractStockRecord):
    """
    Vendor's product listing with delivery options, inheriting from Oscar's AbstractStockRecord
    """
    instant_delivery = models.BooleanField(default=False)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pickup_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta(AbstractStockRecord.Meta):
        app_label = 'marketplace'
    max_delivery_distance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.0
    )
    min_order_quantity = models.IntegerField(default=1)
    max_order_quantity = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.title} by {self.vendor.business_name}"
