from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from unittest.mock import patch, MagicMock
from ..services import NodeService, PaymentProcessor
from ..models import CryptoWallet, CryptoTransaction
from decimal import Decimal

User = get_user_model()

class NodeServiceTests(TestCase):
    def setUp(self):
        self.node_service = NodeService('BTC')

    @patch('requests.get')
    def test_check_balance(self, mock_get):
        """Test balance checking"""
        mock_get.return_value = MagicMock(
            json=lambda: {'balance': '1.23456789'}
        )
        
        balance = self.node_service.check_balance('test_address')
        self.assertEqual(balance, '1.23456789')
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_validate_transaction(self, mock_get):
        """Test transaction validation"""
        mock_get.return_value = MagicMock(
            json=lambda: {'valid': True}
        )
        
        is_valid = self.node_service.validate_transaction('test_hash')
        self.assertTrue(is_valid)
        mock_get.assert_called_once()

class PaymentProcessorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.payment_processor = PaymentProcessor(self.user)

    def test_get_or_create_wallet(self):
        """Test wallet creation"""
        wallet_manager = self.payment_processor.get_or_create_wallet('BTC')
        self.assertIsNotNone(wallet_manager.wallet)
        self.assertEqual(wallet_manager.wallet.user, self.user)
        self.assertEqual(wallet_manager.wallet.currency, 'BTC')

    @patch('crypto_payments.services.NodeService.validate_transaction')
    def test_process_deposit(self, mock_validate):
        """Test deposit processing"""
        mock_validate.return_value = True
        
        success = self.payment_processor.process_deposit(
            Decimal('1.0'),
            'BTC',
            'test_hash'
        )
        
        self.assertTrue(success)
        wallet = CryptoWallet.objects.get(user=self.user, currency='BTC')
        self.assertEqual(wallet.balance, Decimal('1.0'))
