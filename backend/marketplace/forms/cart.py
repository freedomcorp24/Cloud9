from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

class AddToCartForm(forms.Form):
    """Form for adding items to cart"""
    quantity = forms.IntegerField(
        min_value=1,
        max_value=100,
        initial=1,
        label=_('Quantity'),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100)
        ],
        error_messages={
            'min_value': _('Quantity must be at least 1'),
            'max_value': _('Quantity cannot exceed 100'),
            'required': _('Please enter a quantity'),
            'invalid': _('Please enter a valid number')
        }
    )

class UpdateCartForm(forms.Form):
    """Form for updating cart quantities"""
    quantity = forms.IntegerField(
        min_value=1,
        max_value=100,
        label=_('Quantity'),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100)
        ],
        error_messages={
            'min_value': _('Quantity must be at least 1'),
            'max_value': _('Quantity cannot exceed 100'),
            'required': _('Please enter a quantity'),
            'invalid': _('Please enter a valid number')
        }
    )
