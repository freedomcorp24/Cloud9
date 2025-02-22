from celery import shared_task
from django.core.cache import cache
import logging
from .utils.exchange_rates import CoinGeckoExchangeBackend

logger = logging.getLogger(__name__)

@shared_task
def update_exchange_rates():
    """Task to update cryptocurrency exchange rates"""
    try:
        rates = CoinGeckoExchangeBackend.get_exchange_rates()
        for currency, rate in rates.items():
            cache_key = f'exchange_rate_{currency}'
            cache.set(cache_key, rate, 15 * 60)  # Cache for 15 minutes
        logger.info(f"Updated exchange rates: {rates}")
    except Exception as e:
        logger.error(f"Failed to update exchange rates: {str(e)}")
