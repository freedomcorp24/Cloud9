"""Bitcoin node integration service."""
from django.conf import settings
import requests
import json
import logging
from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime, timedelta
from django.utils import timezone

from ..exceptions import (
    NodeError, NodeConnectionError, NodeResponseError,
    TransactionError, InsufficientFundsError
)

logger = logging.getLogger(__name__)

class BitcoinRPCService:
    """Service for interacting with Bitcoin node via RPC."""
    
    def __init__(self):
        """Initialize Bitcoin RPC service with node connection details."""
        self.rpc_url = settings.BTC_NODE_URL
        self.auth = (settings.BTC_NODE_USER, settings.BTC_NODE_PASS)
        self.wallet = settings.BTC_WALLET
        
        # Verify node connection on init
        try:
            self._make_request('getnetworkinfo')
        except Exception as e:
            logger.error(f"Failed to connect to Bitcoin node: {str(e)}")
            raise NodeConnectionError("Could not establish connection to Bitcoin node")
    
    def _make_request(self, method: str, params: Optional[list] = None) -> Dict:
        """Make RPC request to Bitcoin node."""
        headers = {'Content-Type': 'application/json'}
        payload = {
            'jsonrpc': '2.0',
            'id': '0',
            'method': method,
            'params': params if params else []
        }
        
        try:
            response = requests.post(
                self.rpc_url,
                headers=headers,
                auth=self.auth,
                data=json.dumps(payload),
                timeout=settings.CRYPTO_API_TIMEOUT
            )
            response.raise_for_status()
            result = response.json()
            
            if 'error' in result and result['error'] is not None:
                raise NodeResponseError(f"Bitcoin RPC error: {result['error']}")
                
            return result['result']
        except requests.exceptions.RequestException as e:
            logger.error(f"Bitcoin RPC request failed: {str(e)}")
            raise NodeError(f"Failed to communicate with Bitcoin node: {str(e)}")
    
    def create_address(self) -> Dict:
        """Create new one-time Bitcoin deposit address."""
        try:
            # Generate new address using native segwit (bech32)
            result = self._make_request('getnewaddress', ['', 'bech32'])
            
            # Create wallet record with expiry
            from ..models import CryptoWallet
            address = CryptoWallet.objects.create(
                address=result,
                currency='BTC',
                wallet_type='deposit',
                is_active=True,
                expires_at=timezone.now() + timedelta(hours=2)
            )
            
            return {
                'address': result,
                'expires_at': (timezone.now() + timedelta(hours=2)).isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to create Bitcoin address: {str(e)}")
            raise NodeError(f"Failed to create Bitcoin address: {str(e)}")
    
    def get_balance(self, address: str) -> Dict:
        """Get balance for address."""
        try:
            # Get unspent outputs for address
            unspent = self._make_request('listunspent', [0, 9999999, [address]])
            
            # Calculate total balance
            total = sum(Decimal(str(utxo['amount'])) for utxo in unspent)
            confirmed = sum(
                Decimal(str(utxo['amount']))
                for utxo in unspent
                if utxo['confirmations'] >= settings.REQUIRED_CONFIRMATIONS['BTC']
            )
            
            return {
                'total': total,
                'confirmed': confirmed,
                'pending': total - confirmed
            }
        except Exception as e:
            logger.error(f"Failed to get Bitcoin balance: {str(e)}")
            raise NodeError(f"Failed to get Bitcoin balance: {str(e)}")
    
    def transfer(self, destination: str, amount: Decimal, fee_rate: Optional[int] = None) -> Dict:
        """Create Bitcoin transfer transaction."""
        try:
            # Validate amount
            if amount <= 0:
                raise ValueError("Amount must be positive")
                
            # Set fee rate if provided
            options = {}
            if fee_rate is not None:
                options['fee_rate'] = fee_rate
            
            # Create raw transaction
            tx_hex = self._make_request('createrawtransaction', [
                [],  # inputs - will be selected automatically
                {destination: float(amount)}  # outputs
            ])
            
            # Fund raw transaction
            funded_tx = self._make_request('fundrawtransaction', [
                tx_hex,
                options
            ])
            
            # Sign transaction
            signed_tx = self._make_request('signrawtransactionwithwallet', [
                funded_tx['hex']
            ])
            
            if not signed_tx['complete']:
                raise TransactionError("Failed to sign transaction")
            
            # Broadcast transaction
            tx_id = self._make_request('sendrawtransaction', [
                signed_tx['hex']
            ])
            
            return {
                'txid': tx_id,
                'fee': funded_tx['fee'],
                'hex': signed_tx['hex']
            }
        except Exception as e:
            logger.error(f"Failed to create Bitcoin transfer: {str(e)}")
            if 'insufficient funds' in str(e).lower():
                raise InsufficientFundsError("Insufficient funds for transfer")
            raise NodeError(f"Failed to create Bitcoin transfer: {str(e)}")
    
    def check_transaction(self, tx_hash: str) -> Dict:
        """Check transaction status."""
        try:
            tx = self._make_request('gettransaction', [tx_hash])
            
            return {
                'status': 'confirmed' if tx['confirmations'] >= settings.REQUIRED_CONFIRMATIONS['BTC'] else 'pending',
                'confirmations': tx['confirmations'],
                'amount': Decimal(str(tx['amount'])),
                'fee': Decimal(str(tx.get('fee', 0))),
                'timestamp': datetime.fromtimestamp(tx['time'])
            }
        except Exception as e:
            logger.error(f"Failed to check Bitcoin transaction: {str(e)}")
            raise NodeError(f"Failed to check Bitcoin transaction: {str(e)}")
