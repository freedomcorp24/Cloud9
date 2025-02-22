from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.functional import wraps
from django.utils import timezone
from django.conf import settings

class TransactionPINMiddleware:
    """Middleware to enforce PIN verification for sensitive operations"""
    
    PROTECTED_PATHS = [
        '/checkout/',
        '/wallet/withdraw/',
        '/orders/release/',
        '/profile/security/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)
            
        path = request.path_info.lstrip('/')
        
        # Check if path requires PIN
        requires_pin = any(path.startswith(p.lstrip('/')) for p in self.PROTECTED_PATHS)
        
        if requires_pin and request.method == 'POST':
            pin = request.POST.get('transaction_pin')
            
            if not pin:
                messages.error(request, _('Transaction PIN required'))
                return redirect(request.path)
                
            profile = request.user.user_profile
            if not profile.verify_pin(pin):
                if profile.pin_locked_until:
                    messages.error(
                        request,
                        _('PIN locked. Try again in {} minutes').format(
                            (profile.pin_locked_until - timezone.now()).seconds // 60
                        )
                    )
                else:
                    messages.error(
                        request,
                        _('Invalid PIN. {} attempts remaining').format(
                            3 - profile.failed_pin_attempts
                        )
                    )
                return redirect(request.path)
                
        return self.get_response(request)

def require_pin(view_func):
    """Decorator to require PIN verification for a view"""
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
            
        if request.method == 'POST':
            pin = request.POST.get('transaction_pin')
            
            if not pin:
                messages.error(request, _('Transaction PIN required'))
                return redirect(request.path)
                
            profile = request.user.user_profile
            if not profile.verify_pin(pin):
                if profile.pin_locked_until:
                    messages.error(
                        request,
                        _('PIN locked. Try again in {} minutes').format(
                            (profile.pin_locked_until - timezone.now()).seconds // 60
                        )
                    )
                else:
                    messages.error(
                        request,
                        _('Invalid PIN. {} attempts remaining').format(
                            3 - profile.failed_pin_attempts
                        )
                    )
                return redirect(request.path)
                
        return view_func(request, *args, **kwargs)
        
    return wrapped
