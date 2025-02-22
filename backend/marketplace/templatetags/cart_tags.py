from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
def quantity_options(current_quantity):
    """Generate HTML for quantity options from 1 to 100"""
    options = []
    for i in range(1, 101):
        selected = ' selected' if i == current_quantity else ''
        options.append(f'<option value="{i}"{selected}>{i}</option>')
    return mark_safe('\n'.join(options))
