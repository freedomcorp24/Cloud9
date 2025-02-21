from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from .middleware import TorAccessMiddleware

class TorAccessMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TorAccessMiddleware(lambda r: HttpResponse())

    def test_non_tor_request(self):
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_tor_request_detection(self):
        request = self.factory.get('/')
        request.META['HTTP_USER_AGENT'] = 'Tor Browser'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        response = self.middleware(request)
        self.assertTrue(hasattr(request, 'is_tor'))
        self.assertTrue(request.is_tor)

    def test_rate_limit_exceeded(self):
        request = self.factory.get('/')
        request.META['HTTP_USER_AGENT'] = 'Tor Browser'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        # Make multiple requests to exceed rate limit
        for _ in range(31):
            response = self.middleware(request)
        
        self.assertEqual(response.status_code, 429)
