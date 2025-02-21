from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import SupportTicket, TicketMessage, SupportCategory

class SupportDashboardView(LoginRequiredMixin, ListView):
    """View for user's support dashboard"""
    model = SupportTicket
    template_name = 'support/dashboard.html'
    context_object_name = 'tickets'
    
    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['open_tickets'] = self.get_queryset().exclude(status__in=['resolved', 'closed'])
        context['closed_tickets'] = self.get_queryset().filter(status__in=['resolved', 'closed'])
        return context

class TicketCreateView(LoginRequiredMixin, CreateView):
    """View for creating new support tickets"""
    model = SupportTicket
    template_name = 'support/ticket_form.html'
    fields = ['category', 'subject', 'description']
    success_url = reverse_lazy('support:dashboard')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('Support ticket created successfully'))
        return response

class TicketDetailView(LoginRequiredMixin, DetailView):
    """View for viewing ticket details and messages"""
    model = SupportTicket
    template_name = 'support/ticket_detail.html'
    context_object_name = 'ticket'
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return SupportTicket.objects.all()
        return SupportTicket.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = self.object.messages.all()
        context['can_resolve'] = self.request.user.is_staff
        return context

class TicketMessageCreateView(LoginRequiredMixin, CreateView):
    """View for adding messages to tickets"""
    model = TicketMessage
    template_name = 'support/message_form.html'
    fields = ['message']
    
    def get_success_url(self):
        return reverse_lazy('support:ticket_detail', kwargs={'pk': self.kwargs['ticket_pk']})
    
    def form_valid(self, form):
        ticket = SupportTicket.objects.get(pk=self.kwargs['ticket_pk'])
        if not self.request.user.is_staff and ticket.user != self.request.user:
            messages.error(self.request, _('You do not have permission to reply to this ticket'))
            return redirect('support:dashboard')
            
        form.instance.ticket = ticket
        form.instance.user = self.request.user
        form.instance.message_type = 'staff' if self.request.user.is_staff else 'user'
        response = super().form_valid(form)
        messages.success(self.request, _('Message added successfully'))
        return response

class BondWaiverRequestView(LoginRequiredMixin, CreateView):
    """View for requesting vendor bond waivers"""
    model = SupportTicket
    template_name = 'support/bond_waiver_form.html'
    fields = ['description']
    success_url = reverse_lazy('support:dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bond_amount'] = 500  # €500 bond requirement
        return context
    
    def form_valid(self, form):
        # Get or create bond waiver category
        category, _ = SupportCategory.objects.get_or_create(
            name='Bond Waiver Request',
            defaults={
                'description': 'Requests for vendor bond requirement waivers',
                'requires_staff': True
            }
        )
        
        form.instance.user = self.request.user
        form.instance.category = category
        form.instance.subject = 'Vendor Bond Waiver Request'
        form.instance.priority = 'high'
        
        response = super().form_valid(form)
        messages.success(self.request, _('Bond waiver request submitted successfully'))
        return response
