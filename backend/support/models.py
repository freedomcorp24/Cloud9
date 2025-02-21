from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone

class SupportCategory(models.Model):
    """Model for support ticket categories"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    requires_staff = models.BooleanField(
        default=False,
        help_text=_('Only staff members can handle tickets in this category')
    )
    auto_assign_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auto_assigned_categories',
        help_text=_('User to automatically assign tickets in this category to')
    )
    
    class Meta:
        verbose_name = _('Support Category')
        verbose_name_plural = _('Support Categories')
        
    def __str__(self):
        return self.name

class SupportTicket(models.Model):
    """Model for support tickets"""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting', 'Waiting for User'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ]
    
    category = models.ForeignKey(
        SupportCategory,
        on_delete=models.PROTECT,
        related_name='tickets'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_tickets'
    )
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Support Ticket')
        verbose_name_plural = _('Support Tickets')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"#{self.id} - {self.subject}"
        
    def resolve(self, resolved_by):
        """Mark ticket as resolved"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()
        
        # Create resolution message
        TicketMessage.objects.create(
            ticket=self,
            user=resolved_by,
            message=_('Ticket marked as resolved'),
            message_type='system'
        )

class TicketMessage(models.Model):
    """Model for support ticket messages"""
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('staff', 'Staff Message'),
        ('system', 'System Message')
    ]
    
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    message = models.TextField()
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPES,
        default='user'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Ticket Message')
        verbose_name_plural = _('Ticket Messages')
        ordering = ['created_at']
        
    def __str__(self):
        return f"Message on ticket #{self.ticket.id}"
