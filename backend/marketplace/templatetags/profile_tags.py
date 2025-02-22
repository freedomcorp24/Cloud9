from django import template
from django.conf import settings
from django.utils.translation import get_language_info

register = template.Library()

@register.simple_tag
def get_currencies():
    """Get list of supported currencies"""
    return settings.SUPPORTED_CURRENCIES

@register.simple_tag
def get_available_languages():
    """Get list of available languages"""
    languages = []
    for code, name in settings.LANGUAGES:
        info = get_language_info(code)
        languages.append((code, f"{info['name']} ({info['name_local']})"))
    return languages
