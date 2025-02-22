from django.conf import settings
import requests
from typing import Optional

class NodeService:
    """Service for interacting with cryptocurrency nodes."""
    
    def __init__(self, currency_type: str):
        """Initialize node service."""
        self.currency_type = currency_type
        self.node_url = self._get_node_url()
        self.auth = self._get_auth()
    
    def _get_node_url(self) -> str:
        """Get appropriate node URL based on currency type."""
        if self.currency_type == 'BTC':
            return settings.BTC_NODE_URL
        elif self.currency_type == 'XMR':
            return settings.XMR_NODE_URL
        elif self.currency_type == 'USDT':
            return settings.USDT_NODE_URL
        raise ValueError(f"Unsupported currency type: {self.currency_type}")
    
    def _get_auth(self) -> Optional[tuple]:
        """Get authentication credentials if needed."""
        if self.currency_type == 'BTC':
            return (settings.BTC_RPC_USER, settings.BTC_RPC_PASSWORD)
        return None
    
    def check_balance(self, address: str) -> float:
        """Check balance of an address."""
        response = requests.get(
            f"{self.node_url}/balance",
            params={'address': address},
            auth=self.auth,
            timeout=settings.CRYPTO_API_TIMEOUT
        )
        response.raise_for_status()
        return float(response.json()['balance'])
    
    def validate_transaction(self, tx_hash: str, min_confirmations: int = 6) -> bool:
        """Validate a transaction has required confirmations."""
        response = requests.get(
            f"{self.node_url}/transaction",
            params={
                'hash': tx_hash,
                'confirmations': min_confirmations
            },
            auth=self.auth,
            timeout=settings.CRYPTO_API_TIMEOUT
        )
        response.raise_for_status()
        return response.json()['valid']
