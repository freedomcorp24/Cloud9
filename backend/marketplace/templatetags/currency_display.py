from django import template
from django.conf import settings
from decimal import Decimal
from django.utils.safestring import mark_safe
from marketplace.utils.exchange_rates import get_exchange_rate, ExchangeRateError

register = template.Library()

@register.filter(name='display_price')
def display_price(value, currency='USD'):
    """
    Display price in selected currency with crypto payment notice
    """
    if not value:
        return mark_safe('<span class="price">N/A</span>')
        
    try:
        value = Decimal(str(value))
        exchange_rate = get_exchange_rate(currency)
        converted_value = value * exchange_rate
        
        currency_format = settings.OSCAR_CURRENCY_FORMAT.get(currency, {})
        formatted_price = f"{converted_value:,.2f} {currency}"
        
        return mark_safe(
            f'<div class="price-display">'
            f'<span class="price">{formatted_price}</span>'
            '<small class="crypto-notice">* Price shown for reference only. '
            'Payments accepted in BTC, XMR, and USDT only.</small>'
            '</div>'
        )
    except (ValueError, TypeError, AttributeError, ExchangeRateError) as e:
        if settings.DEBUG:
            return mark_safe(f'<span class="price">Error: {str(e)}</span>')
        return mark_safe('<span class="price">N/A</span>')
