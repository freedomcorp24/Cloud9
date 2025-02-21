from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import CryptoWallet, CryptoTransaction
from ..wallet import WalletManager
from decimal import Decimal

User = get_user_model()

class WalletManagerTests(TestCase):
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
            balance=Decimal('0.0')
        )
        self.wallet_manager = WalletManager(self.wallet)

    def test_process_deposit(self):
        """Test deposit processing"""
        self.wallet_manager.process_transaction(
            amount=Decimal('1.0'),
            transaction_type='deposit',
            tx_hash='test_hash'
        )
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('1.0'))
        
        transaction = CryptoTransaction.objects.get(tx_hash='test_hash')
        self.assertEqual(transaction.amount_crypto, Decimal('1.0'))
        self.assertEqual(transaction.transaction_type, 'deposit')
        self.assertEqual(transaction.status, 'pending')

    def test_process_withdrawal(self):
        """Test withdrawal processing"""
        # Setup initial balance
        self.wallet.balance = Decimal('2.0')
        self.wallet.save()
        
        self.wallet_manager.process_transaction(
            amount=Decimal('1.0'),
            transaction_type='withdrawal',
            tx_hash='test_withdrawal'
        )
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('1.0'))
        
        transaction = CryptoTransaction.objects.get(tx_hash='test_withdrawal')
        self.assertEqual(transaction.amount_crypto, Decimal('1.0'))
        self.assertEqual(transaction.transaction_type, 'withdrawal')

    def test_insufficient_funds(self):
        """Test withdrawal with insufficient funds"""
        with self.assertRaises(ValueError):
            self.wallet_manager.process_transaction(
                amount=Decimal('1.0'),
                transaction_type='withdrawal',
                tx_hash='test_insufficient'
            )
