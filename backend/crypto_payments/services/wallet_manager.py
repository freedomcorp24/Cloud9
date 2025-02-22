from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from typing import Optional, Tuple
import logging
from ..models import CryptoWallet
from ..exceptions import InsufficientFundsError, WalletConfigError
from ..node_integration import NodeFactory

logger = logging.getLogger(__name__)

class WalletManager:
    """Manages hot/cold wallet operations and rebalancing"""
    
    def __init__(self, currency: str):
        self.currency = currency
        self.node = NodeFactory.get_node(currency)
    
    @transaction.atomic
    def rebalance_hot_wallet(self, hot_wallet: CryptoWallet) -> Optional[str]:
        """
        Rebalance hot wallet by moving excess funds to cold storage
        Returns transaction hash if rebalancing occurred
        """
        if not hot_wallet.needs_rebalancing():
            return None
            
        cold_wallet = hot_wallet.get_cold_wallet()
        if not cold_wallet:
            logger.error(f"No cold wallet found for {self.currency}")
            raise WalletConfigError(f"No cold wallet configured for {self.currency}")
            
        excess_amount = hot_wallet.get_excess_amount()
        
        # Create and broadcast transaction
        tx_hash = self.node.create_transaction(
            source_address=hot_wallet.address,
            destination_address=cold_wallet.address,
            amount=excess_amount
        )
        
        if tx_hash:
            # Update wallet balances
            hot_wallet.balance -= excess_amount
            cold_wallet.balance += excess_amount
            hot_wallet.last_rebalance = timezone.now()
            
            hot_wallet.save()
            cold_wallet.save()
            
            logger.info(
                f"Rebalanced {self.currency} hot wallet: {excess_amount} moved to cold storage"
            )
            
        return tx_hash
    
    @transaction.atomic
    def replenish_hot_wallet(
        self, 
        hot_wallet: CryptoWallet,
        amount: Decimal
    ) -> Optional[str]:
        """
        Move funds from cold storage to hot wallet
        Returns transaction hash if replenishment occurred
        """
        cold_wallet = hot_wallet.get_cold_wallet()
        if not cold_wallet:
            logger.error(f"No cold wallet found for {self.currency}")
            raise WalletConfigError(f"No cold wallet configured for {self.currency}")
            
        if cold_wallet.balance < amount:
            logger.error(f"Insufficient funds in cold wallet for {self.currency}")
            raise InsufficientFundsError("Insufficient funds in cold storage")
            
        # Create and broadcast transaction
        tx_hash = self.node.create_transaction(
            source_address=cold_wallet.address,
            destination_address=hot_wallet.address,
            amount=amount
        )
        
        if tx_hash:
            # Update wallet balances
            cold_wallet.balance -= amount
            hot_wallet.balance += amount
            hot_wallet.last_rebalance = timezone.now()
            
            hot_wallet.save()
            cold_wallet.save()
            
            logger.info(
                f"Replenished {self.currency} hot wallet with {amount} from cold storage"
            )
            
        return tx_hash
    
    def get_wallet_balances(self) -> Tuple[Decimal, Decimal]:
        """Get current hot and cold wallet balances"""
        hot_wallet = CryptoWallet.objects.filter(
            wallet_type='hot',
            currency=self.currency,
            is_active=True
        ).first()
        
        cold_wallet = CryptoWallet.objects.filter(
            wallet_type='cold', 
            currency=self.currency,
            is_active=True
        ).first()
        
        hot_balance = hot_wallet.balance if hot_wallet else Decimal('0')
        cold_balance = cold_wallet.balance if cold_wallet else Decimal('0')
        
        return hot_balance, cold_balance
