"""
Cryptocurrency node integration module.

This module provides base classes and implementations for interacting with
cryptocurrency nodes (Bitcoin, Monero, and USDT/Ethereum).
"""

"""Node integration for cryptocurrency services."""
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional, Union, List, Type

import requests
from django.conf import settings
from django.utils import timezone
from web3 import Web3
from eth_account import Account

from .exceptions import (
    NodeError, NodeConnectionError, NodeResponseError,
    TransactionError, InsufficientFundsError
)
from .services.bitcoin import BitcoinRPCService
from .services.monero import MoneroRPCService
from .services.ethereum import EthereumService
from .models import CryptoWallet
from .settings.defaults import (
    BTC_NODE_URL, BTC_NODE_USER, BTC_NODE_PASS, BTC_WALLET, BTC_MIN_FEE_RATE,
    XMR_NODE_URL, XMR_RPC_PORT, XMR_NODE_USER, XMR_NODE_PASS, XMR_WALLET_FILENAME,
    ETH_NODE_URL, ETH_CHAIN_ID, ETH_GAS_LIMIT, USDT_CONTRACT_ADDRESS, USDT_ABI_PATH,
    CRYPTO_API_TIMEOUT, REQUIRED_CONFIRMATIONS
)

logger = logging.getLogger(__name__)

class NodeError(Exception):
    """Base exception for node-related errors"""
    pass

class InvalidAddressError(NodeError):
    """Raised when an invalid address is provided"""
    pass

class InsufficientFundsError(NodeError):
    """Raised when there are insufficient funds for a transaction"""
    pass

class TransactionError(NodeError):
    """Raised when a transaction fails"""
    pass

class NodeConnectionError(NodeError):
    """Raised when connection to node fails"""
    pass

