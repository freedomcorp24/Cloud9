from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from ..services.auth import TransactionPINService
from ..forms.auth import (
    TransactionPINForm,
    CustomPasswordChangeForm
)

class TransactionPINView(LoginRequiredMixin, FormView):
    """View for setting transaction PIN"""
    template_name = 'marketplace/auth/change_pin.html'
    form_class = TransactionPINForm
    success_url = reverse_lazy('marketplace:dashboard')
    
    def form_valid(self, form):
        pin_service = TransactionPINService()
        if pin_service.set_pin(self.request.user.profile, form.cleaned_data['pin']):
            messages.success(self.request, _('Transaction PIN updated successfully'))
            return super().form_valid(form)
            
        messages.error(self.request, _('Failed to update transaction PIN'))
        return self.form_invalid(form)

class CustomPasswordChangeView(PasswordChangeView):
    """Custom password change view"""
    template_name = 'marketplace/auth/change_password.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('marketplace:dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Password changed successfully'))
        return response
