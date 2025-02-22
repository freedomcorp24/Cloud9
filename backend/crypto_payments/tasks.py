from celery import shared_task
from django.utils import timezone
from .models import CryptoWallet
from .services.wallet_manager import WalletManager
import logging

logger = logging.getLogger(__name__)

@shared_task
def rebalance_hot_wallets():
    """
    Periodic task to check and rebalance hot wallets
    Moves excess funds to cold storage when threshold is exceeded
    """
    currencies = ['BTC', 'XMR', 'USDT']
    
    for currency in currencies:
        try:
            # Get hot wallet for currency
            hot_wallet = CryptoWallet.objects.filter(
                wallet_type='hot',
                currency=currency,
                is_active=True
            ).first()
            
            if not hot_wallet:
                logger.warning(f"No hot wallet found for {currency}")
                continue
                
            if not hot_wallet.needs_rebalancing():
                continue
                
            # Rebalance wallet
            wallet_manager = WalletManager(currency)
            tx_hash = wallet_manager.rebalance_hot_wallet(hot_wallet)
            
            if tx_hash:
                logger.info(f"Rebalanced {currency} hot wallet: {tx_hash}")
                
        except Exception as e:
            logger.error(f"Error rebalancing {currency} hot wallet: {str(e)}")