class CryptoNode(ABC):
    """Abstract base class for cryptocurrency node integration"""
    
    def __init__(self):
        """Initialize node connection settings"""
        self.timeout = int(CRYPTO_API_TIMEOUT)
        self._wallet_keys: Dict[str, str] = {}
        
    @abstractmethod
    def check_balance(self, address: str) -> Decimal:
        """
        Check balance for address
        
        Args:
            address: Cryptocurrency address to check
            
        Returns:
            Current balance as Decimal
            
        Raises:
            InvalidAddressError: If address format is invalid
            NodeError: If node communication fails
        """
        pass
    
    @abstractmethod
    def validate_transaction(self, tx_hash: str, min_confirmations: int) -> bool:
        """Validate transaction has required confirmations"""
        pass
    
    @abstractmethod
    def broadcast_transaction(self, signed_tx: str) -> str:
        """Broadcast signed transaction to network"""
        pass
        
    @abstractmethod
    def generate_deposit_address(self) -> str:
        """Generate a new one-time deposit address"""
        pass
        
    @abstractmethod
    def check_address(self, address: str) -> Optional[Dict[str, Any]]:
        """Check if address has received payment and get confirmation status"""
        pass
        
    @abstractmethod
    def create_transaction(self,
                         source_address: str,
                         destination_address: str,
                         amount: Decimal,
                         fee_rate: Optional[Decimal] = None,
                         min_confirmations: Optional[int] = None) -> str:
        """
        Create and sign a new transaction
        
        Args:
            source_address: Source address
            destination_address: Destination address
            amount: Amount to send
            fee_rate: Optional custom fee rate
            min_confirmations: Required confirmations for inputs
            
        Returns:
            Transaction hash
            
        Raises:
            InvalidAddressError: If addresses are invalid
            InsufficientFundsError: If source has insufficient funds
            TransactionError: If transaction creation fails
            NodeError: If node communication fails
        """
        pass
        
    @abstractmethod
    def get_transaction_details(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get detailed transaction information
        
        Args:
            tx_hash: Transaction hash to look up
            
        Returns:
            Dict containing:
            - amount: Transaction amount
            - fee: Transaction fee
            - confirmations: Number of confirmations
            - timestamp: Transaction timestamp
            - block_height: Block number containing transaction
            - addresses: Source and destination addresses
            - status: Transaction status (pending/confirmed/failed)
            
        Raises:
            TransactionError: If transaction not found
            NodeError: If node communication fails
        """
        pass
        
    def _validate_address_format(self, address: str) -> bool:
        """
        Validate cryptocurrency address format
        
        Args:
            address: Address to validate
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            NodeError: If validation fails due to node communication error
        """
        raise NotImplementedError("Subclasses must implement _validate_address_format")
        
    def _handle_node_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle node API response and extract result
        
        Args:
            response: Response from node API
            
        Returns:
            Response result data
            
        Raises:
            NodeError: If response indicates an error
        """
        try:
            data = response.json()
            if 'error' in data and data['error'] is not None:
                logger.error(f"Node error: {data['error']}")
                raise NodeError(f"Node returned error: {data['error']}")
            return data.get('result', {})
        except ValueError as e:
            logger.error(f"Failed to parse node response: {str(e)}")
            raise NodeError(f"Invalid response from node: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error handling node response: {str(e)}")
            raise NodeError(f"Node communication error: {str(e)}")
            
    def _log_transaction(self, tx_type: str, tx_hash: str, **details) -> None:
        """Log transaction details"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': tx_type,
            'hash': tx_hash,
            **details
        }
        logger.info(f"Transaction {tx_type}: {json.dumps(log_data)}")
        
    def get_required_confirmations(self) -> int:
        """Get required confirmations for this currency"""
        raise NotImplementedError("Subclasses must implement get_required_confirmations")

class BitcoinNode(CryptoNode):
    """Bitcoin full node integration"""
    def __init__(self):
        super().__init__()
        self.node_url = BTC_NODE_URL
        self.auth = (BTC_NODE_USER, BTC_NODE_PASS)
        self.min_fee_rate = BTC_MIN_FEE_RATE
        
    def get_required_confirmations(self) -> int:
        """Get required confirmations for Bitcoin"""
        return REQUIRED_CONFIRMATIONS['BTC']
        
    def _rpc_call(self, method: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """Make RPC call to Bitcoin node"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": "cloud9",
                "method": method,
                "params": params or []
            }
            response = requests.post(
                self.node_url,
                json=payload,
                auth=self.auth,
                timeout=self.timeout
            )
            return self._handle_node_response(response)
        except Exception as e:
            logger.error(f"Bitcoin RPC call failed: {str(e)}")
            raise NodeConnectionError(f"Failed to communicate with Bitcoin node: {str(e)}")
    
    def check_balance(self, address: str) -> float:
        response = self._rpc_call("getreceivedbyaddress", [address, 0])
        return float(response['result'])
    
    def validate_transaction(self, tx_hash: str, min_confirmations: int = 6) -> bool:
        response = self._rpc_call("gettransaction", [tx_hash])
        if 'result' in response:
            return response['result']['confirmations'] >= min_confirmations
        return False
    
    def broadcast_transaction(self, signed_tx: str) -> str:
        """Broadcast signed Bitcoin transaction"""
        try:
            response = self._rpc_call("sendrawtransaction", [signed_tx])
            if 'result' not in response:
                raise NodeError("Failed to broadcast Bitcoin transaction")
            return response['result']
        except Exception as e:
            logger.error(f"Failed to broadcast Bitcoin transaction: {str(e)}")
            raise NodeError(f"Failed to broadcast Bitcoin transaction: {str(e)}")
        
    def generate_deposit_address(self) -> str:
        """Generate new one-time Bitcoin deposit address that expires after 2 hours"""
        try:
            # Generate new address using full node
            response = self._rpc_call("getnewaddress", ["", "bech32"])
            if 'result' not in response:
                raise NodeError("Failed to generate Bitcoin address")
                
            address = response['result']
            
            # Create wallet record with expiry
            CryptoWallet.objects.create(
                address=address,
                currency_type='BTC',
                deposit_address=address,
                deposit_address_expires=timezone.now() + timedelta(hours=2),
                status='active'
            )
            
            return address
        except Exception as e:
            logger.error(f"Failed to generate Bitcoin deposit address: {str(e)}")
            raise NodeError(f"Failed to generate Bitcoin deposit address: {str(e)}")
        
    def check_address(self, address: str) -> Dict[str, Any]:
        """Check if Bitcoin address has received payment and handle expiry"""
        try:
            # Check if address exists and hasn't expired
            try:
                wallet = CryptoWallet.objects.get(
                    address=address,
                    currency_type='BTC',
                    status='active'
                )
                
                if wallet.is_deposit_address_expired():
                    wallet.status = 'inactive'
                    wallet.save()
                    return {
                        'is_valid': False,
                        'expired': True,
                        'amount': Decimal('0'),
                        'confirmations': 0,
                        'transactions': []
                    }
            except CryptoWallet.DoesNotExist:
                pass
                
            if not self._validate_address_format(address):
                return {
                    'is_valid': False,
                    'expired': False,
                    'amount': Decimal('0'),
                    'confirmations': 0,
                    'transactions': []
                }
                
            response = self._rpc_call("listreceivedbyaddress", [1, True, True, address])
            transactions = []
            
            if 'result' in response and response['result']:
                for tx in response['result']:
                    transactions.append({
                        'txid': tx['txid'],
                        'amount': Decimal(str(tx['amount'])),
                        'confirmations': tx.get('confirmations', 0),
                        'category': 'receive'
                    })
                    
            return {
                'is_valid': True,
                'amount': sum(tx['amount'] for tx in transactions),
                'confirmations': min(tx['confirmations'] for tx in transactions) if transactions else 0,
                'transactions': transactions
            }
        except Exception as e:
            logger.error(f"Failed to check address: {str(e)}")
            return {
                'is_valid': True,
                'amount': Decimal('0'),
                'confirmations': 0,
                'transactions': []
            }
            
            if wallet.expires_at and wallet.expires_at < timezone.now():
                wallet.is_active = False
                wallet.save()
                return {
                    'is_valid': False,
                    'expired': True,
                    'amount': Decimal('0'),
                    'confirmations': 0,
                    'transactions': []
                }
                
            if not self._validate_address_format(address):
                return {
                    'is_valid': False,
                    'expired': False,
                    'amount': Decimal('0'),
                    'confirmations': 0,
                    'transactions': []
                }
            
        try:
            response = self._rpc_call("listreceivedbyaddress", [1, True, True, address])
            transactions = []
            
            if 'result' in response and response['result']:
                for tx in response['result']:
                    transactions.append({
                        'txid': tx['txid'],
                        'amount': Decimal(str(tx['amount'])),
                        'confirmations': tx.get('confirmations', 0),
                        'category': 'receive'
                    })
                    
            return {
                'is_valid': True,
                'amount': sum(tx['amount'] for tx in transactions),
                'confirmations': min(tx['confirmations'] for tx in transactions) if transactions else 0,
                'transactions': transactions
            }
        except Exception as e:
            logger.error(f"Failed to check address: {str(e)}")
            return {
                'is_valid': True,
                'amount': Decimal('0'),
                'confirmations': 0,
                'transactions': []
            }
            
        tx = response['result'][0]
        return {
            'tx_hash': tx['txid'],
            'amount': float(tx['amount']),
            'confirmations': tx.get('confirmations', 0)
        }

