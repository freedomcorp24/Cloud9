from django.db import models
from django.utils.translation import gettext_lazy as _
from oscar.apps.catalogue.abstract_models import AbstractProductAttributeValue

class ProductAttributeValue(AbstractProductAttributeValue):
    """
    Product attribute values for marketplace products
    """
    product = models.ForeignKey(
        'marketplace.ProductListing',
        on_delete=models.CASCADE,
        related_name='marketplace_attribute_values'
    )
    attribute = models.ForeignKey(
        'catalogue.ProductAttribute',
        on_delete=models.CASCADE,
        related_name='marketplace_attribute_values'
    )
    value_option = models.ForeignKey(
        'catalogue.AttributeOption',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='marketplace_attribute_values'
    )
    value_multi_option = models.ManyToManyField(
        'catalogue.AttributeOption',
        blank=True,
        related_name='marketplace_multi_valued_attribute_values'
    )
    entity_content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='marketplace_attribute_values'
    )

    class Meta:
        app_label = 'marketplace'
        verbose_name = _('Product Attribute Value')
        verbose_name_plural = _('Product Attribute Values')
        unique_together = ('product', 'attribute')
