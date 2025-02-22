from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def get_available_currencies():
    """Return list of available currencies"""
    currencies = []
    for code, name in settings.AVAILABLE_CURRENCIES:
        currencies.append({
            'code': code,
            'name': name
        })
    return currencies

@register.simple_tag
def get_available_languages():
    """Return list of available languages"""
    languages = []
    for code, name in settings.LANGUAGES:
        languages.append({
            'code': code,
            'name': name
        })
    return languages
