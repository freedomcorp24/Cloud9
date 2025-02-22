from django.db import models
from django.utils.translation import gettext_lazy as _

class ProductRecommendation(models.Model):
    """
    Through model for product recommendations
    """
    primary = models.ForeignKey(
        'marketplace.ProductListing',
        on_delete=models.CASCADE,
        related_name='primary_recommendations'
    )
    recommendation = models.ForeignKey(
        'marketplace.ProductListing',
        on_delete=models.CASCADE,
        related_name='secondary_recommendations'
    )
    ranking = models.PositiveSmallIntegerField(default=0)

    class Meta:
        app_label = 'marketplace'
        ordering = ['ranking']
        unique_together = ('primary', 'recommendation')
        verbose_name = _('Product Recommendation')
        verbose_name_plural = _('Product Recommendations')
