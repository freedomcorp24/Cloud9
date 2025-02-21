from django.http import HttpResponseForbidden
from django.utils.translation import gettext_lazy as _

class TorJavaScriptMiddleware:
    """Middleware to block JavaScript requests in Tor version"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        """Block JavaScript requests if using Tor"""
        if request.is_tor:
            # Check content type in Accept header
            if 'text/javascript' in request.META.get('HTTP_ACCEPT', ''):
                return HttpResponseForbidden(_('JavaScript not allowed in Tor version'))
                
            # Check file extensions in path
            if request.path.endswith(('.js', '.mjs')):
                return HttpResponseForbidden(_('JavaScript files not allowed in Tor version'))
                
            # Check script tags in POST data
            if request.method == 'POST' and '<script' in request.body.decode('utf-8', errors='ignore'):
                return HttpResponseForbidden(_('Script tags not allowed in Tor version'))
                
        return self.get_response(request)
