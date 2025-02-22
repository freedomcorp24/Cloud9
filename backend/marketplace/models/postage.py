from django.db import models
from django.utils.translation import gettext_lazy as _

class PostageOption(models.Model):
    """
    Postage options for product listings
    """
    product = models.ForeignKey('catalogue.Product', on_delete=models.CASCADE, related_name='postage_options')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        app_label = 'marketplace'
        verbose_name = _('Postage Option')
        verbose_name_plural = _('Postage Options')
        ordering = ['price']

    def __str__(self):
        return f"{self.name} - {self.price}"
