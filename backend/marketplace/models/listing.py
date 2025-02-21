from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError

class ListingStatus(models.Model):
    """Model for tracking listing status changes"""
    listing = models.ForeignKey('ProductListing', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('deleted', 'Deleted')
        ]
    )
    changed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='listing_status_changes'
    )
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Listing Status')
        verbose_name_plural = _('Listing Statuses')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.listing.title} - {self.status}"

class ListingDeletion(models.Model):
    """Model for tracking listing deletions"""
    listing = models.OneToOneField('ProductListing', on_delete=models.CASCADE)
    deleted_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='deleted_listings'
    )
    deleted_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()
    has_active_orders = models.BooleanField(default=False)
    preserve_data = models.BooleanField(
        default=True,
        help_text=_('Preserve listing data for order history')
    )
    
    class Meta:
        verbose_name = _('Listing Deletion')
        verbose_name_plural = _('Listing Deletions')
    
    def __str__(self):
        return f"Deleted: {self.listing.title}"
    
    def save(self, *args, **kwargs):
        # Check for active orders before deletion
        self.has_active_orders = self.listing.orders.filter(
            status__in=['pending', 'processing', 'shipped']
        ).exists()
        
        # Force preserve_data if there are any orders
        if self.listing.orders.exists():
            self.preserve_data = True
            
        super().save(*args, **kwargs)
