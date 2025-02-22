from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from ..models.order import DeliveryOrder
from ..models.checkout import CheckoutSession

class PINVerificationForm(forms.Form):
    """Form for verifying transaction PIN"""
    pin = forms.CharField(
        label=_('Transaction PIN'),
        widget=forms.PasswordInput,
        max_length=6,
        min_length=6,
        help_text=_('Enter your 6-digit transaction PIN')
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
    def clean_pin(self):
        pin = self.cleaned_data['pin']
        if not self.user.user_profile.verify_pin(pin):
            raise forms.ValidationError(_('Invalid PIN'))
        return pin

class DeliveryDetailsForm(forms.ModelForm):
    """Form for collecting delivery details"""
    class Meta:
        model = CheckoutSession
        fields = ['delivery_type', 'completion_window', 'delivery_address', 'delivery_instructions']
        
    def clean(self):
        cleaned_data = super().clean()
        delivery_type = cleaned_data.get('delivery_type')
        completion_window = cleaned_data.get('completion_window')
        
        if delivery_type and completion_window:
            if delivery_type in ['mail', 'pickup']:
                if completion_window < DeliveryOrder.MAIL_PICKUP_MIN_DAYS:
                    self.add_error(
                        'completion_window',
                        _('Completion window must be at least %(days)d days for mail/pickup orders') % {
                            'days': DeliveryOrder.MAIL_PICKUP_MIN_DAYS
                        }
                    )
            elif delivery_type == 'instant':
                if completion_window > 1:
                    self.add_error(
                        'completion_window',
                        _('Instant delivery orders must be completed within 24 hours')
                    )
                    
        if delivery_type in ['mail', 'instant'] and not cleaned_data.get('delivery_address'):
            self.add_error('delivery_address', _('Delivery address is required'))
            
        return cleaned_data
