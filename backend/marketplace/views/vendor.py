from django.views.generic import View, TemplateView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.utils import timezone
from decimal import Decimal
from ..models.vendor_profile import VendorProfile
from ..middleware.vendor import require_vendor_bond, require_vendor_rating
from django.utils.decorators import method_decorator

class VendorRegistrationView(LoginRequiredMixin, CreateView):
    """Register as a vendor"""
    model = VendorProfile
    template_name = 'marketplace/vendor/register.html'
    success_url = reverse_lazy('vendor:bond_payment')
    fields = []  # No fields needed as we just create the profile
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class VendorBondPaymentView(LoginRequiredMixin, TemplateView):
    """Handle vendor bond payment processing"""
    template_name = 'marketplace/vendor/bond_payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = self.request.user.vendor_profile
        context.update({
            'bond_required': vendor.bond_required,
            'bond_paid': vendor.bond_paid,
            'remaining_amount': vendor.bond_required - vendor.bond_paid,
            'bond_waived': vendor.bond_waived
        })
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            amount = Decimal(request.POST.get('amount', '0'))
            if amount <= 0:
                raise ValueError(_("Invalid payment amount"))
                
            vendor = request.user.vendor_profile
            vendor.bond_paid += amount
            
            if vendor.has_paid_bond():
                vendor.status = 'active'
                messages.success(request, _('Bond payment complete. You can now access vendor features.'))
            else:
                messages.info(
                    request,
                    _('Bond payment received. Remaining amount: €{:.2f}').format(
                        vendor.bond_required - vendor.bond_paid
                    )
                )
                
            vendor.save()
            return redirect('vendor:dashboard')
            
        except (ValueError, TypeError) as e:
            messages.error(request, str(e))
            return self.get(request, *args, **kwargs)

@method_decorator(require_vendor_bond, name='dispatch')
class VendorDashboardView(LoginRequiredMixin, TemplateView):
    """Main vendor dashboard view"""
    template_name = 'marketplace/vendor/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = self.request.user.vendor_profile
        context.update({
            'vendor': vendor,
            'bond_paid': vendor.bond_paid,
            'bond_waived': vendor.bond_waived,
            'rating': vendor.rating,
            'total_ratings': vendor.total_ratings,
            'can_finalize_early': vendor.can_finalize_early,
            'finalize_early_threshold': vendor.finalize_early_threshold,
            'pending_orders': vendor.orders.filter(status='pending'),
            'accepted_orders': vendor.orders.filter(status='accepted'),
            'shipped_orders': vendor.orders.filter(status='shipped'),
            'finalized_orders': vendor.orders.filter(status='finalized'),
            'disputed_sales': vendor.orders.filter(status='disputed'),
            'cancelled_sales': vendor.orders.filter(status='cancelled')
        })
        return context

class AdminVendorManagementView(UserPassesTestMixin, TemplateView):
    """Admin interface for vendor management"""
    template_name = 'marketplace/vendor/admin_management.html'
    
    def test_func(self):
        return self.request.user.is_staff
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vendors'] = VendorProfile.objects.all().order_by('-created_at')
        return context
        
    def post(self, request, *args, **kwargs):
        vendor_id = request.POST.get('vendor_id')
        action = request.POST.get('action')
        
        vendor = get_object_or_404(VendorProfile, id=vendor_id)
        
        if action == 'waive_bond':
            vendor.bond_waived = True
            vendor.bond_waived_by = request.user
            vendor.status = 'active'
            messages.success(request, _('Bond requirement waived for {}').format(vendor.user.username))
            
        elif action == 'revoke_waiver':
            vendor.bond_waived = False
            vendor.bond_waived_by = None
            if not vendor.has_paid_bond():
                vendor.status = 'pending'
            messages.success(request, _('Bond waiver revoked for {}').format(vendor.user.username))
            
        elif action == 'suspend':
            vendor.status = 'suspended'
            messages.success(request, _('Vendor {} has been suspended').format(vendor.user.username))
            
        elif action == 'activate':
            if vendor.has_paid_bond():
                vendor.status = 'active'
                messages.success(request, _('Vendor {} has been activated').format(vendor.user.username))
            else:
                messages.error(request, _('Cannot activate vendor without bond payment or waiver'))
                
        vendor.save()
        return self.get(request, *args, **kwargs)
