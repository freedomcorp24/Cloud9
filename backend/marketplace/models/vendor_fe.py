from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class VendorFEPermission(models.Model):
    """Model for managing vendor Finalize Early permissions"""
    vendor = models.OneToOneField('VendorProfile', on_delete=models.CASCADE)
    
    # Automatic FE based on rating
    rating_threshold = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text=_('Minimum rating required for automatic FE permission')
    )
    min_orders = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text=_('Minimum completed orders required for FE eligibility')
    )
    min_account_age_days = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text=_('Minimum account age in days for FE eligibility')
    )
    
    def save(self, *args, **kwargs):
        if not self.rating_threshold:
            self.rating_threshold = settings.FE_RATING_THRESHOLD
        if not self.min_orders:
            self.min_orders = settings.FE_MIN_ORDERS
        if not self.min_account_age_days:
            self.min_account_age_days = settings.FE_MIN_ACCOUNT_AGE_DAYS
        super().save(*args, **kwargs)
    
    # Manual admin override
    fe_enabled = models.BooleanField(
        default=False,
        help_text=_('Manual override to enable/disable FE')
    )
    enabled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fe_permissions_granted'
    )
    enabled_at = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _('Vendor FE Permission')
        verbose_name_plural = _('Vendor FE Permissions')
        
    def __str__(self):
        status = 'Enabled' if self.fe_enabled else 'Disabled'
        return f"{self.vendor.user.username} - FE {status}"
        
    @property
    def can_use_fe(self):
        """Check if vendor can use FE based on criteria or manual override"""
        if self.fe_enabled:
            return True
            
        # Check automatic eligibility criteria
        account_age_days = (timezone.now() - self.vendor.user.date_joined).days
        meets_criteria = (
            self.vendor.rating >= self.rating_threshold and
            self.vendor.completed_orders_count >= self.min_orders and
            account_age_days >= self.min_account_age_days
        )
        return meets_criteria
