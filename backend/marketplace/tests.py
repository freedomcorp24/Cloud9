from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from .middleware import RateLimitMiddleware

class RateLimitMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RateLimitMiddleware(lambda r: HttpResponse())

    def test_normal_request(self):
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_rate_limit_exceeded(self):
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        # Make multiple requests to exceed rate limit
        for _ in range(101):
            response = self.middleware(request)
        
        self.assertEqual(response.status_code, 429)

    def test_admin_bypass(self):
        request = self.factory.get('/admin/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
