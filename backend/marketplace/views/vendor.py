from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from ..models import VendorProfile
from ..decorators import require_vendor_bond
from ..services.vendor import process_vendor_bond_payment
from django.utils.decorators import method_decorator

class VendorBondPaymentView(LoginRequiredMixin, View):
    """Handle vendor bond payment processing"""
    def post(self, request, *args, **kwargs):
        try:
            vendor = request.user.vendor_profile
            process_vendor_bond_payment(vendor, 500.00)
            messages.success(request, _('Vendor bond payment processed successfully'))
            return redirect('marketplace:vendor_dashboard')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('marketplace:vendor_bond_payment')

@method_decorator(require_vendor_bond, name='dispatch')
class VendorDashboardView(LoginRequiredMixin, TemplateView):
    """Main vendor dashboard view"""
    template_name = 'marketplace/vendor_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = self.request.user.vendor_profile
        context.update({
            'vendor': vendor,
            'bond_paid': vendor.bond_paid,
            'bond_waived': vendor.bond_waived,
            'pending_orders': vendor.orders.filter(status='pending'),
            'accepted_orders': vendor.orders.filter(status='accepted'),
            'shipped_orders': vendor.orders.filter(status='shipped'),
            'finalized_orders': vendor.orders.filter(status='finalized'),
            'disputed_sales': vendor.orders.filter(status='disputed'),
            'cancelled_sales': vendor.orders.filter(status='cancelled')
        })
        return context
