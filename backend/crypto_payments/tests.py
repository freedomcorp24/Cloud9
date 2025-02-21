from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import CryptoWallet, CryptoTransaction, TransactionConfirmation

User = get_user_model()

class CryptoWalletTests(TestCase):
    databases = {'default'}
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.wallet = CryptoWallet.objects.create(
            user=self.user,
            currency='BTC',
            address='1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            private_key='test_private_key',
            public_key='test_public_key',
            balance=0.0,
            status='active'
        )

    def test_wallet_creation(self):
        self.assertEqual(self.wallet.user.username, 'testuser')
        self.assertEqual(self.wallet.currency, 'BTC')
        self.assertEqual(self.wallet.status, 'active')
        self.assertEqual(self.wallet.balance, 0.0)

    def test_wallet_str_representation(self):
        expected_str = "testuser's BTC Wallet (1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa)"
        self.assertEqual(str(self.wallet), expected_str)

class CryptoTransactionTests(TestCase):
    databases = {'default'}
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.wallet = CryptoWallet.objects.create(
            user=self.user,
            currency='BTC',
            address='1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            private_key='test_private_key',
            public_key='test_public_key',
            balance=1.0,
            status='active'
        )
        self.transaction = CryptoTransaction.objects.create(
            wallet=self.wallet,
            tx_hash='0x123456789abcdef',
            confirmations=3,
            required_confirmations=6,
            status='pending',
            transaction_type='deposit',
            amount_crypto=0.5,
            fee=0.0001
        )

    def test_transaction_creation(self):
        self.assertEqual(self.transaction.wallet, self.wallet)
        self.assertEqual(self.transaction.status, 'pending')
        self.assertEqual(self.transaction.transaction_type, 'deposit')
        self.assertEqual(self.transaction.amount_crypto, 0.5)

    def test_transaction_confirmation_status(self):
        self.assertFalse(self.transaction.is_confirmed)
        self.transaction.confirmations = 6
        self.transaction.save()
        self.assertTrue(self.transaction.is_confirmed)
