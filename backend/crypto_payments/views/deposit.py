from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from ..models import CryptoWallet, DepositAddress
from ..node_integration import NodeFactory
from ..utils.qr import generate_qr_code

@method_decorator(login_required, name='dispatch')
class DepositAddressCreateView(CreateView):
    """View for creating new deposit addresses"""
    model = DepositAddress
    fields = ['wallet']
    template_name = 'crypto_payments/deposit_address_create.html'
    success_url = reverse_lazy('deposit_address_detail')
    
    def form_valid(self, form):
        wallet = form.cleaned_data['wallet']
        if wallet.user != self.request.user:
            messages.error(self.request, 'Invalid wallet selection')
            return redirect('deposit_address_create')
            
        try:
            # Generate address using full node
            node = NodeFactory.get_node(wallet.currency)
            address = node.generate_deposit_address()
            
            # Create deposit address with QR code
            deposit = form.save(commit=False)
            deposit.wallet = wallet
            deposit.address = address
            deposit.qr_code = generate_qr_code(address)
            deposit.save()
            
            messages.success(self.request, 'Deposit address generated successfully')
            return redirect('deposit_address_detail', pk=deposit.pk)
            
        except Exception as e:
            messages.error(self.request, f'Error generating deposit address: {str(e)}')
            return redirect('deposit_address_create')

@method_decorator(login_required, name='dispatch')
class DepositAddressDetailView(DetailView):
    """View for showing deposit address details"""
    model = DepositAddress
    template_name = 'crypto_payments/deposit_address_detail.html'
    context_object_name = 'deposit'
    
    def get_queryset(self):
        return DepositAddress.objects.filter(
            wallet__user=self.request.user
        ).select_related('wallet')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deposit = self.object
        
        # Add confirmation requirements
        context['required_confirmations'] = deposit.required_confirmations
        context['time_remaining'] = max(
            0,
            (deposit.expires_at - timezone.now()).total_seconds() // 60
        )
        
        return context
