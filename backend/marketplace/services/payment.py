from decimal import Decimal
import logging
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from crypto_payments.payment_server import PaymentServer
from crypto_payments.models import CryptoWallet, CryptoTransaction
from crypto_payments.services.wallet_manager import WalletManager
from ..models.order import DeliveryOrder
from ..utils.exchange_rates import ExchangeRateService

logger = logging.getLogger(__name__)

class PaymentService:
    """Service for handling cryptocurrency payments"""
    
    def __init__(self):
        self.payment_server = PaymentServer()
        self.wallet_manager = WalletManager()
        self.exchange_rates = ExchangeRateService()
        
    def create_payment_address(self, order: DeliveryOrder, currency: str) -> dict:
        """Create payment address for order"""
        if currency.upper() not in ['BTC', 'XMR', 'USDT']:
            raise ValueError(_('Invalid cryptocurrency'))
            
        # Create deposit wallet
        wallet = self.wallet_manager.create_deposit_wallet(currency)
        
        # Calculate crypto amount
        rate = self.exchange_rates.get_rate(currency)
        amount_crypto = order.total_incl_tax / rate
        
        # Associate wallet with order
        order.payment_wallet = wallet
        order.payment_currency = currency
        order.payment_amount_crypto = amount_crypto
        order.save()
        
        return {
            'address': wallet.address,
            'amount': amount_crypto,
            'currency': currency,
            'rate': rate,
            'total_fiat': order.total_incl_tax
        }
        
    def check_payment(self, order: DeliveryOrder) -> bool:
        """Check if payment has been received and verified"""
        if not order.payment_wallet:
            return False
            
        # Get transactions for wallet
        transactions = CryptoTransaction.objects.filter(
            wallet=order.payment_wallet,
            transaction_type='deposit',
            status='completed'
        )
        
        # Calculate total received
        total_received = sum(tx.amount_crypto for tx in transactions)
        
        # Verify amount matches
        return total_received >= order.payment_amount_crypto
        
    def process_refund(self, order: DeliveryOrder, amount: Decimal = None) -> bool:
        """Process refund for order"""
        if not order.payment_wallet:
            raise ValueError(_('No payment wallet associated with order'))
            
        if not amount:
            amount = order.payment_amount_crypto
            
        try:
            # Get customer refund address
            refund_address = order.user.user_profile.get_wallet_address(
                order.payment_currency
            )
            
            if not refund_address:
                raise ValueError(_('No refund address available'))
                
            # Process withdrawal through payment server
            tx_hash = self.payment_server.process_withdrawal(
                wallet=order.payment_wallet,
                amount=amount,
                destination=refund_address
            )
            
            if tx_hash:
                order.refund_tx_hash = tx_hash
                order.refund_amount = amount
                order.refund_processed = timezone.now()
                order.save()
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Refund processing failed: {str(e)}")
            return False
