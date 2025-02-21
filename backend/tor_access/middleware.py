from django.http import HttpResponse

class HttpResponseTooManyRequests(HttpResponse):
    status_code = 429
from django.core.cache import cache
from django.conf import settings
import time

class TorAccessMiddleware:
    """
    Middleware to handle Tor access with rate limiting
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit_window = 300  # 5 minutes
        self.max_requests = 30  # Maximum requests per window

    def __call__(self, request):
        # Check if request is from Tor
        is_tor = self._is_tor_request(request)
        request.is_tor = is_tor

        if is_tor:
            # Apply stricter rate limiting for Tor requests
            if not self._check_rate_limit(request):
                return HttpResponseTooManyRequests("Rate limit exceeded")

        response = self.get_response(request)
        return response

    def _is_tor_request(self, request):
        """
        Check if request is coming from Tor network
        """
        # Check common Tor exit node headers
        tor_headers = [
            'x-tor',
            'via',
            'forwarded',
            'x-forwarded-for'
        ]
        
        # Check user agent for Tor Browser
        user_agent = request.headers.get('user-agent', '').lower()
        if 'tor' in user_agent:
            return True

        # Check headers that might indicate Tor traffic
        for header in tor_headers:
            if header in request.headers:
                value = request.headers[header].lower()
                if 'tor' in value or '.onion' in value:
                    return True

        return False

    def _check_rate_limit(self, request):
        """
        Check if request exceeds rate limit
        """
        client_id = request.META.get('REMOTE_ADDR', '')
        cache_key = f'tor_ratelimit:{client_id}'
        
        now = time.time()
        request_times = cache.get(cache_key, [])
        
        # Clean old requests
        request_times = [t for t in request_times if now - t < self.rate_limit_window]
        
        if len(request_times) >= self.max_requests:
            return False
        
        request_times.append(now)
        cache.set(cache_key, request_times, self.rate_limit_window)
        
        return True
