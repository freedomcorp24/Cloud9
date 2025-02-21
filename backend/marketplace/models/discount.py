from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class DiscountCode(models.Model):
    """Model for vendor discount codes"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('deleted', 'Deleted')
    ]
    
    vendor = models.ForeignKey(
        'VendorProfile',
        on_delete=models.CASCADE,
        related_name='discount_codes'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text=_('Unique discount code')
    )
    description = models.TextField(
        help_text=_('Description of the discount')
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text=_('Discount percentage (0-100)')
    )
    valid_from = models.DateTimeField(
        default=timezone.now,
        help_text=_('When this discount becomes valid')
    )
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When this discount expires (optional)')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text=_('Current status of the discount code')
    )
    max_uses = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text=_('Maximum number of times this code can be used (optional)')
    )
    current_uses = models.IntegerField(
        default=0,
        help_text=_('Number of times this code has been used')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Discount Code')
        verbose_name_plural = _('Discount Codes')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.code} ({self.get_status_display()})"
        
    @property
    def is_valid(self):
        """Check if discount code is currently valid"""
        now = timezone.now()
        
        if self.status != 'active':
            return False
            
        if self.valid_until and now > self.valid_until:
            return False
            
        if now < self.valid_from:
            return False
            
        if self.max_uses and self.current_uses >= self.max_uses:
            return False
            
        return True
        
    def soft_delete(self):
        """Soft delete the discount code"""
        self.status = 'deleted'
        self.save()
