from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext_lazy as _

class TransactionPINForm(forms.Form):
    """Form for setting up or changing transaction PIN"""
    pin = forms.CharField(
        label=_('Transaction PIN'),
        min_length=6,
        max_length=6,
        widget=forms.PasswordInput(),
        help_text=_('Enter a 6-digit PIN for authorizing transactions')
    )
    confirm_pin = forms.CharField(
        label=_('Confirm PIN'),
        min_length=6,
        max_length=6,
        widget=forms.PasswordInput(),
        help_text=_('Enter the same PIN again')
    )
    
    def clean(self):
        cleaned_data = super().clean()
        pin = cleaned_data.get('pin')
        confirm_pin = cleaned_data.get('confirm_pin')
        
        if pin and confirm_pin:
            if not pin.isdigit():
                raise forms.ValidationError(_('PIN must contain only numbers'))
                
            if pin != confirm_pin:
                raise forms.ValidationError(_('PINs do not match'))
                
        return cleaned_data

class CustomPasswordChangeForm(PasswordChangeForm):
    """Extended password change form with additional validation"""
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_('Passwords do not match'))
                
            if len(password1) < 12:
                raise forms.ValidationError(_('Password must be at least 12 characters long'))
                
        return password2
