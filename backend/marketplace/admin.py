from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import (
    VendorProfile, VendorProduct, DeliveryOrder,
    OrderDispute, DeliveryTracking, UserWallet, 
    WithdrawalAddress, PostageOption, MarketplaceCategory,
    ProductCategory
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

@admin.register(MarketplaceCategory)
class MarketplaceCategoryAdmin(MPTTModelAdmin):
    """Admin interface for category management"""
    list_display = ['name', 'slug', 'parent', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ['parent']
    
    def save_model(self, request, obj, form, change):
        """Ensure admin user is tracked"""
        if not change:  # New category
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
        
    def get_queryset(self, request):
        """Show all categories to superusers, only active ones to staff"""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(is_active=True)
        return qs
        
    def has_change_permission(self, request, obj=None):
        """Only allow superusers to edit categories"""
        return request.user.is_superuser
        
    def has_delete_permission(self, request, obj=None):
        """Only allow superusers to delete categories"""
        return request.user.is_superuser

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    """Admin interface for product categorization"""
    list_display = ['product', 'category', 'added_by', 'added_at']
    list_filter = ['category', 'added_at']
    raw_id_fields = ['product', 'category']
    search_fields = ['product__name', 'category__name']
    
    def save_model(self, request, obj, form, change):
        """Track who added the categorization"""
        if not change:
            obj.added_by = request.user
        super().save_model(request, obj, form, change)

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


@admin.register(PostageOption)
class PostageOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)
    ordering = ('price',)

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
