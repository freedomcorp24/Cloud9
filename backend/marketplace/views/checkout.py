from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.utils import timezone
from ..models.cart import Cart
from ..models.checkout import CheckoutSession
from ..forms.checkout import PINVerificationForm, DeliveryDetailsForm

class CheckoutView(LoginRequiredMixin, TemplateView):
    """View for checkout process"""
    template_name = 'clearnet/checkout/checkout.html'
    
    def get_template_names(self):
        """Return appropriate template based on request type"""
        if getattr(self.request, 'is_tor', False):
            return ['tor/checkout/checkout.html']
        return [self.template_name]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        carts = Cart.objects.filter(user=self.request.user).prefetch_related('items')
        
        # Get or create checkout session for each cart
        checkout_sessions = []
        total = 0
        for cart in carts:
            session, _ = CheckoutSession.objects.get_or_create(
                user=self.request.user,
                cart=cart
            )
            checkout_sessions.append(session)
            total += sum(item.total_price for item in cart.items.all())
            
        context.update({
            'carts': carts,
            'total': total,
            'checkout_sessions': checkout_sessions,
            'pin_form': PINVerificationForm(self.request.user),
            'delivery_form': DeliveryDetailsForm()
        })
        return context

class PINVerificationView(LoginRequiredMixin, View):
    """View for verifying transaction PIN"""
    
    def post(self, request):
        form = PINVerificationForm(request.user, request.POST)
        if form.is_valid():
            # Verify PIN for all active checkout sessions
            sessions = CheckoutSession.objects.filter(user=request.user)
            for session in sessions:
                session.verify_pin(form.cleaned_data['pin'])
            messages.success(request, _('PIN verified successfully.'))
        else:
            for error in form.errors['pin']:
                messages.error(request, error)
                
        return redirect('checkout:index')

class DeliveryDetailsView(LoginRequiredMixin, View):
    """View for collecting delivery details"""
    
    @transaction.atomic
    def post(self, request):
        # Verify all sessions have valid PIN verification
        sessions = CheckoutSession.objects.filter(user=request.user)
        if not all(session.is_pin_verification_valid() for session in sessions):
            messages.error(request, _('PIN verification required.'))
            return redirect('checkout:index')
            
        form = DeliveryDetailsForm(request.POST)
        if form.is_valid():
            delivery_type = form.cleaned_data['delivery_type']
            completion_window = form.cleaned_data['completion_window']
            delivery_address = form.cleaned_data['delivery_address']
            delivery_instructions = form.cleaned_data['delivery_instructions']
            
            try:
                # Update all sessions with delivery details
                for session in sessions:
                    session.delivery_type = delivery_type
                    session.completion_window = completion_window
                    session.delivery_address = delivery_address
                    session.delivery_instructions = delivery_instructions
                    session.save()
                    
                    # Create order from session
                    order = session.create_order()
                    
                messages.success(request, _('Orders created successfully.'))
                return redirect('order:list')  # Redirect to order list
            except ValueError as e:
                messages.error(request, str(e))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
                    
        return redirect('checkout:index')
