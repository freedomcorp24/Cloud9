from django.db import models
from django.utils.translation import gettext_lazy as _

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
