"""
Example configuration for cryptocurrency payment settings.
Copy this file to settings.py and configure appropriate values.
"""
from django.conf import settings

# Security Settings
# Security Settings - REQUIRED
# Configure these in your environment variables
API_TIMEOUT = None  # Seconds, configure in environment
MAX_WITHDRAWALS_PER_HOUR = None  # Count, configure in environment
MAX_WITHDRAWALS_TO_ADDRESS = None  # Count per week, configure in environment
MAX_ADDRESS_RISK_SCORE = None  # 0-100 (lower is safer), configure in environment
MAX_TRANSACTION_AMOUNT = None  # Maximum amount per transaction, configure in environment

# Node Configuration - REQUIRED
# Configure these in your environment variables
BTC_MIN_CONFIRMATIONS = None  # Required confirmations (default: 2), configure in environment
XMR_MIN_CONFIRMATIONS = None  # Required confirmations (default: 10), configure in environment
USDT_MIN_CONFIRMATIONS = None  # Required confirmations (default: 10), configure in environment
DEPOSIT_ADDRESS_EXPIRY = None  # Hours until deposit address expires (default: 2)

"""
Required Environment Variables:
CRYPTO_API_TIMEOUT=<int>  # API timeout in seconds
MAX_WITHDRAWALS_PER_HOUR=<int>  # Maximum withdrawals per hour
MAX_WITHDRAWALS_TO_ADDRESS=<int>  # Maximum withdrawals to single address per week
MAX_ADDRESS_RISK_SCORE=<int>  # Maximum risk score for addresses (0-100)
MAX_TRANSACTION_AMOUNT=<decimal>  # Maximum amount per transaction
BTC_MIN_CONFIRMATIONS=<int>  # Required confirmations for Bitcoin
XMR_MIN_CONFIRMATIONS=<int>  # Required confirmations for Monero
BLOCKCHAIN_ANALYSIS_SERVICE=<url>  # Optional: URL for blockchain analysis service
BLOCKCHAIN_ANALYSIS_KEY=<key>  # Optional: API key for blockchain analysis service
"""

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
