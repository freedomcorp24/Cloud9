from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django_countries.fields import CountryField
from djmoney.models.fields import MoneyField
from babel import Locale, UnknownLocaleError

User = get_user_model()

class UserPreferences(models.Model):
    """User preferences for language and currency display."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='display_preferences'
    )
    
    # Language preferences
    language = models.CharField(
        max_length=10,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
        help_text=_("Preferred language for interface")
    )
    
    # Currency display preferences (not payment)
    display_currency = models.CharField(
        max_length=3,
        choices=settings.OSCAR_CURRENCY_CHOICES,
        default=settings.OSCAR_DEFAULT_CURRENCY,
        help_text=_("Currency for price display (payments in crypto only)")
    )
    
    # Auto-detect settings
    auto_detect_language = models.BooleanField(
        default=True,
        help_text=_("Automatically detect language from browser/device")
    )
    
    auto_detect_currency = models.BooleanField(
        default=True,
        help_text=_("Automatically detect currency from location")
    )
    
    class Meta:
        app_label = 'marketplace'
        verbose_name = _('User Preferences')
        verbose_name_plural = _('User Preferences')
    
    def save(self, *args, **kwargs):
        if not self.pk and self.auto_detect_language:
            self.detect_language()
        if not self.pk and self.auto_detect_currency:
            self.detect_currency()
        super().save(*args, **kwargs)
    
    def detect_language(self):
        """Detect language from user's browser/device settings."""
        try:
            request = getattr(self.user, '_request', None)
            if request and request.META.get('HTTP_ACCEPT_LANGUAGE'):
                browser_lang = request.META['HTTP_ACCEPT_LANGUAGE'].split(',')[0][:2]
                if browser_lang in dict(settings.LANGUAGES):
                    self.language = browser_lang
        except (AttributeError, IndexError):
            pass
    
    def detect_currency(self):
        """Detect currency from user's location."""
        try:
            request = getattr(self.user, '_request', None)
            if request and hasattr(request, 'user'):
                profile = getattr(request.user, 'user_profile', None)
                if profile and profile.country:
                    locale = Locale.parse(f"en_{profile.country}")
                    currency = locale.currency
                    if currency in dict(settings.OSCAR_CURRENCY_CHOICES):
                        self.display_currency = currency
        except (AttributeError, UnknownLocaleError):
            pass
