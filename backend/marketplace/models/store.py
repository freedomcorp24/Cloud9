from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError

class StoreSettings(models.Model):
    """Model for vendor store settings including vacation mode"""
    vendor = models.OneToOneField('VendorProfile', on_delete=models.CASCADE)
    vacation_mode = models.BooleanField(
        default=False,
        help_text=_('Enable to temporarily close store')
    )
    vacation_message = models.TextField(
        blank=True,
        help_text=_('Message to display when store is in vacation mode')
    )
    vacation_start = models.DateTimeField(null=True, blank=True)
    vacation_end = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Store Settings')
        verbose_name_plural = _('Store Settings')
    
    def __str__(self):
        status = 'Closed' if self.vacation_mode else 'Open'
        return f"{self.vendor.user.username}'s Store - {status}"
    
    @property
    def is_open(self):
        """Check if store is open for business"""
        if not self.vacation_mode:
            return True
        if self.vacation_end and timezone.now() > self.vacation_end:
            self.vacation_mode = False
            self.save()
            return True
        return False

# OrderTimeframe model moved to timeframe.py

class DisputeQueue(models.Model):
    """Model for managing dispute resolution queues"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    support_staff = models.ManyToManyField(
        'auth.User',
        related_name='dispute_queues',
        limit_choices_to={'is_staff': True}
    )
    requires_admin = models.BooleanField(
        default=False,
        help_text=_('Only admins can handle disputes in this queue')
    )
    
    class Meta:
        verbose_name = _('Dispute Queue')
        verbose_name_plural = _('Dispute Queues')
    
    def __str__(self):
        return self.name

class Dispute(models.Model):
    """Model for order disputes"""
    order = models.OneToOneField('DeliveryOrder', on_delete=models.CASCADE)
    opened_by = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='opened_disputes'
    )
    queue = models.ForeignKey(
        DisputeQueue,
        on_delete=models.SET_NULL,
        null=True
    )
    assigned_to = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_disputes'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('open', 'Open'),
            ('escalated', 'Escalated to Admin'),
            ('resolved', 'Resolved')
        ],
        default='open'
    )
    resolution = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Dispute')
        verbose_name_plural = _('Disputes')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Dispute #{self.id} - {self.order}"
    
    def escalate_to_admin(self):
        """Escalate dispute to admin queue"""
        admin_queue = DisputeQueue.objects.get(requires_admin=True)
        self.queue = admin_queue
        self.status = 'escalated'
        self.save()
    
    def resolve(self, resolution, resolved_by):
        """Resolve the dispute"""
        self.resolution = resolution
        self.resolved_at = timezone.now()
        self.status = 'resolved'
        self.save()
