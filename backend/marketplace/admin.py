from django.contrib import admin
from .models import VendorProfile, VendorProduct

@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'verification_status', 'bond_paid', 'rating', 'created_at')
    list_filter = ('verification_status', 'bond_paid', 'created_at')
    search_fields = ('business_name', 'user__username', 'description')
    readonly_fields = ('rating', 'total_ratings', 'created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(VendorProduct)
class VendorProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'vendor', 'price', 'stock', 'instant_delivery', 'created_at')
    list_filter = ('instant_delivery', 'created_at')
    search_fields = ('product__title', 'vendor__business_name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Product Information', {
            'fields': ('product', 'vendor', 'price', 'stock')
        }),
        ('Delivery Options', {
            'fields': ('instant_delivery', 'delivery_fee', 'shipping_fee', 'pickup_fee', 'max_delivery_distance')
        }),
        ('Order Limits', {
            'fields': ('min_order_quantity', 'max_order_quantity')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
