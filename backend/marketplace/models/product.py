from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from oscar.apps.catalogue.abstract_models import AbstractProduct
from .vendor_fe import VendorFEPermission
from .listing import ListingStatus, ListingDeletion
from .vendor import VendorProfile

User = get_user_model()

class ProductListing(AbstractProduct):
    """Model for vendor product listings, inheriting from Oscar's AbstractProduct"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('deleted', 'Deleted'),
        ('private', 'Private')
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    authorized_users = models.ManyToManyField(
        User,
        related_name='private_listings',
        blank=True,
        help_text=_('Users authorized to view and purchase this private listing')
    )
    deleted_at = models.DateTimeField(null=True, blank=True)
    last_active_at = models.DateTimeField(auto_now_add=True)
    preserve_data = models.BooleanField(
        default=True,
        help_text=_('Preserve listing data for order history')
    )
    has_active_orders = models.BooleanField(
        default=False,
        help_text=_('Indicates if listing has any active orders')
    )
    # General Information
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE)
    
    @property
    def can_access_dashboard(self):
        """Check if vendor has access to dashboard features"""
        return self.vendor.bond_paid or self.vendor.bond_waived
    category = models.CharField(max_length=100)
    origin_country = models.CharField(max_length=100)
    
    # Payment Methods
    escrow_enabled = models.BooleanField(default=True)
    fe_enabled = models.BooleanField(default=False)  # Finalize Early - only for trusted vendors
    accept_btc = models.BooleanField(default=True)
    accept_xmr = models.BooleanField(default=True)
    accept_usdt = models.BooleanField(default=True)
    
    # Item Specifics
    refund_policy = models.TextField()
    tags = models.CharField(max_length=500)  # Comma-separated, max 10 tags
    auto_message = models.TextField(blank=True)  # Optional default message
    
    # Quantity Settings
    unlimited_quantity = models.BooleanField(default=False)
    
    # Bulk Pricing (Optional)
    bulk_pricing = models.JSONField(null=True, blank=True)
    
    class Meta:
        app_label = 'marketplace'
    
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
        permissions = [
            ('view_private_listings', 'Can view all private listings'),
            ('manage_listings', 'Can manage all listings')
        ]
    
    def __str__(self):
        return f"{self.title} by {self.vendor.user.username}"
        
    def user_can_view(self, user):
        """Check if a user has permission to view this listing"""
        # Admins and support staff can always view
        if user.is_staff or user.is_superuser:
            return True
            
        # Public listings are visible to all
        if self.status != 'private':
            return True
            
        # Vendor can view their own listings
        if self.vendor.user == user:
            return True
            
        # Check if user is authorized for private listing
        return self.authorized_users.filter(id=user.id).exists()
        
    def change_status(self, new_status, changed_by=None, reason=None):
        """Change listing status with validation and tracking"""
        if new_status not in [s[0] for s in self.STATUS_CHOICES]:
            raise ValidationError(_('Invalid status'))
            
        # Check for active orders before deletion
        if new_status == 'deleted':
            has_active = self.orders.filter(
                status__in=['pending', 'processing', 'shipped']
            ).exists()
            if has_active:
                self.has_active_orders = True
                self.preserve_data = True
            
        old_status = self.status
        self.status = new_status
        
        if new_status == 'deleted':
            self.deleted_at = timezone.now()
        elif new_status == 'active':
            self.last_active_at = timezone.now()
            
        self.save()
        
        # Track status change
        ListingStatus.objects.create(
            listing=self,
            status=new_status,
            changed_by=changed_by,
            reason=reason or ''
        )
        
        return old_status != new_status
        
    def soft_delete(self, deleted_by=None, reason=None):
        """Soft delete the listing while preserving order data"""
        if self.status == 'deleted':
            return False
            
        changed = self.change_status('deleted', deleted_by, reason)
        if changed:
            ListingDeletion.objects.create(
                listing=self,
                deleted_by=deleted_by,
                reason=reason or '',
                has_active_orders=self.has_active_orders,
                preserve_data=self.preserve_data
            )
        return changed
    
    def clean(self):
        """Validate model data"""
        # Ensure FE is only enabled for vendors with permission
        if self.fe_enabled:
            try:
                fe_permission = self.vendor.vendorfepermission
                if not fe_permission.can_use_fe:
                    raise ValidationError(_('Vendor does not have permission to use Finalize Early'))
            except VendorFEPermission.DoesNotExist:
                raise ValidationError(_('Vendor does not have FE permissions configured'))
            
        # Validate private listing settings
        if self.status == 'private' and not self.pk:
            # Can't validate M2M before save
            if not hasattr(self, '_authorized_users'):
                raise ValidationError(_('Private listings must specify authorized users'))
        elif self.status == 'private' and self.pk:
            if not self.authorized_users.exists():
                raise ValidationError(_('Private listings must specify authorized users'))
            
        # Validate tag count
        if len(self.tags.split(',')) > 10:
            raise ValidationError(_('Maximum 10 tags allowed'))
            
        # Validate image sizes
        max_size = 400 * 1024  # 400KB
        for img in [self.main_image, self.image_2, self.image_3, 
                   self.image_4, self.image_5, self.image_6]:
            if img and img.size > max_size:
                raise ValidationError(_('Image size must not exceed 400KB'))
                
        # Check for active orders before status changes
        if self.pk:  # Only check if listing already exists
            has_active = self.orders.filter(
                status__in=['pending', 'processing', 'shipped']
            ).exists()
            if has_active != self.has_active_orders:
                self.has_active_orders = has_active
            if has_active:
                self.preserve_data = True
