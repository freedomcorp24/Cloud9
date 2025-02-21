from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import ListView, DetailView
from django.db.models import Sum, Count
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from ..models import (
    CryptoWallet,
    CryptoTransaction,
    PaymentBatch,
    BatchTransaction,
    AdminAction
)

@staff_member_required
class PaymentDashboardView(ListView):
    """Main payment dashboard view showing payment metrics and batch operations"""
    template_name = 'admin/payment_dashboard.html'
    context_object_name = 'payment_metrics'
    model = CryptoTransaction
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get pending payments
        context['pending_payments'] = CryptoTransaction.objects.filter(
            status='pending'
        ).select_related('wallet__user')
        
        # Get frozen accounts
        context['frozen_accounts'] = CryptoWallet.objects.filter(
            status='frozen'
        ).select_related('user')
        
        # Get payment batches
        context['payment_batches'] = PaymentBatch.objects.all()
        
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
        context['metrics'] = metrics
        
        # Get suspicious activity
        context['suspicious_activity'] = CryptoTransaction.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(hours=24),
            status__in=['frozen', 'failed']
        ).select_related('wallet__user')
        
        return context

@staff_member_required
class BatchDetailView(DetailView):
    """Detailed view of a payment batch with transaction list"""
    template_name = 'admin/batch_detail.html'
    model = PaymentBatch
    context_object_name = 'batch'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions'] = BatchTransaction.objects.filter(
            batch=self.object
        ).select_related('transaction', 'transaction__wallet__user')
        return context

@staff_member_required
class UserPaymentHistoryView(ListView):
    """View for user payment history and account management"""
    template_name = 'admin/user_payment_history.html'
    model = CryptoTransaction
    context_object_name = 'transactions'
    
    def get_queryset(self):
        return CryptoTransaction.objects.filter(
            wallet__user_id=self.kwargs['user_id']
        ).select_related('wallet').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_wallets'] = CryptoWallet.objects.filter(
            user_id=self.kwargs['user_id']
        )
        context['payment_metrics'] = {
            'total_volume': self.get_queryset().filter(
                status='completed'
            ).aggregate(total=Sum('amount_crypto'))['total'] or 0,
            'pending_count': self.get_queryset().filter(
                status='pending'
            ).count(),
            'frozen_count': self.get_queryset().filter(
                status='frozen'
            ).count()
        }
        return context

@staff_member_required
class AdminActionLogView(ListView):
    """View for admin action audit log"""
    template_name = 'admin/action_log.html'
    model = AdminAction
    context_object_name = 'actions'
    paginate_by = 50
    
    def get_queryset(self):
        return AdminAction.objects.all().select_related(
            'admin'
        ).order_by('-timestamp')
