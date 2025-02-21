from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ..models import VendorProfile

def process_vendor_bond_payment(vendor: VendorProfile, payment_amount: float) -> bool:
    """Process vendor bond payment"""
    if payment_amount < vendor.bond_amount:
        raise ValidationError(_('Payment amount must be at least €500'))
        
    if vendor.bond_paid:
        raise ValidationError(_('Vendor bond has already been paid'))
        
    vendor.bond_paid = True
    vendor.bond_paid_at = timezone.now()
    vendor.save()
    
    return True

def check_vendor_dashboard_access(vendor: VendorProfile) -> bool:
    """Check if vendor has access to dashboard features"""
    return vendor.bond_paid or vendor.bond_waived
