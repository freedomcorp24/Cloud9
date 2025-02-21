from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('vendor/profile/', views.VendorProfileView.as_view(), name='vendor_profile'),
    path('vendor/profile/edit/', views.VendorProfileUpdateView.as_view(), name='vendor_profile_edit'),
    path('vendor/products/', views.VendorProductListView.as_view(), name='vendor_products'),
    path('vendor/products/add/', views.VendorProductCreateView.as_view(), name='vendor_product_add'),
    path('vendor/products/<int:pk>/edit/', views.VendorProductUpdateView.as_view(), name='vendor_product_edit'),
]
