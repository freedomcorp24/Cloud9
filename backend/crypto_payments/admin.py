from django.contrib import admin
from .models.transaction import CryptoTransaction
from .models.payment import PaymentBatch, BatchTransaction
from .models.admin import AdminAction

@admin.register(CryptoTransaction)
class CryptoTransactionAdmin(admin.ModelAdmin):
    list_display = ('tx_hash', 'wallet', 'transaction_type', 'amount_crypto', 'status')
    list_filter = ('status', 'transaction_type')
    search_fields = ('tx_hash', 'wallet__address', 'wallet__user__username')

@admin.register(PaymentBatch)
class PaymentBatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'currency', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'currency')
    search_fields = ('id', 'created_by__username')

@admin.register(BatchTransaction)
class BatchTransactionAdmin(admin.ModelAdmin):
    list_display = ('batch', 'transaction', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('batch__id', 'transaction__tx_hash')

@admin.register(AdminAction)
class AdminActionAdmin(admin.ModelAdmin):
    list_display = ('action_type', 'admin', 'target_type', 'timestamp')
    list_filter = ('action_type', 'timestamp')
    search_fields = ('admin__username', 'target_type', 'details')
