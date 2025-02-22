from django.core.cache import cache
from django.conf import settings
import requests
from decimal import Decimal
from typing import Dict, Optional

class ExchangeRateError(Exception):
    """Raised when there's an error fetching exchange rates."""
    pass

class CoinGeckoExchangeBackend:
    """CoinGecko exchange rate backend."""
    
    BASE_URL = 'https://api.coingecko.com/api/v3'
    CRYPTO_IDS = {
        'BTC': 'bitcoin',
        'XMR': 'monero',
        'USDT': 'tether'
    }
    
    @classmethod
    def get_exchange_rates(cls) -> Dict[str, Decimal]:
        """Get exchange rates for supported cryptocurrencies."""
        try:
            # Get rates for all supported cryptocurrencies
            response = requests.get(
                f"{cls.BASE_URL}/simple/price",
                params={
                    'ids': ','.join(cls.CRYPTO_IDS.values()),
                    'vs_currencies': 'usd'
                }
            )
            response.raise_for_status()
            data = response.json()
            
            rates = {}
            for crypto, gecko_id in cls.CRYPTO_IDS.items():
                rates[crypto] = Decimal(str(data[gecko_id]['usd']))
            
            return rates
            
        except (requests.RequestException, KeyError, ValueError) as e:
            raise ExchangeRateError(f"Failed to fetch exchange rates: {str(e)}")

def get_exchange_rate(currency: str) -> Decimal:
    """Get exchange rate for cryptocurrency with 15-minute caching."""
    if currency.upper() not in CoinGeckoExchangeBackend.CRYPTO_IDS:
        raise ValueError(f"Unsupported cryptocurrency: {currency}")
        
    cache_key = f'exchange_rate_{currency.upper()}'
    rate = cache.get(cache_key)
    
    if rate is None:
        try:
            rates = CoinGeckoExchangeBackend.get_exchange_rates()
            rate = rates.get(currency.upper())
            if rate:
                # Cache for 15 minutes
                cache.set(cache_key, rate, 15 * 60)
            else:
                raise ExchangeRateError(f"No rate available for {currency}")
        except Exception as e:
            raise ExchangeRateError(f"Failed to fetch exchange rate: {str(e)}")
    
    return Decimal(str(rate))
