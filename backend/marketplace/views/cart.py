from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from ..models.cart import Cart, CartItem
from ..models.product import ProductListing
from ..models.vendor import VendorProfile

class CartView(LoginRequiredMixin, TemplateView):
    """View for displaying shopping cart contents"""
    template_name = 'clearnet/cart/cart.html'
    
    def get_template_names(self):
        """Return appropriate template based on request type"""
        if getattr(self.request, 'is_tor', False):
            return ['tor/cart/cart.html']
        return [self.template_name]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        carts = Cart.objects.filter(user=self.request.user).prefetch_related('items')
        
        cart_data = []
        total = 0
        for cart in carts:
            items = cart.items.all()
            cart_total = sum(item.total_price for item in items)
            total += cart_total
            cart_data.append({
                'vendor': cart.vendor,
                'items': items,
                'total': cart_total
            })
        
        context.update({
            'carts': cart_data,
            'total': total
        })
        return context

class AddToCartView(LoginRequiredMixin, View):
    """View for adding items to cart"""
    
    @transaction.atomic
    def post(self, request, product_id):
        product = get_object_or_404(ProductListing, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity < 1 or quantity > 100:
            messages.error(request, _('Invalid quantity. Must be between 1 and 100.'))
            return redirect('product:detail', pk=product_id)
            
        # Get or create cart for this vendor
        cart, _ = Cart.objects.get_or_create(
            user=request.user,
            vendor=product.vendor
        )
        
        # Check if item already in cart
        try:
            cart_item = cart.items.get(product=product)
            cart_item.quantity = quantity
            cart_item.unit_price = product.price
            cart_item.save()
            messages.success(request, _('Cart updated successfully.'))
        except CartItem.DoesNotExist:
            CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity,
                unit_price=product.price
            )
            messages.success(request, _('Item added to cart.'))
            
        return redirect('cart:view')

class RemoveFromCartView(LoginRequiredMixin, View):
    """View for removing items from cart"""
    
    def post(self, request, item_id):
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        item.delete()
        messages.success(request, _('Item removed from cart.'))
        return redirect('cart:view')

class UpdateCartView(LoginRequiredMixin, View):
    """View for updating cart item quantities"""
    
    def post(self, request, item_id):
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity < 1 or quantity > 100:
            messages.error(request, _('Invalid quantity. Must be between 1 and 100.'))
        else:
            item.quantity = quantity
            item.save()
            messages.success(request, _('Cart updated successfully.'))
            
        return redirect('cart:view')
