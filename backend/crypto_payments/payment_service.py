from django.conf import settings
from .models import CryptoWallet, CryptoTransaction
from .wallet import WalletManager
from .node_service import NodeService

class CryptoPaymentService:
    """Service for handling cryptocurrency payments."""
    
    def __init__(self):
        """Initialize payment service."""
        self.node_services = {
            'BTC': NodeService('BTC'),
            'XMR': NodeService('XMR'),
            'USDT': NodeService('USDT')
        }
    
    def get_deposit_address(self, wallet: CryptoWallet, currency: str) -> str:
        """Get or generate deposit address for wallet."""
        if not wallet.deposit_address or wallet.is_deposit_address_expired():
            wallet_manager = WalletManager(wallet)
            return wallet_manager.generate_deposit_address()
        return wallet.deposit_address
    
    def process_withdrawal(self, wallet: CryptoWallet, currency: str, amount: float, destination: str) -> bool:
        """Process withdrawal from wallet."""
        try:
            # Verify transaction with node
            node_service = self.node_services[currency]
            if not node_service.validate_transaction(destination, settings.WITHDRAWAL_CONFIRMATION_BLOCKS):
                return False
            
            # Process withdrawal
            wallet_manager = WalletManager(wallet)
            wallet_manager.process_transaction(
                amount=amount,
                transaction_type='withdrawal',
                reference=destination
            )
            return True
            
        except Exception as e:
            return False
    
    def process_deposit(self, wallet: CryptoWallet, currency: str, amount: float, tx_hash: str) -> bool:
        """Process deposit to wallet."""
        try:
            # Verify transaction with node
            node_service = self.node_services[currency]
            if not node_service.validate_transaction(tx_hash, settings.BTC_MIN_CONFIRMATIONS):
                return False
            
            # Process deposit
            wallet_manager = WalletManager(wallet)
            wallet_manager.process_transaction(
                amount=amount,
                transaction_type='deposit',
                reference=tx_hash
            )
            return True
            
        except Exception as e:
            return False
