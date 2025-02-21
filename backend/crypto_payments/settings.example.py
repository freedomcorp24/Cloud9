"""
Example configuration for cryptocurrency payment settings.
Copy this file to settings.py and configure appropriate values.
"""
from django.conf import settings

# Security Settings
# Security Settings - REQUIRED
# Configure these in your environment variables
API_TIMEOUT = settings.CRYPTO_API_TIMEOUT  # Seconds
MAX_WITHDRAWALS_PER_HOUR = settings.MAX_WITHDRAWALS_PER_HOUR  # Count
MAX_WITHDRAWALS_TO_ADDRESS = settings.MAX_WITHDRAWALS_TO_ADDRESS  # Count per week
MAX_ADDRESS_RISK_SCORE = settings.MAX_ADDRESS_RISK_SCORE  # 0-100 (lower is safer)
MAX_TRANSACTION_AMOUNT = settings.MAX_TRANSACTION_AMOUNT  # Maximum amount per transaction

# Node Configuration - REQUIRED
# Configure these in your environment variables
BTC_MIN_CONFIRMATIONS = settings.BTC_MIN_CONFIRMATIONS  # Required confirmations
XMR_MIN_CONFIRMATIONS = settings.XMR_MIN_CONFIRMATIONS  # Required confirmations

"""
Required Environment Variables:
CRYPTO_API_TIMEOUT=<int>
MAX_WITHDRAWALS_PER_HOUR=<int>
MAX_WITHDRAWALS_TO_ADDRESS=<int>
MAX_ADDRESS_RISK_SCORE=<int>
MAX_TRANSACTION_AMOUNT=<decimal>
BTC_MIN_CONFIRMATIONS=<int>
XMR_MIN_CONFIRMATIONS=<int>
"""
