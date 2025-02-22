from django.conf import settings
import requests
import json
import logging
from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime, timedelta
from django.utils import timezone

from ..exceptions import NodeError, NodeConnectionError, NodeResponseError, TransactionError

logger = logging.getLogger(__name__)

class MoneroRPCService:
    """Service for interacting with Monero node via RPC."""
    
    def __init__(self):
        """Initialize Monero RPC service with node connection details."""
        self.rpc_url = settings.XMR_NODE_URL
        self.rpc_port = settings.XMR_RPC_PORT
        self.endpoint = f"{self.rpc_url}:{self.rpc_port}/json_rpc"
        self.auth = None
        if hasattr(settings, 'XMR_NODE_USER') and hasattr(settings, 'XMR_NODE_PASS'):
            self.auth = (settings.XMR_NODE_USER, settings.XMR_NODE_PASS)
            
        # Verify node connection on init
        try:
            self._make_request('get_version')
        except Exception as e:
            logger.error(f"Failed to connect to Monero node: {str(e)}")
            raise NodeConnectionError("Could not establish connection to Monero node")
        
    def _make_request(self, method: str, params: Optional[Dict] = None) -> Dict:
        """Make RPC request to Monero node."""
        headers = {'Content-Type': 'application/json'}
        payload = {
            'jsonrpc': '2.0',
            'id': '0',
            'method': method,
            'params': params if params else {}
        }
            
        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                data=json.dumps(payload),
                timeout=settings.CRYPTO_API_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Monero RPC request failed: {str(e)}")
            raise NodeError(f"Failed to communicate with Monero node: {str(e)}")
        
    def create_address(self) -> Dict:
        """Create new one-time Monero deposit address."""
        try:
            result = self._make_request('create_address', {
                'account_index': 0,
                'label': f'deposit_{int(timezone.now().timestamp())}'
            })
            
            if 'error' in result:
                raise NodeResponseError(f"Failed to create address: {result['error']['message']}")
                
            # Create wallet record with expiry
            from ..models import CryptoWallet
            CryptoWallet.objects.create(
                address=result['address'],
                currency='XMR',
                wallet_type='deposit',
                is_active=True,
                expires_at=timezone.now() + timedelta(hours=2)
            )
            
            return {
                'address': result['address'],
                'view_key': result.get('view_key'),
                'expires_at': (timezone.now() + timedelta(hours=2)).isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to create Monero address: {str(e)}")
            raise NodeError(f"Failed to create Monero address: {str(e)}")
        
    def get_balance(self, address: str) -> Dict:
        """Get balance for address."""
        try:
            params = {'address': address}
            result = self._make_request('get_balance', params)
            
            if 'error' in result:
                raise NodeResponseError(f"Failed to get balance: {result['error']['message']}")
                
            return {
                'total': Decimal(str(result.get('balance', 0))) / Decimal('1e12'),
                'unlocked': Decimal(str(result.get('unlocked_balance', 0))) / Decimal('1e12'),
                'pending': Decimal(str(result.get('pending_balance', 0))) / Decimal('1e12')
            }
        except Exception as e:
            logger.error(f"Failed to get Monero balance: {str(e)}")
            raise NodeError(f"Failed to get Monero balance: {str(e)}")
        
    def transfer(self, destination: str, amount: float, payment_id: Optional[str] = None) -> Dict:
        """Create transfer transaction."""
        try:
            params = {
                'destinations': [{
                    'address': destination,
                    'amount': int(amount * 1e12)  # Convert XMR to atomic units
                }],
                'priority': 1,
                'ring_size': 11
            }
            if payment_id:
                params['payment_id'] = payment_id
                
            result = self._make_request('transfer', params)
            
            if 'error' in result:
                raise NodeError(f"Monero transfer failed: {result['error']['message']}")
                
            return result
        except Exception as e:
            logger.error(f"Failed to create Monero transfer: {str(e)}")
            raise NodeError(f"Failed to create Monero transfer: {str(e)}")
        
    def get_transfers(self, address: str) -> Dict:
        """Get transfer history for address."""
        try:
            params = {'address': address}
            result = self._make_request('get_transfers', params)
            if 'error' in result:
                raise NodeResponseError(f"Failed to get transfers: {result['error']['message']}")
            return result
        except Exception as e:
            logger.error(f"Failed to get transfer history: {str(e)}")
            raise NodeError(f"Failed to get transfer history: {str(e)}")
        
    def check_transaction(self, tx_hash: str) -> Dict:
        """Check transaction status."""
        try:
            params = {'txid': tx_hash}
            result = self._make_request('get_transfer_by_txid', params)
            if 'error' in result:
                raise NodeResponseError(f"Failed to check transaction: {result['error']['message']}")
            return {
                'status': result.get('status', 'failed'),
                'confirmations': result.get('confirmations', 0),
                'amount': Decimal(str(result.get('amount', 0))) / Decimal('1e12'),
                'fee': Decimal(str(result.get('fee', 0))) / Decimal('1e12'),
                'timestamp': datetime.fromtimestamp(result.get('timestamp', 0))
            }
        except Exception as e:
            logger.error(f"Failed to check transaction: {str(e)}")
            raise NodeError(f"Failed to check transaction: {str(e)}")
