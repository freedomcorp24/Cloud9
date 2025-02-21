from django import forms
from django.utils.translation import gettext_lazy as _
from ..models.wallet import WithdrawalAddress

class WithdrawalForm(forms.ModelForm):
    """Form for cryptocurrency withdrawals"""
    amount = forms.DecimalField(
        label=_('Amount'),
        min_value=0.00000001,
        max_digits=18,
        decimal_places=8,
        help_text=_('Amount to withdraw')
    )
    pin = forms.CharField(
        label=_('Transaction PIN'),
        widget=forms.PasswordInput(),
        help_text=_('Enter your 6-digit transaction PIN')
    )
    
    class Meta:
        model = WithdrawalAddress
        fields = ['address']
        
    def __init__(self, *args, currency=None, **kwargs):
        super().__init__(*args, **kwargs)
        if currency:
            self.instance.currency = currency
            
            # Adjust decimal places based on currency
            if currency == 'xmr':
                self.fields['amount'].decimal_places = 12
            elif currency == 'usdt':
                self.fields['amount'].decimal_places = 6
                
    def clean_pin(self):
        pin = self.cleaned_data.get('pin')
        if not pin.isdigit() or len(pin) != 6:
            raise forms.ValidationError(_('PIN must be 6 digits'))
        return pin
