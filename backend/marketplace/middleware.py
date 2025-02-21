from django.http import HttpResponse

class HttpResponseTooManyRequests(HttpResponse):
    status_code = 429
from django.core.cache import cache
import time

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