class MoneroNode(CryptoNode):
    """Monero full node integration"""
    def __init__(self):
        super().__init__()
        self.node_url = XMR_NODE_URL
        self.rpc_port = XMR_RPC_PORT
        self.auth = (XMR_NODE_USER, XMR_NODE_PASS)
        self._wallet_paths = {
            'hot': f"/wallet/{XMR_WALLET_FILENAME}",
            'cold': "/wallet/cold_storage",
            'user': ""  # Default wallet
        }
        
    def get_required_confirmations(self) -> int:
        """Get required confirmations for Monero"""
        return REQUIRED_CONFIRMATIONS['XMR']
        
    def _rpc_call(self, method: str, params: Optional[Dict[str, Any]] = None, wallet_type: str = 'user') -> Dict[str, Any]:
        """Make RPC call to Monero node"""
        url = f"{self.node_url}:{self.rpc_port}{self._wallet_paths[wallet_type]}/json_rpc"
        payload = {
            "jsonrpc": "2.0",
            "id": "cloud9",
            "method": method,
            "params": params or {}
        }
        response = requests.post(url, json=payload)
        return response.json()
    
    def check_balance(self, address: str) -> float:
        response = self._rpc_call(
            "get_balance",
            {"address": address}
        )
        return float(response['result']['balance'])
    
    def validate_transaction(self, tx_hash: str, min_confirmations: int = 10) -> bool:
        response = self._rpc_call(
            "get_transfer_by_txid",
            {"txid": tx_hash}
        )
        if 'result' in response:
            return response['result']['confirmations'] >= min_confirmations
        return False
    
    def broadcast_transaction(self, signed_tx: str) -> str:
        response = self._rpc_call(
            "submit_transfer",
            {"tx_as_hex": signed_tx}
        )
        return response['result']['tx_hash']
        
    def generate_deposit_address(self) -> str:
        """Generate new Monero deposit address"""
        response = self._rpc_call("create_address", {"account_index": 0})
        if 'result' not in response or 'address' not in response['result']:
            raise ValueError("Failed to generate Monero address")
        return response['result']['address']
        
    def check_address(self, address: str) -> Dict[str, Any]:
        """Check if Monero address has received payment"""
        if not self._validate_address_format(address):
            return {
                'is_valid': False,
                'amount': Decimal('0'),
                'confirmations': 0,
                'transactions': []
            }
            
        try:
            response = self._rpc_call(
                "get_transfers",
                {
                    "in": True,
                    "account_index": 0,
                    "address": address
                }
            )
            
            transactions = []
            total_amount = Decimal('0')
            min_confirmations = float('inf')
            
            if 'result' in response and 'in' in response['result']:
                for tx in response['result']['in']:
                    if tx['address'] == address:
                        amount = Decimal(str(tx['amount'])) / Decimal('1e12')
                        confirmations = tx.get('confirmations', 0)
                        
                        transactions.append({
                            'txid': tx['txid'],
                            'amount': amount,
                            'confirmations': confirmations,
                            'timestamp': tx.get('timestamp')
                        })
                        
                        total_amount += amount
                        min_confirmations = min(min_confirmations, confirmations)
                        
            return {
                'is_valid': True,
                'amount': total_amount,
                'confirmations': min_confirmations if min_confirmations != float('inf') else 0,
                'transactions': transactions
            }
        except Exception as e:
            logger.error(f"Failed to check Monero address: {str(e)}")
            return {
                'is_valid': True,
                'amount': Decimal('0'),
                'confirmations': 0,
                'transactions': []
            }

