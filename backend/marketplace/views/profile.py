from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.conf import settings
from marketplace.models.user_preferences import UserPreferences

class UserProfileView(LoginRequiredMixin, UpdateView):
    """View for updating user preferences."""
    model = UserPreferences
    template_name = 'oscar/customer/profile/profile.html'
    fields = ['display_currency', 'language', 'auto_detect_language', 'auto_detect_currency']
    success_url = reverse_lazy('customer:profile-view')
    
    def get_object(self, queryset=None):
        """Get or create user preferences."""
        return UserPreferences.objects.get_or_create(user=self.request.user)[0]
    
    def get_context_data(self, **kwargs):
        """Add currency and language choices to context."""
        context = super().get_context_data(**kwargs)
        context['currency_choices'] = settings.OSCAR_CURRENCY_CHOICES
        context['languages'] = settings.LANGUAGES
        return context
