from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import resolve
from django.utils import timezone
import base64

class HttpResponseTooManyRequests(HttpResponse):
    status_code = 429

class BasicAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DJANGO_ENV == 'test':
            if 'HTTP_AUTHORIZATION' in request.META:
                auth = request.META['HTTP_AUTHORIZATION'].split()
                if len(auth) == 2 and auth[0].lower() == "basic":
                    username, password = base64.b64decode(auth[1]).decode().split(':')
                    if (username == settings.BASIC_AUTH_USERNAME and 
                        password == settings.BASIC_AUTH_PASSWORD):
                        return self.get_response(request)
            
            response = HttpResponse('Unauthorized', status=401)
            response['WWW-Authenticate'] = 'Basic realm="Test Environment"'
            return response
        
        return self.get_response(request)
from django.core.cache import cache
import time

class VendorBondMiddleware:
    """Middleware to enforce vendor bond requirements"""
    EXEMPT_URLS = [
        'bond_waiver_request',
        'vendor_bond_payment',
        'support_dashboard'
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)
            
        # Check if accessing vendor-specific URL
        url_name = resolve(request.path_info).url_name
        if not url_name or not url_name.startswith('vendor_'):
            return self.get_response(request)
            
        # Skip bond check for exempt URLs
        if url_name in self.EXEMPT_URLS:
            return self.get_response(request)
            
        # Check vendor bond status
        if hasattr(request.user, 'vendor_profile'):
            vendor = request.user.vendor_profile
            if not vendor.can_access_dashboard:
                messages.warning(
                    request,
                    _('You must pay the €500 vendor bond or request a waiver to access vendor features')
                )
                return redirect('support:bond_waiver_request')
                
        return self.get_response(request)

class RateLimitMiddleware:
    """
    Global rate limiting middleware for marketplace
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit_window = 60  # 1 minute
        self.max_requests = 100  # Maximum requests per minute per IP

    def __call__(self, request):
        # Skip rate limiting for admin and static/media URLs
        if request.path.startswith(('/admin/', '/static/', '/media/')):
            return self.get_response(request)

        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        if not self._check_rate_limit(client_ip):
            return HttpResponseTooManyRequests("Rate limit exceeded")

        return self.get_response(request)

    def _get_client_ip(self, request):
        """
        Get client IP from request, handling proxies
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _check_rate_limit(self, client_ip):
        """
        Check if request exceeds rate limit using Redis
        """
        cache_key = f'ratelimit:{client_ip}'
        now = time.time()
        
        # Get current request count and timestamp
        request_data = cache.get(cache_key)
        
        if request_data is None:
            # First request from this IP
            cache.set(cache_key, {'count': 1, 'window_start': now}, self.rate_limit_window)
            return True
            
        count = request_data.get('count', 0)
        window_start = request_data.get('window_start', now)
        
        # Check if we're in a new window
        if now - window_start >= self.rate_limit_window:
            cache.set(cache_key, {'count': 1, 'window_start': now}, self.rate_limit_window)
            return True
            
        # Check if limit exceeded
        if count >= self.max_requests:
            return False
            
        # Increment request count
        request_data['count'] = count + 1
        cache.set(cache_key, request_data, self.rate_limit_window)
        return True