class USDTNode(CryptoNode):
    """USDT (ERC20) node integration"""
    
    def __init__(self):
        super().__init__()
        self.node_url = ETH_NODE_URL
        self.contract_address = USDT_CONTRACT_ADDRESS
        self.web3 = Web3(Web3.HTTPProvider(self.node_url))
        self.chain_id = ETH_CHAIN_ID
        
        try:
            with open(USDT_ABI_PATH) as f:
                self.contract = self.web3.eth.contract(
                    address=self.contract_address,
                    abi=json.load(f)
                )
        except Exception as e:
            logger.error(f"Failed to initialize USDT contract: {str(e)}")
            raise NodeError(f"Failed to initialize USDT node: {str(e)}")
            
    def get_required_confirmations(self) -> int:
        """Get required confirmations for USDT"""
        return REQUIRED_CONFIRMATIONS['USDT']
        
    def _validate_address_format(self, address: str) -> bool:
        """Validate Ethereum address format"""
        return self.web3.is_address(address)
        
    def check_balance(self, address: str) -> Decimal:
        """Check USDT balance for address"""
        try:
            balance = self.contract.functions.balanceOf(address).call()
            return Decimal(str(balance)) / Decimal('1e6')
        except Exception as e:
            logger.error(f"Failed to check USDT balance: {str(e)}")
            raise NodeError(f"Failed to check USDT balance: {str(e)}")
    
    def validate_transaction(self, tx_hash: str, min_confirmations: int = 10) -> bool:
        """Validate USDT transaction confirmations"""
        try:
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            if not receipt:
                return False
                
            current_block = self.web3.eth.block_number
            confirmations = current_block - receipt['blockNumber'] + 1
            return confirmations >= min_confirmations
        except Exception as e:
            logger.error(f"Failed to validate USDT transaction: {str(e)}")
            return False
    
    def broadcast_transaction(self, signed_tx: str) -> str:
        """Broadcast signed USDT transaction"""
        try:
            # Remove '0x' prefix if present
            tx_hex = signed_tx[2:] if signed_tx.startswith('0x') else signed_tx
            tx_hash = self.web3.eth.send_raw_transaction(bytes.fromhex(tx_hex))
            
            # Wait for transaction receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            if not receipt.status:
                raise NodeError("USDT transaction failed")
                
            return self.web3.to_hex(tx_hash)
        except Exception as e:
            logger.error(f"Failed to broadcast USDT transaction: {str(e)}")
            raise NodeError(f"Failed to broadcast USDT transaction: {str(e)}")
        
    def generate_deposit_address(self) -> str:
        """Generate new USDT deposit address"""
        try:
            account = Account.create()
            address = account.address
            
            # Create wallet record with expiry
            CryptoWallet.objects.create(
                address=address,
                currency_type='USDT',
                deposit_address=address,
                deposit_address_expires=timezone.now() + timedelta(hours=2),
                status='active'
            )
            
            return address
        except Exception as e:
            logger.error(f"Failed to generate USDT address: {str(e)}")
            raise NodeError(f"Failed to generate USDT address: {str(e)}")
        
    def create_transaction(self,
                         source_address: str,
                         destination_address: str,
                         amount: Decimal,
                         fee_rate: Optional[Decimal] = None,
                         min_confirmations: Optional[int] = None) -> str:
        """Create USDT transaction"""
        if not self._validate_address_format(source_address):
            raise InvalidAddressError("Invalid source address")
        if not self._validate_address_format(destination_address):
            raise InvalidAddressError("Invalid destination address")
            
        try:
            # Convert amount to USDT decimals
            amount_wei = int(amount * Decimal('1e6'))
            
            # Get nonce
            nonce = self.web3.eth.get_transaction_count(source_address)
            
            # Build transaction
            tx = self.contract.functions.transfer(
                destination_address,
                amount_wei
            ).build_transaction({
                'chainId': self.chain_id,
                'gas': ETH_GAS_LIMIT,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': nonce,
            })
            
            return self.web3.to_hex(tx)
        except Exception as e:
            logger.error(f"Failed to create USDT transaction: {str(e)}")
            raise TransactionError(f"Failed to create USDT transaction: {str(e)}")
            
    def get_transaction_details(self, tx_hash: str) -> Dict[str, Any]:
        """Get USDT transaction details"""
        try:
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            if not receipt:
                raise TransactionError("Transaction not found")
                
            tx = self.web3.eth.get_transaction(tx_hash)
            current_block = self.web3.eth.block_number
            block = self.web3.eth.get_block(receipt['blockNumber'])
            
            # Decode transfer event
            transfer_event = None
            for log in receipt['logs']:
                if log['address'].lower() == self.contract_address.lower():
                    try:
                        transfer_event = self.contract.events.Transfer().process_log(log)
                        break
                    except:
                        continue
                        
            if not transfer_event:
                raise TransactionError("Not a USDT transfer transaction")
                
            return {
                'amount': Decimal(str(transfer_event['args']['value'])) / Decimal('1e6'),
                'fee': Decimal(str(receipt['gasUsed'] * tx['gasPrice'])) / Decimal('1e18'),
                'confirmations': current_block - receipt['blockNumber'] + 1,
                'timestamp': block['timestamp'],
                'block_height': receipt['blockNumber'],
                'addresses': {
                    'from': transfer_event['args']['from'],
                    'to': transfer_event['args']['to']
                },
                'status': 'confirmed' if receipt['status'] else 'failed'
            }
        except Exception as e:
            logger.error(f"Failed to get USDT transaction details: {str(e)}")
            raise TransactionError(f"Failed to get USDT transaction details: {str(e)}")
        
    def check_address(self, address: str) -> Dict[str, Any]:
        """Check if USDT address has received payment"""
        if not self._validate_address_format(address):
            return {
                'is_valid': False,
                'amount': Decimal('0'),
                'confirmations': 0,
                'transactions': []
            }
            
        try:
            # Get USDT balance
            balance = self.contract.functions.balanceOf(address).call()
            balance_decimal = Decimal(str(balance)) / Decimal('1e6')
            
            # Get recent transfers
            block_number = self.web3.eth.block_number
            from_block = max(0, block_number - 10000)  # Last ~10k blocks
            
            transfer_filter = self.contract.events.Transfer.create_filter(
                fromBlock=from_block,
                argument_filters={'to': address}
            )
            
            transactions = []
            for event in transfer_filter.get_all_entries():
                tx_receipt = self.web3.eth.get_transaction_receipt(
                    event['transactionHash']
                )
                
                amount = Decimal(str(event['args']['value'])) / Decimal('1e6')
                confirmations = block_number - event['blockNumber'] + 1
                
                transactions.append({
                    'txid': self.web3.to_hex(event['transactionHash']),
                    'from': event['args']['from'],
                    'amount': amount,
                    'confirmations': confirmations,
                    'block_number': event['blockNumber']
                })
                
            return {
                'is_valid': True,
                'amount': balance_decimal,
                'confirmations': min(tx['confirmations'] for tx in transactions) if transactions else 0,
                'transactions': transactions
            }
        except Exception as e:
            logger.error(f"Failed to check USDT address: {str(e)}")
            return {
                'is_valid': True,
                'amount': Decimal('0'),
                'confirmations': 0,
                'transactions': []
            }

