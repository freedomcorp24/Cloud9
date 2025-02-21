from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import SupportTicket, TicketMessage

@receiver(post_save, sender=SupportTicket)
def handle_new_ticket(sender, instance, created, **kwargs):
    """Handle new support ticket creation"""
    if created:
        # Auto-assign if category has default assignee
        if instance.category.auto_assign_to:
            instance.assigned_to = instance.category.auto_assign_to
            instance.save()
            
        # Create initial system message
        TicketMessage.objects.create(
            ticket=instance,
            user=instance.user,
            message='Ticket created',
            message_type='system'
        )

@receiver(post_save, sender=TicketMessage)
def handle_new_message(sender, instance, created, **kwargs):
    """Handle new ticket message creation"""
    if created and instance.message_type != 'system':
        # Update ticket
        ticket = instance.ticket
        ticket.updated_at = instance.created_at
        
        # If staff replied, mark as in progress
        if instance.message_type == 'staff':
            ticket.status = 'in_progress'
        # If user replied to in_progress ticket, mark as waiting
        elif instance.message_type == 'user' and ticket.status == 'in_progress':
            ticket.status = 'waiting'
            
        ticket.save()
