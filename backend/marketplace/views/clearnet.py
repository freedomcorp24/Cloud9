from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from oscar.core.loading import get_model
from ..models import ProductListing
from ..models.product_category import ProductCategory
from ..mixins import CurrencyDisplayMixin

Category = get_model('catalogue', 'Category')

class ClearnetHomeView(CurrencyDisplayMixin, TemplateView):
    template_name = 'clearnet/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(depth=1)
        context['featured_products'] = ProductListing.objects.filter(
            status='active',
            visibility='public'
        ).order_by('-created_at')[:6]
        return context

class ClearnetProductListView(CurrencyDisplayMixin, ListView):
    template_name = 'clearnet/product_list.html'
    model = ProductListing
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset().filter(status='active', visibility='public')
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(categories=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = get_object_or_404(Category, slug=category_slug)
        return context

class ClearnetProductDetailView(CurrencyDisplayMixin, DetailView):
    template_name = 'clearnet/product_detail.html'
    model = ProductListing
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return super().get_queryset().filter(status='active', visibility='public')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        # Get related products from the same categories using the through model
        product_categories = ProductCategory.objects.filter(product=product).values_list('category', flat=True)
        if product_categories:
            context['related_products'] = ProductListing.objects.filter(
                product_categories__category__in=product_categories,
                status='active',
                visibility='public'
            ).exclude(pk=product.pk).distinct()[:4]
        return context
