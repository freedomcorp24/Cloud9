from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.utils import timezone

class ProductListing(models.Model):
    """Model for vendor product listings"""
    # General Information
    vendor = models.ForeignKey('VendorProfile', on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    origin_country = models.CharField(max_length=100)
    
    # Payment Methods
    escrow_enabled = models.BooleanField(default=True)
    fe_enabled = models.BooleanField(default=False)  # Finalize Early - only for trusted vendors
    accept_btc = models.BooleanField(default=True)
    accept_xmr = models.BooleanField(default=True)
    accept_usdt = models.BooleanField(default=True)
    
    # Item Specifics
    title = models.CharField(max_length=200)
    description = models.TextField()
    refund_policy = models.TextField()
    tags = models.CharField(max_length=500)  # Comma-separated, max 10 tags
    auto_message = models.TextField(blank=True)  # Optional default message
    
    # Pricing and Quantity
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_quantity = models.IntegerField(default=1)
    unlimited_quantity = models.BooleanField(default=False)
    
    # Bulk Pricing (Optional)
    bulk_pricing = models.JSONField(null=True, blank=True)
    
    # Images
    main_image = models.ImageField(upload_to='product_images/')
    image_2 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    image_3 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    image_4 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    image_5 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    image_6 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    
    # Shipping
    ships_to = models.CharField(max_length=500)  # Comma-separated countries
    
    # Postage Options (1-5)
    class PostageOption(models.Model):
        product = models.ForeignKey('ProductListing', on_delete=models.CASCADE)
        name = models.CharField(max_length=100)
        price = models.DecimalField(max_digits=10, decimal_places=2)
        
        class Meta:
            verbose_name = _('Postage Option')
            verbose_name_plural = _('Postage Options')
    
    # Search Options
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('hidden', 'Hidden')
    ]
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    restrict_buyers = models.BooleanField(default=False)
    
    # Timeframe Settings
    cancel_hours = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(95)],
        help_text=_('Hours until buyer can cancel if not accepted')
    )
    auto_cancel_hours = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(96)],
        help_text=_('Hours until pending sale auto-cancels')
    )
    auto_finalize_days = models.IntegerField(
        validators=[MinValueValidator(7), MaxValueValidator(90)],
        help_text=_('Days until shipped sale auto-finalizes')
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Product Listing')
        verbose_name_plural = _('Product Listings')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.vendor.user.username}"
    
    def clean(self):
        """Validate model data"""
        # Ensure FE is only enabled for trusted vendors
        if self.fe_enabled and not self.vendor.is_trusted:
            raise ValidationError(_('Only trusted vendors can enable Finalize Early'))
            
        # Validate tag count
        if len(self.tags.split(',')) > 10:
            raise ValidationError(_('Maximum 10 tags allowed'))
            
        # Validate image sizes
        max_size = 400 * 1024  # 400KB
        for img in [self.main_image, self.image_2, self.image_3, 
                   self.image_4, self.image_5, self.image_6]:
            if img and img.size > max_size:
                raise ValidationError(_('Image size must not exceed 400KB'))
