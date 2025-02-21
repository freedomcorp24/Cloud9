from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def stealth_time(value):
    """Convert timestamp to stealth-friendly format"""
    if not value:
        return "Never"
        
    now = timezone.now()
    diff = now - value
    
    if diff < timedelta(hours=1):
        return "Recently"
    elif diff < timedelta(hours=24):
        return "Today"
    elif diff < timedelta(days=7):
        return "This week"
    else:
        return "More than a week ago"
