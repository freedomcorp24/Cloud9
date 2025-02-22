from django.contrib import admin
from .models import (
    VendorProfile, VendorProduct, DeliveryOrder,
    OrderDispute, DeliveryTracking, UserWallet, 
    WithdrawalAddress
)

@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'verification_status', 'bond_paid', 'rating', 'created_at')
    list_filter = ('verification_status', 'bond_paid', 'created_at')
    search_fields = ('business_name', 'user__username')
    readonly_fields = ('rating', 'total_ratings', 'created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(VendorProduct)
class VendorProductAdmin(admin.ModelAdmin):
    list_display = ('get_product_title', 'get_vendor', 'get_price', 'get_stock', 'instant_delivery', 'created_at')
    list_filter = ('instant_delivery', 'created_at')
    search_fields = ('product__title', 'partner__name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    def get_product_title(self, obj):
        return obj.product.title if obj.product else None
    get_product_title.short_description = 'Product'
    get_product_title.admin_order_field = 'product__title'

    def get_vendor(self, obj):
        return obj.partner.name if obj.partner else None
    get_vendor.short_description = 'Vendor'
    get_vendor.admin_order_field = 'partner__name'

    def get_price(self, obj):
        return obj.price_excl_tax
    get_price.short_description = 'Price'
    get_price.admin_order_field = 'price_excl_tax'

    def get_stock(self, obj):
        return obj.num_in_stock
    get_stock.short_description = 'Stock'
    get_stock.admin_order_field = 'num_in_stock'
    
    fieldsets = (
        ('Product Information', {
            'fields': ('product', 'partner', 'price_excl_tax', 'num_in_stock')
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

@admin.register(DeliveryOrder)
class DeliveryOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'vendor', 'delivery_type', 'status', 'created_at')
    list_filter = ('delivery_type', 'created_at')
    search_fields = ('vendor__business_name', 'delivery_address')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(OrderDispute)
class OrderDisputeAdmin(admin.ModelAdmin):
    list_display = ('order', 'dispute_type', 'status', 'created_at')
    list_filter = ('dispute_type', 'status', 'created_at')
    search_fields = ('order__id', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    list_display = ('order', 'status_update', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('order__id', 'status_update')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)



@admin.register(UserWallet)
class UserWalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_total_balance', 'created_at')
    
    def get_total_balance(self, obj):
        return f"BTC: {obj.btc_balance}, XMR: {obj.xmr_balance}, USDT: {obj.usdt_balance}"
    get_total_balance.short_description = 'Balance'
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(WithdrawalAddress)
class WithdrawalAddressAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'address', 'currency', 'created_at')
    
    def get_user(self, obj):
        return obj.wallet.user
    get_user.short_description = 'User'
    get_user.admin_order_field = 'wallet__user'
    list_filter = ('currency', 'created_at')
    search_fields = ('user__username', 'address')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
