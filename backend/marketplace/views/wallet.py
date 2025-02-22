from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from ..models.wallet import UserWallet
from ..forms.wallet import WithdrawalForm
from ..services.wallet import WalletService
from ..services.auth import TransactionPINService
from crypto_payments.payment_service import CryptoPaymentService

class WalletDashboardView(LoginRequiredMixin, TemplateView):
    """Main wallet dashboard view"""
    template_name = 'marketplace/wallet/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wallet, _ = UserWallet.objects.get_or_create(user=self.request.user)
        context['wallet'] = wallet
        return context

class WalletDepositView(LoginRequiredMixin, TemplateView):
    """View for handling cryptocurrency deposits"""
    template_name = 'marketplace/wallet/deposit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        currency = self.kwargs.get('currency')
        wallet, _ = UserWallet.objects.get_or_create(user=self.request.user)
        
        # Get or generate deposit address from payment service
        payment_service = CryptoPaymentService()
        deposit_address = payment_service.get_deposit_address(
            wallet=wallet,
            currency=currency
        )
        
        context.update({
            'wallet': wallet,
            'currency': currency,
            'deposit_address': deposit_address,
            'qr_code': deposit_address.qr_code if deposit_address else None
        })
        return context

class WalletWithdrawView(LoginRequiredMixin, FormView):
    """View for handling cryptocurrency withdrawals"""
    template_name = 'marketplace/wallet/withdraw.html'
    form_class = WithdrawalForm
    
    def get_success_url(self):
        return reverse_lazy('marketplace:wallet_dashboard')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['currency'] = self.kwargs.get('currency')
        return kwargs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        currency = self.kwargs.get('currency')
        wallet, _ = UserWallet.objects.get_or_create(user=self.request.user)
        
        context.update({
            'wallet': wallet,
            'currency': currency,
            'balance': getattr(wallet, f"{currency}_balance")
        })
        return context
        
    def form_valid(self, form):
        currency = self.kwargs.get('currency')
        wallet = UserWallet.objects.get(user=self.request.user)
        
        # Verify PIN
        pin_service = TransactionPINService()
        if not pin_service.verify_pin(self.request.user, form.cleaned_data['pin']):
            messages.error(self.request, _('Invalid transaction PIN'))
            return self.form_invalid(form)
            
        # Check balance
        amount = form.cleaned_data['amount']
        balance = getattr(wallet, f"{currency}_balance")
        if amount > balance:
            messages.error(self.request, _('Insufficient balance'))
            return self.form_invalid(form)
            
        try:
            # Add withdrawal address
            wallet_service = WalletService()
            withdrawal_address = wallet_service.add_withdrawal_address(
                wallet=wallet,
                currency=currency,
                address=form.cleaned_data['address']
            )
            
            if withdrawal_address.is_flagged:
                messages.warning(
                    self.request,
                    _('This address has been flagged for suspicious activity')
                )
                return self.form_invalid(form)
                
            # Process withdrawal
            payment_service = CryptoPaymentService()
            payment_service.process_withdrawal(
                wallet=wallet,
                currency=currency,
                amount=amount,
                address=form.cleaned_data['address']
            )
            
            messages.success(self.request, _('Withdrawal request submitted successfully'))
            return super().form_valid(form)
            
        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
