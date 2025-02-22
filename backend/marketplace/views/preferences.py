from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from oscar.core.loading import get_model

UserPreferences = get_model('customer', 'UserPreferences')

class PreferencesUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating user preferences."""
    model = UserPreferences
    fields = ['display_currency', 'language']
    success_url = reverse_lazy('profile:profile')
    
    def get_object(self, queryset=None):
        """Get or create user preferences."""
        return UserPreferences.objects.get_or_create(user=self.request.user)[0]
    
    def form_valid(self, form):
        messages.success(self.request, _('Preferences updated successfully'))
        return super().form_valid(form)
