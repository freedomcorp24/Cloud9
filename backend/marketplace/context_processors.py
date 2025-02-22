from django.conf import settings

def currency_choices(request):
    """Add currency choices to template context"""
    return {
        'CURRENCIES': settings.AVAILABLE_CURRENCIES
    }

def language_choices(request):
    """Add language choices to template context"""
    return {
        'LANGUAGES': settings.LANGUAGES
    }
