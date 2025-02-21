from django.conf import settings
from . import settings as crypto_settings
from django.db import models
from django.utils import timezone
from typing import Dict, Any, Optional
from decimal import Decimal
import hmac
import hashlib
import time
import logging
import requests
from .models import CryptoWallet, CryptoTransaction
from .models.blacklist import AddressBlacklist
from .node_integration import NodeFactory

logger = logging.getLogger(__name__)

class SecurityCheck:
    """Security checks for cryptocurrency transactions"""
    
    @staticmethod
    def verify_signature(payload: Dict[str, Any], signature: str) -> bool:
        """Verify HMAC signature of payload"""
        key = settings.PAYMENT_SERVER_KEY.encode()
        message = str(payload).encode()
        expected = hmac.new(key, message, hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected)
    
    @staticmethod
    def validate_withdrawal_limits(wallet: CryptoWallet, amount: Decimal) -> bool:
        """
        Check withdrawal against daily/monthly limits and transaction history
        Returns False if any security check fails
        """
        try:
            daily_limit = Decimal(settings.DAILY_WITHDRAWAL_LIMIT)
            monthly_limit = Decimal(settings.MONTHLY_WITHDRAWAL_LIMIT)
            
            # Check 24h withdrawals
            from django.utils import timezone
            daily_total = CryptoTransaction.objects.filter(
                wallet=wallet,
                transaction_type='withdrawal',
                status__in=['pending', 'completed'],
                created_at__gte=timezone.now() - timezone.timedelta(days=1)
            ).aggregate(total=models.Sum('amount_crypto'))['total'] or 0
            
            if daily_total + amount > daily_limit:
                return False
                
            # Check monthly withdrawals
            monthly_total = CryptoTransaction.objects.filter(
                wallet=wallet,
                transaction_type='withdrawal',
                status__in=['pending', 'completed'],
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).aggregate(total=models.Sum('amount_crypto'))['total'] or 0
            
            if monthly_total + amount > monthly_limit:
                return False
            
            # Check for suspicious patterns
            recent_withdrawals = CryptoTransaction.objects.filter(
                wallet=wallet,
                transaction_type='withdrawal',
                created_at__gte=timezone.now() - timezone.timedelta(hours=1)
            ).count()
            
            if recent_withdrawals >= settings.MAX_WITHDRAWALS_PER_HOUR:
                return False
            
            return True
        except Exception as e:
            # Log the error but fail closed for security
            logger.error(f"Error validating withdrawal limits: {str(e)}")
            return False
    
    @staticmethod
    def check_address_history(address: str) -> bool:
        """
        Check if withdrawal address has suspicious history
        Integrates with blockchain analysis services and local blacklist
        """
        try:
            # Check local blacklist
            if AddressBlacklist.objects.filter(address=address).exists():
                return False
            
            # Check recent withdrawal history
            recent_withdrawals = CryptoTransaction.objects.filter(
                destination_address=address,
                transaction_type='withdrawal',
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count()
            
            if recent_withdrawals >= settings.MAX_WITHDRAWALS_TO_ADDRESS:
                return False
            
            # Check blockchain analysis service if configured
            analysis_service = settings.BLOCKCHAIN_ANALYSIS_SERVICE
            analysis_key = settings.BLOCKCHAIN_ANALYSIS_KEY
            
            if analysis_service and analysis_key:
                try:
                    response = requests.get(
                        f"{analysis_service}/check/{address}",
                        headers={'Authorization': f'Bearer {analysis_key}'},
                        timeout=settings.API_TIMEOUT
                    )
                    if response.status_code == 200:
                        result = response.json()
                        return result.get('risk_score', 100) <= settings.MAX_ADDRESS_RISK_SCORE
                except requests.exceptions.RequestException as e:
                    logger.error(f"Blockchain analysis service error: {str(e)}")
                    return False
            
            return True
        except Exception as e:
            # Log the error but fail closed for security
            logger.error(f"Error checking address history: {str(e)}")
            return False

class PaymentServer:
    """
    Separate payment server for secure transaction processing
    """
    def __init__(self):
        self.security = SecurityCheck()
    
    def process_withdrawal(
        self,
        wallet: CryptoWallet,
        amount: Decimal,
        destination: str,
        signature: str
    ) -> Optional[str]:
        """
        Process withdrawal with comprehensive security checks
        Returns transaction hash if successful
        """
        try:
            payload = {
                'wallet_id': wallet.id,
                'amount': str(amount),
                'destination': destination,
                'timestamp': int(time.time())
            }
            
            # Security checks
            if not self.security.verify_signature(payload, signature):
                logger.warning(f"Invalid signature for withdrawal from wallet {wallet.id}")
                raise ValueError("Invalid transaction signature")
                
            if not self.security.validate_withdrawal_limits(wallet, amount):
                logger.warning(f"Withdrawal limit exceeded for wallet {wallet.id}")
                raise ValueError("Withdrawal limit exceeded")
                
            if not self.security.check_address_history(destination):
                logger.warning(f"Suspicious destination address: {destination}")
                raise ValueError("Destination address flagged as suspicious")
            
            # Verify wallet balance
            if wallet.balance < amount:
                logger.warning(f"Insufficient balance in wallet {wallet.id}")
                raise ValueError("Insufficient balance")
            
            # Process withdrawal through full node
            node = NodeFactory.get_node(wallet.currency)
            
            # Create and sign transaction
            signed_tx = self._create_signed_transaction(
                wallet, amount, destination
            )
            
            # Broadcast through full node
            tx_hash = node.broadcast_transaction(signed_tx)
            
            # Record transaction
            transaction = CryptoTransaction.objects.create(
                wallet=wallet,
                tx_hash=tx_hash,
                amount_crypto=amount,
                transaction_type='withdrawal',
                status='pending',
                destination_address=destination
            )
            
            # Update wallet balance
            wallet.balance -= amount
            wallet.save()
            
            logger.info(f"Withdrawal processed successfully: {tx_hash}")
            return tx_hash
            
        except Exception as e:
            logger.error(f"Withdrawal processing failed: {str(e)}")
            raise
    
    def _create_signed_transaction(
        self,
        wallet: CryptoWallet,
        amount: Decimal,
        destination: str
    ) -> str:
        """
        Create and sign transaction with security checks
        Implementation depends on cryptocurrency type
        """
        try:
            # Get node for currency
            node = NodeFactory.get_node(wallet.currency)
            
            # Additional security checks before signing
            if not self._validate_transaction_parameters(wallet, amount, destination):
                raise ValueError("Invalid transaction parameters")
            
            # Create transaction (actual implementation in node integration)
            return node.create_transaction(
                source_address=wallet.address,
                destination_address=destination,
                amount=amount
            )
        except Exception as e:
            logger.error(f"Failed to create transaction: {str(e)}")
            raise
            
    def _validate_transaction_parameters(
        self,
        wallet: CryptoWallet,
        amount: Decimal,
        destination: str
    ) -> bool:
        """Validate transaction parameters before signing"""
        try:
            # Check amount is positive and within limits
            if amount <= 0 or amount > settings.MAX_TRANSACTION_AMOUNT:
                return False
                
            # Verify destination address format
            if not self._is_valid_address_format(wallet.currency, destination):
                return False
                
            # Check for recent failed attempts
            recent_failures = CryptoTransaction.objects.filter(
                wallet=wallet,
                status='failed',
                created_at__gte=timezone.now() - timezone.timedelta(hours=1)
            ).count()
            
            if recent_failures >= settings.MAX_FAILED_ATTEMPTS:
                return False
                
            return True
        except Exception as e:
            logger.error(f"Transaction parameter validation failed: {str(e)}")
            return False
            
    def _is_valid_address_format(self, currency: str, address: str) -> bool:
        """Validate cryptocurrency address format"""
        try:
            if currency.upper() == 'BTC':
                # Bitcoin address validation
                return len(address) >= 26 and len(address) <= 35
            elif currency.upper() == 'XMR':
                # Monero address validation
                return len(address) == 95
            return False
        except Exception:
            return False
    
    def verify_deposit(
        self,
        wallet: CryptoWallet,
        tx_hash: str
    ) -> bool:
        """
        Verify deposit through full node with security checks
        """
        try:
            # Get node for currency
            node = NodeFactory.get_node(wallet.currency)
            
            # Verify transaction exists and has required confirmations
            if not node.validate_transaction(tx_hash):
                logger.warning(f"Transaction validation failed for {tx_hash}")
                return False
            
            # Check for duplicate deposits
            if CryptoTransaction.objects.filter(
                wallet=wallet,
                tx_hash=tx_hash,
                transaction_type='deposit'
            ).exists():
                logger.warning(f"Duplicate deposit attempt: {tx_hash}")
                return False
            
            # Verify transaction details through node
            tx_details = node.get_transaction_details(tx_hash)
            if not tx_details:
                logger.warning(f"Could not fetch transaction details: {tx_hash}")
                return False
            
            # Record verified deposit
            CryptoTransaction.objects.create(
                wallet=wallet,
                tx_hash=tx_hash,
                amount_crypto=Decimal(tx_details['amount']),
                transaction_type='deposit',
                status='completed'
            )
            
            # Update wallet balance
            wallet.balance += Decimal(tx_details['amount'])
            wallet.save()
            
            logger.info(f"Deposit verified successfully: {tx_hash}")
            return True
            
        except Exception as e:
            logger.error(f"Deposit verification failed: {str(e)}")
            return False
