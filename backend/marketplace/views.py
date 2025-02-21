from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import VendorProfile, VendorProduct
from .forms import VendorProfileForm, VendorProductForm

@method_decorator(login_required, name='dispatch')
class VendorProfileView(DetailView):
    model = VendorProfile
    template_name = 'marketplace/vendor_profile.html'
    context_object_name = 'vendor'

    def get_object(self):
        return get_object_or_404(VendorProfile, user=self.request.user)

@method_decorator(login_required, name='dispatch')
class VendorProfileUpdateView(UpdateView):
    model = VendorProfile
    form_class = VendorProfileForm
    template_name = 'marketplace/vendor_profile_form.html'
    success_url = reverse_lazy('marketplace:vendor_profile')

    def get_object(self):
        return get_object_or_404(VendorProfile, user=self.request.user)

@method_decorator(login_required, name='dispatch')
class VendorProductListView(ListView):
    model = VendorProduct
    template_name = 'marketplace/vendor_product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return VendorProduct.objects.filter(vendor__user=self.request.user)

@method_decorator(login_required, name='dispatch')
class VendorProductCreateView(CreateView):
    model = VendorProduct
    form_class = VendorProductForm
    template_name = 'marketplace/vendor_product_form.html'
    success_url = reverse_lazy('marketplace:vendor_products')

    def form_valid(self, form):
        form.instance.vendor = self.request.user.vendorprofile
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class VendorProductUpdateView(UpdateView):
    model = VendorProduct
    form_class = VendorProductForm
    template_name = 'marketplace/vendor_product_form.html'
    success_url = reverse_lazy('marketplace:vendor_products')

    def get_queryset(self):
        return VendorProduct.objects.filter(vendor__user=self.request.user)
