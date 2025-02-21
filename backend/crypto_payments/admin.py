from django.contrib import admin
from .models import CryptoWallet, CryptoTransaction, TransactionConfirmation

@admin.register(CryptoWallet)
class CryptoWalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'currency', 'address', 'balance', 'status', 'created_at')
    list_filter = ('currency', 'status', 'created_at')
    search_fields = ('user__username', 'address')
    readonly_fields = ('created_at', 'updated_at', 'last_sync')

@admin.register(CryptoTransaction)
class CryptoTransactionAdmin(admin.ModelAdmin):
    list_display = ('tx_hash', 'wallet', 'transaction_type', 'amount_crypto', 'status', 'confirmations')
    list_filter = ('status', 'transaction_type')
    search_fields = ('tx_hash', 'wallet__address', 'wallet__user__username')

@admin.register(TransactionConfirmation)
class TransactionConfirmationAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'block_height', 'block_hash', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('transaction__tx_hash', 'block_hash')
    readonly_fields = ('timestamp',)
