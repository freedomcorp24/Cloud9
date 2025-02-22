from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from oscar.core.loading import get_model
from typing import Any, TypeVar

Category = get_model('catalogue', 'Category')
CategoryType = TypeVar('CategoryType', bound=Any)  # Type for Category model

class UncategorizedProductManager:
    """Manages products without categories."""
    
    UNCATEGORIZED_SLUG = 'uncategorized'
    
    @classmethod
    def get_uncategorized_category(cls) -> CategoryType:
        """Get or create the Uncategorized category."""
        return Category.objects.get_or_create(
            slug=cls.UNCATEGORIZED_SLUG,
            defaults={
                'name': _('Uncategorized'),
                'description': _('Products without a specific category'),
                'is_public': True,
            }
        )[0]
    
    @classmethod
    def move_to_uncategorized(cls, products) -> None:
        """Move products to the Uncategorized category."""
        uncategorized = cls.get_uncategorized_category()
        for product in products:
            product.categories.add(uncategorized)
            product.save()
    
    @classmethod
    def get_uncategorized_products(cls):
        """Get all products in the Uncategorized category."""
        uncategorized = cls.get_uncategorized_category()
        return uncategorized.product_set.all()

class ProductCategory(models.Model):
    """
    Through model for product-category relationships
    """
    product = models.ForeignKey(
        'marketplace.ProductListing',
        on_delete=models.CASCADE,
        related_name='product_categories'
    )
    category = models.ForeignKey(
        'catalogue.Category',
        on_delete=models.CASCADE,
        related_name='marketplace_product_categories'
    )

    class Meta:
        app_label = 'marketplace'
        verbose_name = _('Product Category')
        verbose_name_plural = _('Product Categories')
        unique_together = ('product', 'category')
