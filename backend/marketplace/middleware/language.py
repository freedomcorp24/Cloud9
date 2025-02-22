from django.utils import translation
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import get_language_from_request
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from typing import Optional

class LanguageDetectionMiddleware(MiddlewareMixin):
    """Middleware to detect and set user's preferred language."""
    
    def process_request(self, request) -> None:
        """
        Process request to detect and set language.
        No JavaScript required for Tor compatibility.
        """
        if not request.session.get('language_detected'):
            # Try to get language from user preferences first
            if hasattr(request, 'user') and request.user.is_authenticated:
                try:
                    prefs = request.user.display_preferences
                    if prefs and prefs.language:
                        translation.activate(prefs.language)
                        request.session['language_detected'] = True
                        return
                except AttributeError:
                    pass
            
            # Fall back to browser headers
            accept_lang = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
            if accept_lang:
                try:
                    lang_code = accept_lang.split(',')[0].split('-')[0].lower()
                    if lang_code in dict(settings.LANGUAGES):
                        translation.activate(lang_code)
                        request.session['language_detected'] = True
                        return
                except (IndexError, KeyError):
                    pass
            
            # Default to English if no other language detected
            translation.activate(settings.LANGUAGE_CODE)
            request.session['language_detected'] = True
    
    def process_response(self, request, response) -> Optional[str]:
        """Ensure language cookie is set properly."""
        if not request.session.get('language_detected'):
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                translation.get_language(),
                max_age=settings.LANGUAGE_COOKIE_AGE,
                secure=settings.LANGUAGE_COOKIE_SECURE,
                httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
                samesite=settings.LANGUAGE_COOKIE_SAMESITE
            )
        return response
