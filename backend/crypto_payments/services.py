from django.conf import settings
from .models import CryptoWallet, Transaction
from .wallet import WalletManager
import requests

class NodeService:
    """
    Service for interacting with cryptocurrency nodes
    """
    def __init__(self, currency_type):
        self.currency_type = currency_type
        self.node_url = self._get_node_url()
        
    def _get_node_url(self):
        """Get appropriate node URL based on currency type"""
        if self.currency_type == 'BTC':
            return settings.BTC_NODE_URL
        elif self.currency_type == 'XMR':
            return settings.XMR_NODE_URL
        elif self.currency_type == 'USDT':
            return settings.USDT_NODE_URL
        raise ValueError(f"Unsupported currency type: {self.currency_type}")
        
    def check_balance(self, address):
        """Check balance of an address"""
        response = requests.get(
            f"{self.node_url}/balance",
            params={'address': address}
        )
        return response.json()['balance']
        
    def validate_transaction(self, tx_hash, confirmations=6):
        """Validate a transaction has required confirmations"""
        response = requests.get(
            f"{self.node_url}/transaction",
            params={
                'hash': tx_hash,
                'confirmations': confirmations
            }
        )
        return response.json()['valid']

class PaymentProcessor:
    """
    Handles payment processing and wallet operations
    """
    def __init__(self, user):
        self.user = user
        
    def get_or_create_wallet(self, currency_type):
        """Get existing wallet or create new one"""
        try:
            wallet = CryptoWallet.objects.get(
                user=self.user,
                currency_type=currency_type
            )
            return WalletManager(wallet)
        except CryptoWallet.DoesNotExist:
            return WalletManager.create_wallet(self.user, currency_type)
            
    def process_deposit(self, amount, currency_type, tx_hash):
        """Process a deposit transaction"""
        wallet_manager = self.get_or_create_wallet(currency_type)
        node_service = NodeService(currency_type)
        
        if node_service.validate_transaction(tx_hash):
            wallet_manager.process_transaction(
                amount,
                'deposit',
                reference=tx_hash
            )
            return True
        return False
        
    def process_withdrawal(self, amount, currency_type, destination_address):
        """Process a withdrawal transaction"""
        wallet_manager = self.get_or_create_wallet(currency_type)
        
        try:
            wallet_manager.process_transaction(
                amount,
                'withdrawal',
                reference=destination_address
            )
            return True
        except ValueError:
            return False
