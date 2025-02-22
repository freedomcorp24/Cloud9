from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone

class VendorProfile(models.Model):
    """
    Vendor profile with bond requirements and rating system
    """
    VENDOR_STATUS = [
        ('pending', _('Pending Bond')),
        ('active', _('Active')),
        ('suspended', _('Suspended')),
        ('banned', _('Banned'))
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor_profile'
    )
    
    # Bond management
    bond_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_('Amount of vendor bond paid')
    )
    bond_required = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('500.00'),  # €500 default bond
        help_text=_('Required bond amount')
    )
    bond_waived = models.BooleanField(
        default=False,
        help_text=_('Whether bond requirement has been waived by admin')
    )
    bond_waived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bond_waivers_granted'
    )
    
    # Vendor status and ratings
    status = models.CharField(
        max_length=20,
        choices=VENDOR_STATUS,
        default='pending'
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_ratings = models.PositiveIntegerField(default=0)
    
    # Permissions and features
    can_finalize_early = models.BooleanField(
        default=False,
        help_text=_('Permission to finalize orders early')
    )
    finalize_early_threshold = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('4.50'),  # Minimum 4.5/5.0 rating required
        help_text=_('Rating threshold for automatic finalize early permission')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = _('Vendor Profile')
        verbose_name_plural = _('Vendor Profiles')
        
    def __str__(self):
        return f"{self.user.username}'s vendor profile"
        
    def has_paid_bond(self):
        """Check if vendor has paid the required bond"""
        return self.bond_paid >= self.bond_required or self.bond_waived
        
    def can_access_vendor_features(self):
        """Check if vendor can access vendor features"""
        return self.status == 'active' and self.has_paid_bond()
        
    def update_rating(self, new_rating):
        """Update vendor rating with new rating value"""
        if not (0 <= new_rating <= 5):
            raise ValueError("Rating must be between 0 and 5")
            
        total = self.rating * self.total_ratings
        self.total_ratings += 1
        self.rating = (total + new_rating) / self.total_ratings
        
        # Check rating threshold for finalize early permission
        if not self.can_finalize_early and self.rating >= self.finalize_early_threshold:
            self.can_finalize_early = True
            
        self.save()
        
    def record_activity(self):
        """Update last active timestamp"""
        self.last_active = timezone.now()
        self.save()
