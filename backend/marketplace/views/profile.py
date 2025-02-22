from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from ..mixins import CurrencyDisplayMixin
from ..models.user_profile import UserProfile
from ..forms import ProfileUpdateForm, SecuritySettingsForm, PGPVerificationForm

class ProfileView(LoginRequiredMixin, CurrencyDisplayMixin, TemplateView):
    """View for displaying user profile"""
    template_name = 'clearnet/profile/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.user_profile
        
        context.update({
            'profile': profile,
            'online_status': profile.get_online_status(),
            'recent_orders': self.request.user.orders.order_by('-created_at')[:5],
            'has_2fa': profile.pgp_verified,
            'CURRENCIES': [choice[0] for choice in profile._meta.get_field('preferred_currency').choices],
            'COUNTRIES': [choice[0] for choice in profile._meta.get_field('country').choices]
        })
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating profile information"""
    model = UserProfile
    form_class = ProfileUpdateForm
    template_name = 'clearnet/profile/profile_edit.html'
    success_url = reverse_lazy('profile:profile')
    
    def get_object(self):
        return self.request.user.user_profile
        
    def form_valid(self, form):
        messages.success(self.request, _('Profile updated successfully.'))
        return super().form_valid(form)

class SecuritySettingsView(LoginRequiredMixin, TemplateView):
    """View for managing security settings"""
    template_name = 'clearnet/profile/security_settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.user_profile
        
        context.update({
            'profile': profile,
            'security_form': SecuritySettingsForm(instance=profile),
            'pgp_form': PGPVerificationForm(user_profile=profile) if profile.pgp_key and not profile.pgp_verified else None
        })
        return context
        
    def post(self, request, *args, **kwargs):
        profile = request.user.user_profile
        action = request.POST.get('action')
        
        if action == 'security':
            form = SecuritySettingsForm(request.POST, instance=profile)
            if form.is_valid():
                if form.cleaned_data.get('new_pin'):
                    profile.transaction_pin = form.cleaned_data['new_pin']
                    profile.pin_last_changed = timezone.now()
                    profile.failed_pin_attempts = 0
                    profile.pin_locked_until = None
                
                if form.cleaned_data.get('pgp_key'):
                    profile.pgp_key = form.cleaned_data['pgp_key']
                    profile.pgp_verified = False
                    verification_code = profile.start_pgp_verification()
                    messages.info(request, _('Please decrypt the verification message sent to verify your PGP key.'))
                
                profile.save()
                messages.success(request, _('Security settings updated successfully.'))
                
        elif action == 'verify_pgp':
            form = PGPVerificationForm(profile, request.POST)
            if form.is_valid():
                profile.pgp_verified = True
                profile.pgp_verification_code = ''
                profile.pgp_verification_expires = None
                profile.save()
                messages.success(request, _('PGP key verified successfully.'))
            
        return redirect('profile:security_settings')
