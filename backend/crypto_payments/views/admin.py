from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import ListView, DetailView
from django.db.models import Sum, Count
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.conf import settings
from ..models import (
    CryptoWallet,
    CryptoTransaction,
    PaymentBatch,
    BatchTransaction,
    AdminAction
)
from ..models.blacklist import AddressBlacklist
from ..payment_server import PaymentServer
from ..node_integration import NodeFactory

@staff_member_required
def payment_dashboard(request):
    """Main payment dashboard view showing payment metrics and batch operations"""
    # Get pending payments
    pending_payments = CryptoTransaction.objects.filter(
        status='pending'
    ).select_related('wallet__user')
    
    # Get frozen accounts
    frozen_accounts = CryptoWallet.objects.filter(
        status='frozen'
    ).select_related('user')
    
    # Get payment batches
    payment_batches = PaymentBatch.objects.all()
    
    # Get payment metrics
    metrics = {}
    for currency in CryptoWallet.objects.values_list('currency', flat=True).distinct():
        metrics[currency] = {
            'total_volume': CryptoTransaction.objects.filter(
                wallet__currency=currency,
                status='completed'
            ).aggregate(total=Sum('amount_crypto'))['total'] or 0,
            'pending_count': CryptoTransaction.objects.filter(
                wallet__currency=currency,
                status='pending'
            ).count(),
            'frozen_count': CryptoTransaction.objects.filter(
                wallet__currency=currency,
                status='frozen'
            ).count()
        }
    
    # Get suspicious activity
    suspicious_activity = CryptoTransaction.objects.filter(
        created_at__gte=timezone.now() - timezone.timedelta(hours=24),
        status__in=['frozen', 'failed']
    ).select_related('wallet__user')
    
    # Get blacklisted addresses
    blacklisted_addresses = AddressBlacklist.objects.all().order_by('-risk_score')
    
    context = {
        'pending_payments': pending_payments,
        'frozen_accounts': frozen_accounts,
        'payment_batches': payment_batches,
        'metrics': metrics,
        'suspicious_activity': suspicious_activity,
        'blacklisted_addresses': blacklisted_addresses
    }
    
    return render(request, 'admin/payment_dashboard.html', context)

@staff_member_required
def batch_detail(request, pk):
    """Detailed view of a payment batch with transaction list"""
    batch = get_object_or_404(PaymentBatch, pk=pk)
    transactions = BatchTransaction.objects.filter(
        batch=batch
    ).select_related('transaction', 'transaction__wallet__user')
    
    context = {
        'batch': batch,
        'transactions': transactions
    }
    return render(request, 'admin/batch_detail.html', context)

@staff_member_required
def user_payment_history(request, user_id):
    """View for user payment history and account management"""
    transactions = CryptoTransaction.objects.filter(
        wallet__user_id=user_id
    ).select_related('wallet').order_by('-created_at')
    
    user_wallets = CryptoWallet.objects.filter(
        user_id=user_id
    )
    
    payment_metrics = {
        'total_volume': transactions.filter(
            status='completed'
        ).aggregate(total=Sum('amount_crypto'))['total'] or 0,
        'pending_count': transactions.filter(
            status='pending'
        ).count(),
        'frozen_count': transactions.filter(
            status='frozen'
        ).count()
    }
    
    context = {
        'transactions': transactions,
        'user_wallets': user_wallets,
        'payment_metrics': payment_metrics
    }
    
    return render(request, 'admin/user_payment_history.html', context)

@staff_member_required
def admin_action_log(request):
    """View for admin action audit log"""
    actions = AdminAction.objects.all().select_related(
        'admin'
    ).order_by('-timestamp')
    
    context = {
        'actions': actions
    }
    
    return render(request, 'admin/action_log.html', context)

@staff_member_required
def deposit_address(request, pk):
    """View for managing deposit addresses and confirmations"""
    wallet = get_object_or_404(CryptoWallet, pk=pk)
    
    if request.method == 'POST':
        try:
            node = NodeFactory.get_node(wallet.currency)
            new_address = node.generate_deposit_address()
            
            # Create pending transaction
            CryptoTransaction.objects.create(
                wallet=wallet,
                status='pending',
                destination_address=new_address,
                transaction_type='deposit'
            )
            messages.success(request, f'Generated new deposit address: {new_address}')
            
        except Exception as e:
            messages.error(request, f'Error generating deposit address: {str(e)}')
            
        return redirect('admin:deposit_address', pk=wallet.pk)
    
    active_deposits = CryptoTransaction.objects.filter(
        wallet=wallet,
        status='pending',
        created_at__gte=timezone.now() - timezone.timedelta(hours=settings.DEPOSIT_ADDRESS_EXPIRY)
    ).order_by('-created_at')
    
    context = {
        'wallet': wallet,
        'active_deposits': active_deposits
    }
    
    return render(request, 'admin/deposit_address.html', context)
