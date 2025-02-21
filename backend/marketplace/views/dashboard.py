from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
from ..models import DeliveryOrder, OrderStatus
from ..decorators import require_vendor_bond

class VendorDashboardView(LoginRequiredMixin, ListView):
    """Main vendor dashboard view showing order status sections"""
    template_name = 'marketplace/dashboard/vendor_dashboard.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        """Get all orders for current vendor"""
        return DeliveryOrder.objects.filter(
            vendor=self.request.user.vendor_profile
        ).select_related(
            'status_history'
        ).order_by('-created_at')
        
    def get_context_data(self, **kwargs):
        """Add order status sections to context"""
        context = super().get_context_data(**kwargs)
        orders = self.get_queryset()
        
        # Get latest status for each order
        status_map = {}
        for order in orders:
            try:
                latest_status = order.status_history.latest()
                status_map[order.id] = latest_status.status
            except OrderStatus.DoesNotExist:
                status_map[order.id] = 'pending'
        
        # Filter orders by status
        context.update({
            'pending_orders': [
                order for order in orders 
                if status_map[order.id] == 'pending'
            ],
            'accepted_orders': [
                order for order in orders 
                if status_map[order.id] == 'accepted'
            ],
            'shipped_orders': [
                order for order in orders 
                if status_map[order.id] == 'shipped'
            ],
            'finalized_orders': [
                order for order in orders 
                if status_map[order.id] == 'finalized'
            ],
            'disputed_sales': [
                order for order in orders 
                if status_map[order.id] == 'disputed'
            ],
            'cancelled_sales': [
                order for order in orders 
                if status_map[order.id] == 'cancelled'
            ],
            'open_sales': [
                order for order in orders
                if status_map[order.id] in ['pending', 'accepted', 'shipped']
            ]
        })
        
        return context

class OrderDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a specific order"""
    model = DeliveryOrder
    template_name = 'marketplace/dashboard/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        """Ensure vendor can only view their own orders"""
        return super().get_queryset().filter(
            vendor=self.request.user.vendor_profile
        )
        
    def get_context_data(self, **kwargs):
        """Add status history to context"""
        context = super().get_context_data(**kwargs)
        context['status_history'] = self.object.status_history.all().order_by('-changed_at')
        return context
