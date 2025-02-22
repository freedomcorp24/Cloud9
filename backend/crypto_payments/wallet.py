from django.db import models
from django.conf import settings
from django.utils import timezone
import hashlib
import secrets
from decimal import Decimal
from typing import Optional, Dict, Tuple
from .models import CryptoWallet, CryptoTransaction
from .services.bitcoin import BitcoinService
from .services.monero import MoneroService
from .services.ethereum import EthereumService
from .exceptions import InsufficientFundsError, WalletError

class WalletManager:
    """
    Manages cryptocurrency wallets and transactions with hot/cold separation
    """
    SUPPORTED_CURRENCIES = ['BTC', 'XMR', 'USDT']
    
    def __init__(self, wallet: CryptoWallet):
        if wallet.currency_type not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {wallet.currency_type}")
        self.wallet = wallet
        self._init_service()
        
    def _init_service(self):
        """Initialize appropriate crypto service"""
        if self.wallet.currency_type == 'BTC':
            self.service = BitcoinService()
        elif self.wallet.currency_type == 'XMR':
            self.service = MoneroService()
        elif self.wallet.currency_type == 'USDT':
            self.service = EthereumService()
    
    @classmethod
    def create_wallet(cls, user, currency_type: str, wallet_type: str = 'deposit') -> 'WalletManager':
        """Create a new wallet for a user"""
        if currency_type not in cls.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {currency_type}")
            
        if wallet_type not in dict(CryptoWallet.WALLET_TYPES):
            raise ValueError(f"Invalid wallet type: {wallet_type}")
            
        wallet_id = hashlib.sha256(
            f"{user.id}:{currency_type}:{wallet_type}:{secrets.token_hex(16)}".encode()
        ).hexdigest()
        
        # Get hot wallet threshold from settings
        hot_wallet_threshold = None
        if wallet_type == 'hot':
            threshold_key = f'{currency_type}_HOT_WALLET_THRESHOLD'
            hot_wallet_threshold = getattr(settings, threshold_key, None)
            if not hot_wallet_threshold:
                raise ValueError(f"Hot wallet threshold not configured for {currency_type}")
        
        wallet = CryptoWallet.objects.create(
            user=user,
            wallet_id=wallet_id,
            currency_type=currency_type,
            wallet_type=wallet_type,
            hot_wallet_threshold=hot_wallet_threshold,
            balance=Decimal('0')
        )
        return cls(wallet)
    
    def generate_deposit_address(self, expires_in: int = 7200) -> str:
        """Generate one-time deposit address using appropriate crypto service"""
        if self.wallet.wallet_type != 'deposit':
            raise WalletError("Can only generate addresses for deposit wallets")
            
        address_info = self.service.create_address()
        
        self.wallet.address = address_info['address']
        if 'view_key' in address_info:  # For Monero
            self.wallet.view_key = address_info['view_key']
            
        self.wallet.deposit_address_expires = timezone.now() + timezone.timedelta(seconds=expires_in)
        self.wallet.save()
        
        return self.wallet.address
        
    def process_transaction(self, amount: Decimal, transaction_type: str, reference: Optional[str] = None) -> None:
        """Process a transaction with hot/cold wallet separation"""
        if transaction_type not in ['deposit', 'withdrawal']:
            raise ValueError("Invalid transaction type")
            
        if transaction_type == 'withdrawal' and self.wallet.balance < amount:
            raise InsufficientFundsError("Insufficient funds for withdrawal")
            
        # Handle hot/cold wallet separation
        if self.wallet.wallet_type == 'hot' and transaction_type == 'deposit':
            if self.wallet.needs_rebalancing():
                self._rebalance_to_cold_wallet()
                
        elif self.wallet.wallet_type == 'cold' and transaction_type == 'withdrawal':
            raise WalletError("Cannot withdraw directly from cold wallet")
            
        # Update balance
        if transaction_type == 'deposit':
            self.wallet.balance += amount
        else:  # withdrawal
            self.wallet.balance -= amount
            
        self.wallet.save()
        
        # Create transaction record
        CryptoTransaction.objects.create(
            wallet=self.wallet,
            amount=amount,
            transaction_type=transaction_type,
            reference=reference
        )
        
    def _rebalance_to_cold_wallet(self) -> None:
        """Move excess funds to cold storage"""
        if not self.wallet.needs_rebalancing():
            return
            
        excess_amount = self.wallet.get_excess_amount()
        cold_wallet = self.wallet.get_cold_wallet()
        
        if not cold_wallet:
            raise WalletError(f"No cold wallet found for {self.wallet.currency_type}")
            
        # Create internal transfer transactions
        self.process_transaction(excess_amount, 'withdrawal', 'cold_storage_transfer')
        WalletManager(cold_wallet).process_transaction(
            excess_amount,
            'deposit',
            'hot_wallet_transfer'
        )
        
        self.wallet.last_rebalance = timezone.now()
        self.wallet.save()
