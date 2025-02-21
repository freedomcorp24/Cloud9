from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token
from django.core.cache import cache
from ..models import DeliveryOrder, LiveDeliveryTracking, VendorProfile
from ..views.delivery import tracking_view, update_status

User = get_user_model()

class DeliveryTrackingTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client(enforce_csrf_checks=True)
        self.factory = RequestFactory()
        
        # Create users
        self.vendor = User.objects.create_user(
            username='testvendor',
            password='testpass123'
        )
        self.customer = User.objects.create_user(
            username='testcustomer',
            password='testpass123'
        )
        
        # Create vendor profile
        self.vendor_profile = VendorProfile.objects.create(
            user=self.vendor,
            business_name='Test Store'
        )
        
        # Create test order
        self.order = DeliveryOrder.objects.create(
            vendor=self.vendor_profile,
            customer=self.customer,
            status='pending'
        )
        
        # Create tracking for order
        self.tracking = LiveDeliveryTracking.objects.create(
            order=self.order,
            tracking_mode='manual',
            driver_name='Test Driver'
        )
        
        # Login users
        self.client.login(username='testvendor', password='testpass123')
        
        # Clear rate limit cache
        cache.clear()
    
    def test_tor_tracking_view(self):
        """Test tracking view in Tor browser"""
        response = self.client.get(
            reverse('marketplace:delivery-tracking', args=[self.order.id]),
            HTTP_USER_AGENT='Tor Browser'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'marketplace/delivery/tracking_tor.html')
        self.assertNotContains(response, '<script')
        self.assertNotContains(response, 'text/javascript')
        self.assertNotContains(response, 'websocket')
        
    def test_clearnet_tracking_view(self):
        """Test tracking view in regular browser"""
        response = self.client.get(
            reverse('marketplace:delivery-tracking', args=[self.order.id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'marketplace/delivery/tracking.html')
        self.assertContains(response, 'mapbox-gl.js')
        
    def test_tor_status_update(self):
        """Test status updates in Tor browser"""
        # Get CSRF token
        csrf_token = get_token(self.client.get('/').wsgi_request)
        
        response = self.client.post(
            reverse('marketplace:tor-delivery-status', args=[self.order.id]),
            {'status': 'on_way'},
            HTTP_USER_AGENT='Tor Browser',
            HTTP_X_CSRFTOKEN=csrf_token
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'on_way')
        
    def test_tor_status_update_without_csrf(self):
        """Test status updates fail without CSRF token"""
        response = self.client.post(
            reverse('marketplace:tor-delivery-status', args=[self.order.id]),
            {'status': 'on_way'},
            HTTP_USER_AGENT='Tor Browser'
        )
        
        self.assertEqual(response.status_code, 403)  # CSRF check failed
        
    def test_tor_tracking_mode_blocked(self):
        """Test real-time tracking mode is blocked in Tor"""
        csrf_token = get_token(self.client.get('/').wsgi_request)
        
        response = self.client.post(
            reverse('marketplace:toggle-tracking-mode', args=[self.order.id]),
            {'mode': 'realtime'},
            HTTP_USER_AGENT='Tor Browser',
            HTTP_X_CSRFTOKEN=csrf_token
        )
        
        self.assertEqual(response.status_code, 403)
        self.tracking.refresh_from_db()
        self.assertEqual(self.tracking.tracking_mode, 'manual')
        
    def test_clearnet_tracking_mode_toggle(self):
        """Test tracking mode toggle in regular browser"""
        csrf_token = get_token(self.client.get('/').wsgi_request)
        
        response = self.client.post(
            reverse('marketplace:toggle-tracking-mode', args=[self.order.id]),
            {'mode': 'realtime'},
            HTTP_X_CSRFTOKEN=csrf_token
        )
        
        self.assertEqual(response.status_code, 200)
        self.tracking.refresh_from_db()
        self.assertEqual(self.tracking.tracking_mode, 'realtime')
        
    def test_javascript_middleware_tor(self):
        """Test JavaScript blocking middleware in Tor"""
        response = self.client.get(
            reverse('marketplace:delivery-tracking', args=[self.order.id]),
            HTTP_ACCEPT='text/javascript',
            HTTP_USER_AGENT='Tor Browser'
        )
        
        self.assertEqual(response.status_code, 403)
        
    def test_unauthorized_access(self):
        """Test unauthorized access is blocked"""
        unauthorized = User.objects.create_user(
            username='unauthorized',
            password='testpass123'
        )
        self.client.login(username='unauthorized', password='testpass123')
        
        response = self.client.get(
            reverse('marketplace:delivery-tracking', args=[self.order.id])
        )
        
        self.assertEqual(response.status_code, 403)
        
    def test_rate_limiting(self):
        """Test rate limiting on status updates"""
        csrf_token = get_token(self.client.get('/').wsgi_request)
        
        # Make multiple requests quickly
        for _ in range(5):
            response = self.client.post(
                reverse('marketplace:tor-delivery-status', args=[self.order.id]),
                {'status': 'on_way'},
                HTTP_USER_AGENT='Tor Browser',
                HTTP_X_CSRFTOKEN=csrf_token
            )
            
        # Next request should be rate limited
        response = self.client.post(
            reverse('marketplace:tor-delivery-status', args=[self.order.id]),
            {'status': 'on_way'},
            HTTP_USER_AGENT='Tor Browser',
            HTTP_X_CSRFTOKEN=csrf_token
        )
        
        self.assertEqual(response.status_code, 429)  # Too Many Requests
