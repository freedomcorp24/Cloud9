from django.db import models
from django.conf import settings
import hashlib
import secrets
from .models import CryptoWallet, Transaction

class WalletManager:
    """
    Manages cryptocurrency wallets and transactions
    """
    def __init__(self, wallet: CryptoWallet):
        self.wallet = wallet
        
    @classmethod
    def create_wallet(cls, user, currency_type):
        """Create a new wallet for a user"""
        wallet_id = hashlib.sha256(
            f"{user.id}:{currency_type}:{secrets.token_hex(16)}".encode()
        ).hexdigest()
        
        wallet = CryptoWallet.objects.create(
            user=user,
            wallet_id=wallet_id,
            currency_type=currency_type,
            balance=0
        )
        return cls(wallet)
    
    def generate_deposit_address(self, expires_in=7200):
        """Generate one-time deposit address"""
        address = hashlib.sha256(
            f"{self.wallet.wallet_id}:{secrets.token_hex(16)}".encode()
        ).hexdigest()
        
        self.wallet.deposit_address = address
        self.wallet.deposit_address_expires = expires_in
        self.wallet.save()
        
        return address
        
    def process_transaction(self, amount, transaction_type, reference=None):
        """Process a transaction on the wallet"""
        if transaction_type == 'deposit':
            self.wallet.balance += amount
        elif transaction_type == 'withdrawal':
            if self.wallet.balance < amount:
                raise ValueError("Insufficient funds")
            self.wallet.balance -= amount
            
        self.wallet.save()
        
        Transaction.objects.create(
            wallet=self.wallet,
            amount=amount,
            transaction_type=transaction_type,
            reference=reference
        )
