from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseForbidden, JsonResponse
from django.conf import settings
from ..models import LiveDeliveryTracking, DeliveryOrder

@login_required
def tracking_view(request, order_id):
    """View for tracking delivery status"""
    order = get_object_or_404(DeliveryOrder, id=order_id)
    
    # Ensure user has permission to view this order
    if not (request.user == order.vendor.user or request.user == order.customer):
        return HttpResponseForbidden(_("You don't have permission to view this order"))
    
    # Select template based on Tor status
    template = (
        'marketplace/delivery/tracking_tor.html' 
        if request.is_tor else 
        'marketplace/delivery/tracking.html'
    )
    
    context = {
        'order': order,
        'mapbox_token': None if request.is_tor else settings.MAPBOX_TOKEN
    }
    
    # Add tracking info if available and not using Tor
    if not request.is_tor and hasattr(order, 'live_tracking'):
        context['tracking'] = order.live_tracking
    
    return render(request, template, context)

@login_required
def update_status(request, order_id):
    """Update delivery status (Tor-compatible endpoint)"""
    if not request.method == 'POST':
        return HttpResponseForbidden(_("Method not allowed"))
        
    order = get_object_or_404(DeliveryOrder, id=order_id)
    
    # Ensure user has permission to update this order
    if request.user != order.vendor.user:
        return HttpResponseForbidden(_("Only the vendor can update delivery status"))
    
    status = request.POST.get('status')
    if status not in ['on_way', 'close', 'arrived']:
        return HttpResponseForbidden(_("Invalid status"))
        
    order.set_status(
        status,
        changed_by=request.user,
        notes=_('Driver marked as {}').format(status)
    )
    
    return redirect('marketplace:delivery-tracking', order_id=order.id)

@login_required
def toggle_tracking_mode(request, order_id):
    """Toggle between real-time and manual tracking modes"""
    if request.is_tor:
        return HttpResponseForbidden(_("Real-time tracking not available in Tor"))
        
    if not request.method == 'POST':
        return HttpResponseForbidden(_("Method not allowed"))
        
    order = get_object_or_404(DeliveryOrder, id=order_id)
    
    # Ensure user has permission
    if request.user != order.vendor.user:
        return HttpResponseForbidden(_("Only the vendor can update tracking mode"))
        
    tracking = get_object_or_404(LiveDeliveryTracking, order=order)
    mode = request.POST.get('mode')
    
    if mode not in ['realtime', 'manual']:
        return JsonResponse({'error': _('Invalid tracking mode')}, status=400)
        
    tracking.tracking_mode = mode
    tracking.save()
    
    return JsonResponse({
        'status': 'success',
        'mode': mode
    })