class NodeFactory:
    """Factory for creating cryptocurrency node instances"""
    
    _instances: Dict[str, CryptoNode] = {}
    _node_classes: Dict[str, Type[CryptoNode]] = {
        'BTC': BitcoinNode,
        'XMR': MoneroNode,
        'USDT': USDTNode
    }
    
    @classmethod
    def get_node(cls, currency_type: str) -> CryptoNode:
        """
        Get or create node instance for currency type
        
        Args:
            currency_type: Type of cryptocurrency (BTC/XMR/USDT)
            
        Returns:
            CryptoNode instance
            
        Raises:
            ValueError: If currency type not supported
            NodeError: If node initialization fails
        """
        currency_type = currency_type.upper()
        
        if currency_type not in cls._instances:
            if currency_type not in cls._node_classes:
                raise ValueError(f"Unsupported currency type: {currency_type}")
                
            node_class = cls._node_classes[currency_type]
            try:
                instance = node_class()
                # Verify instance implements all abstract methods
                for method in CryptoNode.__abstractmethods__:  # type: ignore
                    if not hasattr(instance, method):
                        raise NotImplementedError(
                            f"{currency_type} node missing required method: {method}"
                        )
                cls._instances[currency_type] = instance
            except Exception as e:
                logger.error(f"Failed to initialize {currency_type} node: {str(e)}")
                raise NodeError(f"Failed to initialize {currency_type} node: {str(e)}")
                
        return cls._instances[currency_type]
        
    @classmethod
    def reset_instances(cls) -> None:
        """Reset all node instances (useful for testing)"""
        cls._instances.clear()
