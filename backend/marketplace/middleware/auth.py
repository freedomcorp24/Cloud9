from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import resolve
from django.utils import timezone
from ..services.auth import TransactionPINService

class TransactionPINMiddleware:
    """Middleware to enforce transaction PIN requirements"""
    EXEMPT_URLS = [
        'change_pin',
        'change_password',
        'verify_pgp',
        'pgp_2fa'
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.pin_service = TransactionPINService()
        
    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)
            
        # Check if accessing transaction-related URL
        url_name = resolve(request.path_info).url_name
        if not url_name or not self._requires_pin(url_name):
            return self.get_response(request)
            
        # Skip PIN check for exempt URLs
        if url_name in self.EXEMPT_URLS:
            return self.get_response(request)
            
        # Check if PIN is set
        if not request.user.profile.transaction_pin:
            messages.warning(
                request,
                _('You must set up a transaction PIN to perform this action')
            )
            return redirect('marketplace:change_pin')
            
        # Check if PIN is locked
        if (request.user.profile.pin_locked_until and 
            request.user.profile.pin_locked_until > timezone.now()):
            messages.error(
                request,
                _('Your PIN is locked due to too many failed attempts. '
                  'Please try again later.')
            )
            return redirect('marketplace:profile')
            
        return self.get_response(request)
        
    def _requires_pin(self, url_name: str) -> bool:
        """Check if URL requires PIN verification"""
        pin_required_urls = [
            'purchase',
            'release_funds',
            'withdraw',
            'instant_delivery'
        ]
        return any(url_name.startswith(prefix) for prefix in pin_required_urls)
