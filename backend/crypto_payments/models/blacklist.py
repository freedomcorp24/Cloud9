from django.db import models
from django.utils.translation import gettext_lazy as _

class BlacklistedAddress(models.Model):
    """Model for storing blacklisted cryptocurrency addresses"""
    address = models.CharField(max_length=100, unique=True)
    reason = models.TextField()
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Blacklisted Address')
        verbose_name_plural = _('Blacklisted Addresses')
        
    def __str__(self):
        return f"{self.address} (added: {self.added_at})"
