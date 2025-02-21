from abc import ABC, abstractmethod
import requests
from django.conf import settings
from typing import Dict, Any
import json

class CryptoNode(ABC):
    """Abstract base class for cryptocurrency node integration"""
    
    @abstractmethod
    def check_balance(self, address: str) -> float:
        pass
    
    @abstractmethod
    def validate_transaction(self, tx_hash: str, min_confirmations: int) -> bool:
        pass
    
    @abstractmethod
    def broadcast_transaction(self, signed_tx: str) -> str:
        pass
        
    @abstractmethod
    def generate_deposit_address(self) -> str:
        """Generate a new one-time deposit address"""
        pass
        
    @abstractmethod
    def check_address(self, address: str) -> Dict[str, Any]:
        """Check if address has received payment and get confirmation status"""
        pass

class BitcoinNode(CryptoNode):
    """Bitcoin full node integration"""
    def __init__(self):
        self.node_url = settings.BTC_NODE_URL
        self.auth = (settings.BTC_NODE_USER, settings.BTC_NODE_PASS)
    
    def _rpc_call(self, method: str, params: list = None) -> Dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": "cloud9",
            "method": method,
            "params": params or []
        }
        response = requests.post(
            self.node_url,
            json=payload,
            auth=self.auth
        )
        return response.json()
    
    def check_balance(self, address: str) -> float:
        response = self._rpc_call("getreceivedbyaddress", [address, 0])
        return float(response['result'])
    
    def validate_transaction(self, tx_hash: str, min_confirmations: int = 6) -> bool:
        response = self._rpc_call("gettransaction", [tx_hash])
        if 'result' in response:
            return response['result']['confirmations'] >= min_confirmations
        return False
    
    def broadcast_transaction(self, signed_tx: str) -> str:
        response = self._rpc_call("sendrawtransaction", [signed_tx])
        return response['result']
        
    def generate_deposit_address(self) -> str:
        """Generate new Bitcoin deposit address"""
        response = self._rpc_call("getnewaddress")
        if 'result' not in response:
            raise ValueError("Failed to generate Bitcoin address")
        return response['result']
        
    def check_address(self, address: str) -> Dict[str, Any]:
        """Check if Bitcoin address has received payment"""
        response = self._rpc_call("listreceivedbyaddress", [1, True, True, address])
        if 'result' not in response or not response['result']:
            return None
            
        tx = response['result'][0]
        return {
            'tx_hash': tx['txid'],
            'amount': float(tx['amount']),
            'confirmations': tx.get('confirmations', 0)
        }

class MoneroNode(CryptoNode):
    """Monero full node integration"""
    def __init__(self):
        self.node_url = settings.XMR_NODE_URL
        self.auth = (settings.XMR_NODE_USER, settings.XMR_NODE_PASS)
        
    def _rpc_call(self, method: str, params: Dict = None) -> Dict[str, Any]:
        url = f"{self.node_url}:{self.rpc_port}/json_rpc"
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
        response = self._rpc_call(
            "get_transfers",
            {
                "in": True,
                "account_index": 0,
                "address": address
            }
        )
        if 'result' not in response or 'in' not in response['result']:
            return None
            
        transfers = response['result']['in']
        if not transfers:
            return None
            
        tx = transfers[-1]
        return {
            'tx_hash': tx['txid'],
            'amount': float(tx['amount']),
            'confirmations': tx.get('confirmations', 0)
        }

class USDTNode(CryptoNode):
    """USDT full node integration"""
    def __init__(self):
        self.node_url = settings.USDT_NODE_URL
        self.auth = (settings.USDT_NODE_USER, settings.USDT_NODE_PASS)
        
    def _rpc_call(self, method: str, params: list = None) -> Dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": "cloud9",
            "method": method,
            "params": params or []
        }
        response = requests.post(
            self.node_url,
            json=payload,
            auth=self.auth
        )
        return response.json()
    
    def check_balance(self, address: str) -> float:
        response = self._rpc_call("omni_getbalance", [address, 31])  # 31 is USDT
        return float(response['result']['balance'])
    
    def validate_transaction(self, tx_hash: str, min_confirmations: int = 10) -> bool:
        response = self._rpc_call("omni_gettransaction", [tx_hash])
        if 'result' in response:
            return response['result']['confirmations'] >= min_confirmations
        return False
    
    def broadcast_transaction(self, signed_tx: str) -> str:
        response = self._rpc_call("sendrawtransaction", [signed_tx])
        return response['result']
        
    def generate_deposit_address(self) -> str:
        """Generate new USDT deposit address"""
        response = self._rpc_call("getnewaddress")
        if 'result' not in response:
            raise ValueError("Failed to generate USDT address")
        return response['result']
        
    def check_address(self, address: str) -> Dict[str, Any]:
        """Check if USDT address has received payment"""
        response = self._rpc_call("omni_getbalance", [address, 31])  # 31 is USDT
        if 'result' not in response:
            return None
            
        balance = response['result']
        if float(balance['balance']) > 0:
            tx_response = self._rpc_call("omni_listtransactions", [address])
            if 'result' in tx_response and tx_response['result']:
                tx = tx_response['result'][-1]
                return {
                    'tx_hash': tx['txid'],
                    'amount': float(tx['amount']),
                    'confirmations': tx.get('confirmations', 0)
                }
        return None

class NodeFactory:
    """Factory for creating cryptocurrency node instances"""
    @staticmethod
    def get_node(currency_type: str) -> CryptoNode:
        currency_type = currency_type.upper()
        if currency_type == 'BTC':
            return BitcoinNode()
        elif currency_type == 'XMR':
            return MoneroNode()
        elif currency_type == 'USDT':
            return USDTNode()
        raise ValueError(f"Unsupported currency type: {currency_type}")
