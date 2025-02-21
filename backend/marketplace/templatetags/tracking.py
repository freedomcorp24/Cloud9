from django import template

register = template.Library()

@register.filter
def is_realtime(tracking):
    """Check if tracking mode is realtime"""
    return tracking.tracking_mode == 'realtime' if tracking else False

@register.filter
def button_disabled(tracking):
    """Return disabled attribute if tracking is realtime"""
    return 'disabled' if is_realtime(tracking) else ''
