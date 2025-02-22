from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from ..models.order import DeliveryOrder
from ..models.driver_tracking import DriverLocation, DeliveryStatus
from decimal import Decimal

class OrderTrackingView(View):
    """View for tracking order delivery status"""
    template_name_tor = 'tor/order/tracking.html'
    template_name_clearnet = 'clearnet/order/tracking.html'
    
    @method_decorator(login_required)
    def get(self, request, order_id):
        order = get_object_or_404(
            DeliveryOrder.objects.select_related('driver_location'),
            id=order_id,
            user=request.user
        )
        
        # Use appropriate template based on access method
        template = (
            self.template_name_tor 
            if request.is_tor 
            else self.template_name_clearnet
        )
        
        context = {
            'order': order,
            'maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        }
        return render(request, template, context)

class UpdateDeliveryStatusView(View):
    """View for drivers to update delivery status"""
    
    @method_decorator(login_required)
    def post(self, request, order_id):
        order = get_object_or_404(
            DeliveryOrder,
            id=order_id,
            driver=request.user
        )
        
        status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if status not in dict(DeliveryStatus.STATUS_CHOICES):
            messages.error(request, _('Invalid status'))
            return redirect('order:tracking', order_id=order_id)
            
        # Create status update
        DeliveryStatus.objects.create(
            order=order,
            driver=request.user,
            status=status,
            notes=notes,
            latitude=request.POST.get('latitude'),
            longitude=request.POST.get('longitude')
        )
        
        messages.success(request, _('Status updated successfully'))
        return redirect('order:tracking', order_id=order_id)

class ToggleTrackingView(View):
    """View for drivers to toggle location tracking"""
    
    @method_decorator(login_required)
    def post(self, request, order_id):
        order = get_object_or_404(
            DeliveryOrder,
            id=order_id,
            driver=request.user
        )
        
        enabled = request.POST.get('tracking_enabled') == 'on'
        
        # Update or create driver location
        location, _ = DriverLocation.objects.get_or_create(
            driver=request.user,
            defaults={
                'tracking_status': 'enabled' if enabled else 'disabled',
                'latitude': Decimal('0'),
                'longitude': Decimal('0')
            }
        )
        
        if location.tracking_status != ('enabled' if enabled else 'disabled'):
            location.tracking_status = 'enabled' if enabled else 'disabled'
            location.save()
        
        messages.success(
            request,
            _('Location tracking enabled') if enabled else _('Location tracking disabled')
        )
        return redirect('order:tracking', order_id=order_id)

class UpdateLocationView(View):
    """View for updating driver location"""
    
    @method_decorator(login_required)
    def post(self, request):
        try:
            latitude = Decimal(request.POST['latitude'])
            longitude = Decimal(request.POST['longitude'])
            accuracy = float(request.POST.get('accuracy', 0))
            
            if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                return JsonResponse({'error': 'Invalid coordinates'}, status=400)
                
            location, _ = DriverLocation.objects.get_or_create(
                driver=request.user,
                defaults={
                    'tracking_status': 'enabled',
                    'latitude': latitude,
                    'longitude': longitude,
                    'accuracy': accuracy
                }
            )
            
            if location.tracking_status == 'enabled':
                location.latitude = latitude
                location.longitude = longitude
                location.accuracy = accuracy
                location.save()
                
            return JsonResponse({'status': 'success'})
            
        except (KeyError, ValueError, TypeError):
            return JsonResponse({'error': 'Invalid data'}, status=400)
