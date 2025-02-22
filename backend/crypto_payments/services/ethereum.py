from django.conf import settings
from web3 import Web3
from eth_account import Account
from typing import Dict, Optional
import json

class EthereumService:
    """Service for interacting with Ethereum node and USDT contract."""
    
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.ETH_NODE_URL))
        
        # Load USDT contract ABI
        with open(settings.USDT_ABI_PATH) as f:
            self.usdt_abi = json.load(f)
            
        self.usdt_contract = self.w3.eth.contract(
            address=settings.USDT_CONTRACT_ADDRESS,
            abi=self.usdt_abi
        )
        
    def create_address(self) -> Dict:
        """Create new Ethereum address."""
        account = Account.create()
        return {
            'address': account.address,
            'private_key': account.key.hex()
        }
        
    def get_eth_balance(self, address: str) -> float:
        """Get ETH balance for address."""
        balance_wei = self.w3.eth.get_balance(address)
        return self.w3.from_wei(balance_wei, 'ether')
        
    def get_usdt_balance(self, address: str) -> float:
        """Get USDT balance for address."""
        balance = self.usdt_contract.functions.balanceOf(address).call()
        return balance / 1e6  # Convert from USDT decimals
        
    def transfer_usdt(self, 
                     from_address: str,
                     to_address: str, 
                     amount: float,
                     private_key: str) -> str:
        """Transfer USDT tokens."""
        nonce = self.w3.eth.get_transaction_count(from_address)
        amount_wei = int(amount * 1e6)  # Convert to USDT decimals
        
        # Build transaction
        transaction = self.usdt_contract.functions.transfer(
            to_address,
            amount_wei
        ).build_transaction({
            'chainId': settings.ETH_CHAIN_ID,
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': nonce,
        })
        
        # Sign and send transaction
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction,
            private_key=private_key
        )
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return self.w3.to_hex(tx_hash)
        
    def check_transaction(self, tx_hash: str) -> Dict:
        """Check transaction status."""
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return {
                'status': receipt['status'],
                'block_number': receipt['blockNumber'],
                'confirmations': self.w3.eth.block_number - receipt['blockNumber']
            }
        except Exception:
            return {'status': 0, 'confirmations': 0}
