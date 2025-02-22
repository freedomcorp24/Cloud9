from django import template

register = template.Library()

@register.inclusion_tag('cart/quantity_options.html')
def quantity_options(current_quantity):
    """Generate quantity options from 1 to 100"""
    return {
        'options': range(1, 101),
        'current_quantity': current_quantity
    }
