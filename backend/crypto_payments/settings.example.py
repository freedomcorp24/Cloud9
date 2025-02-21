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

# Required Environment Variables - DO NOT SET VALUES HERE
# Configure all values through environment variables for security

# Node Configuration
BTC_MIN_CONFIRMATIONS = None  # Required confirmations for Bitcoin
XMR_MIN_CONFIRMATIONS = None  # Required confirmations for Monero
USDT_MIN_CONFIRMATIONS = None  # Required confirmations for USDT
DEPOSIT_ADDRESS_EXPIRY = None  # Hours until deposit address expires

# Node Authentication
BTC_NODE_URL = None  # Bitcoin node RPC URL
BTC_NODE_USER = None  # Bitcoin node RPC username
BTC_NODE_PASS = None  # Bitcoin node RPC password

XMR_NODE_URL = None  # Monero node RPC URL
XMR_NODE_USER = None  # Monero node RPC username
XMR_NODE_PASS = None  # Monero node RPC password

USDT_NODE_URL = None  # USDT node RPC URL
USDT_NODE_USER = None  # USDT node RPC username
USDT_NODE_PASS = None  # USDT node RPC password

"""
Required Environment Variables:
CRYPTO_API_TIMEOUT=<int>  # API timeout in seconds
BTC_MIN_CONFIRMATIONS=<int>  # Required confirmations for Bitcoin (default: 2)
XMR_MIN_CONFIRMATIONS=<int>  # Required confirmations for Monero (default: 10)
USDT_MIN_CONFIRMATIONS=<int>  # Required confirmations for USDT (default: 10)
DEPOSIT_ADDRESS_EXPIRY=<int>  # Hours until deposit address expires (default: 2)

BTC_NODE_URL=<url>  # Bitcoin node RPC URL
BTC_NODE_USER=<str>  # Bitcoin node RPC username
BTC_NODE_PASS=<str>  # Bitcoin node RPC password

XMR_NODE_URL=<url>  # Monero node RPC URL
XMR_NODE_USER=<str>  # Monero node RPC username
XMR_NODE_PASS=<str>  # Monero node RPC password

USDT_NODE_URL=<url>  # USDT node RPC URL
USDT_NODE_USER=<str>  # USDT node RPC username
USDT_NODE_PASS=<str>  # USDT node RPC password
"""

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
