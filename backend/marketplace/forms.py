from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from .models import VendorProfile, VendorProduct

class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['business_name', 'description']
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': 100,
                'placeholder': _('Enter your business name')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'maxlength': 2000,
                'placeholder': _('Describe your business')
            }),
        }

    def clean_business_name(self):
        name = self.cleaned_data['business_name']
        if len(name.strip()) < 3:
            raise forms.ValidationError(_('Business name must be at least 3 characters long'))
        return name

class VendorProductForm(forms.ModelForm):
    class Meta:
        model = VendorProduct
        fields = [
            'product', 'price', 'stock', 'instant_delivery',
            'delivery_fee', 'shipping_fee', 'pickup_fee',
            'max_delivery_distance', 'min_order_quantity',
            'max_order_quantity'
        ]
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'instant_delivery': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'delivery_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'shipping_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'pickup_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'max_delivery_distance': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.1',
                'max': '999.99',
                'step': '0.1'
            }),
            'min_order_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'max_order_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        min_qty = cleaned_data.get('min_order_quantity')
        max_qty = cleaned_data.get('max_order_quantity')
        
        if min_qty and max_qty and min_qty > max_qty:
            raise forms.ValidationError(_('Minimum order quantity cannot be greater than maximum order quantity'))
        
        return cleaned_data
