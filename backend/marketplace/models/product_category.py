from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from mptt.models import MPTTModel, TreeForeignKey
from oscar.core.loading import get_model
from typing import Any, TypeVar, Optional
from django.utils import timezone

User = get_user_model()
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

class MarketplaceCategory(MPTTModel):
    """
    Category model with MPTT for unlimited nesting and admin-only management
    """
    name = models.CharField(_('Name'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255, unique=True)
    description = models.TextField(_('Description'), blank=True)
    
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Parent Category')
    )
    
    # Admin management tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='categories_created',
        verbose_name=_('Created By')
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='categories_updated',
        verbose_name=_('Last Updated By')
    )
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    is_active = models.BooleanField(_('Active'), default=True)
    
    class Meta:
        app_label = 'marketplace'
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['tree_id', 'lft']
        
    class MPTTMeta:
        order_insertion_by = ['name']
        
    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def clean(self):
        """Ensure only admins can modify categories"""
        if not hasattr(self, 'created_by') or not self.created_by.is_staff:
            raise ValidationError(_('Only administrators can manage categories'))
            
    def delete(self, using=None, keep_parents=False):
        """Move products to uncategorized before deletion"""
        UncategorizedProductManager.move_to_uncategorized(self.products.all())
        super().delete(using=using, keep_parents=keep_parents)

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
        MarketplaceCategory,
        on_delete=models.CASCADE,
        related_name='products'
    )
    
    # Track category changes
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='product_categorizations'
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'marketplace'
        verbose_name = _('Product Category')
        verbose_name_plural = _('Product Categories')
        unique_together = ('product', 'category')
