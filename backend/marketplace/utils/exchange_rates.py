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
    
    @classmethod
    def get_exchange_rates(cls) -> Dict[str, Decimal]:
        """Get exchange rates for all supported currencies."""
        try:
            # Get BTC/USD rate first as base
            btc_response = requests.get(
                f"{cls.BASE_URL}/simple/price",
                params={
                    'ids': 'bitcoin',
                    'vs_currencies': 'usd'
                }
            )
            btc_data = btc_response.json()
            btc_usd_rate = Decimal(str(btc_data['bitcoin']['usd']))
            
            # Get all fiat currency rates against USD
            fiat_response = requests.get(
                f"{cls.BASE_URL}/exchange_rates",
            )
            fiat_data = fiat_response.json()
            
            rates = {}
            usd_rates = fiat_data['rates']
            
            # Calculate rates for all supported currencies
            for currency in settings.OSCAR_CURRENCY_FORMAT.keys():
                if currency in usd_rates:
                    rate = Decimal(str(usd_rates[currency]['value']))
                    rates[currency] = rate / btc_usd_rate
            
            return rates
            
        except (requests.RequestException, KeyError, ValueError) as e:
            raise ExchangeRateError(f"Failed to fetch exchange rates: {str(e)}")

def get_exchange_rate(currency: str) -> Decimal:
    """Get exchange rate for currency with caching."""
    cache_key = f'exchange_rate_{currency}'
    rate = cache.get(cache_key)
    
    if rate is None:
        backend_class = settings.EXCHANGE_BACKEND
        try:
            rates = backend_class.get_exchange_rates()
            rate = rates.get(currency, Decimal('1.0'))
            cache.set(cache_key, rate, settings.CURRENCIES_CACHE_TIMEOUT)
        except ExchangeRateError:
            return Decimal('1.0')
    
    return Decimal(str(rate))
