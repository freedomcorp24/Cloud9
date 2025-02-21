from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from ..models import CryptoWallet, CryptoTransaction
from ..payment_server import SecurityCheck, PaymentServer
from decimal import Decimal
import hmac
import hashlib
import time

User = get_user_model()

class SecurityCheckTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.wallet = CryptoWallet.objects.create(
            user=self.user,
            currency='BTC',
            address='test_address',
            private_key='encrypted_key',
            public_key='public_key',
            balance=Decimal('1.0')
        )
        self.security = SecurityCheck()

    def test_signature_verification(self):
        """Test HMAC signature verification"""
        payload = {
            'wallet_id': self.wallet.id,
            'amount': '0.5',
            'destination': 'test_dest',
            'timestamp': int(time.time())
        }
        
        # Create valid signature
        key = settings.PAYMENT_SERVER_KEY.encode()
        message = str(payload).encode()
        valid_sig = hmac.new(key, message, hashlib.sha256).hexdigest()
        
        # Test valid signature
        self.assertTrue(
            self.security.verify_signature(payload, valid_sig)
        )
        
        # Test invalid signature
        invalid_sig = 'invalid_signature'
        self.assertFalse(
            self.security.verify_signature(payload, invalid_sig)
        )

    def test_withdrawal_limits(self):
        """Test withdrawal limit validation"""
        # Test within daily limit
        self.assertTrue(
            self.security.validate_withdrawal_limits(
                self.wallet,
                Decimal('0.1')
            )
        )
        
        # Test exceeding daily limit
        settings.DAILY_WITHDRAWAL_LIMIT = '0.05'
        self.assertFalse(
            self.security.validate_withdrawal_limits(
                self.wallet,
                Decimal('0.1')
            )
        )

class PaymentServerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.wallet = CryptoWallet.objects.create(
            user=self.user,
            currency='BTC',
            address='test_address',
            private_key='encrypted_key',
            public_key='public_key',
            balance=Decimal('1.0')
        )
        self.payment_server = PaymentServer()

    def test_withdrawal_processing(self):
        """Test withdrawal processing with security checks"""
        amount = Decimal('0.5')
        destination = 'test_destination'
        
        # Create valid signature
        payload = {
            'wallet_id': self.wallet.id,
            'amount': str(amount),
            'destination': destination,
            'timestamp': int(time.time())
        }
        key = settings.PAYMENT_SERVER_KEY.encode()
        message = str(payload).encode()
        signature = hmac.new(key, message, hashlib.sha256).hexdigest()
        
        # Test successful withdrawal
        tx_hash = self.payment_server.process_withdrawal(
            self.wallet,
            amount,
            destination,
            signature
        )
        self.assertIsNotNone(tx_hash)
        
        # Verify transaction was created
        transaction = CryptoTransaction.objects.get(tx_hash=tx_hash)
        self.assertEqual(transaction.amount_crypto, amount)
        self.assertEqual(transaction.transaction_type, 'withdrawal')
        
        # Test invalid signature
        with self.assertRaises(ValueError):
            self.payment_server.process_withdrawal(
                self.wallet,
                amount,
                destination,
                'invalid_signature'
            )
