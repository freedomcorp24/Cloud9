from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

def require_vendor_bond(view_func):
    """Decorator to require vendor bond payment or waiver"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'vendor_profile'):
            messages.error(request, _('You must be a vendor to access this page'))
            return redirect('marketplace:home')
            
        vendor = request.user.vendor_profile
        if not vendor.can_access_dashboard:
            messages.warning(
                request,
                _('You must pay the €500 vendor bond or request a waiver to access the vendor dashboard')
            )
            return redirect('support:bond_waiver_request')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view
