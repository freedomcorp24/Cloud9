from django import forms
from .models import VendorProfile, VendorProduct

class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['business_name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class VendorProductForm(forms.ModelForm):
    class Meta:
        model = VendorProduct
        fields = [
            'product', 'price', 'stock', 'instant_delivery',
            'delivery_fee', 'shipping_fee', 'pickup_fee'
        ]
        widgets = {
            'instant_delivery': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
