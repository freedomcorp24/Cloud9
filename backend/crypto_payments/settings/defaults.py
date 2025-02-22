"""Default settings for cryptocurrency payment processing."""

from decimal import Decimal
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
CONTRACT_DIR = BASE_DIR / 'contracts'

# Node URLs and credentials (override in .env)
BTC_NODE_URL = 'http://localhost:8332'
BTC_NODE_USER = 'bitcoinrpc'
BTC_NODE_PASS = 'rpcpassword'
BTC_WALLET = 'hot_wallet'
BTC_MIN_FEE_RATE = 10  # sat/byte

XMR_NODE_URL = 'http://localhost:18081'
XMR_RPC_PORT = 18081
XMR_NODE_USER = 'monerorp'
XMR_NODE_PASS = 'rpcpassword'
XMR_WALLET_FILENAME = 'hot_wallet'

ETH_NODE_URL = 'http://localhost:8545'
ETH_CHAIN_ID = 1  # Mainnet
ETH_GAS_LIMIT = 100000
USDT_CONTRACT_ADDRESS = '0xdac17f958d2ee523a2206206994597c13d831ec7'  # Mainnet USDT
USDT_ABI_PATH = str(CONTRACT_DIR / 'usdt_abi.json')

# Transaction limits (override in admin or .env)
MAX_TRANSACTION_AMOUNT = {
    'BTC': Decimal('1.0'),
    'XMR': Decimal('10.0'),
    'USDT': Decimal('10000.0')
}

MIN_TRANSACTION_AMOUNT = {
    'BTC': Decimal('0.0001'),
    'XMR': Decimal('0.01'),
    'USDT': Decimal('10.0')
}

# Confirmation thresholds
REQUIRED_CONFIRMATIONS = {
    'BTC': 6,
    'XMR': 10,
    'USDT': 12
}

# Security settings
MAX_FAILED_ATTEMPTS = 3
LOCKOUT_DURATION_MINUTES = 30
DEPOSIT_ADDRESS_EXPIRY = 2  # hours

# API settings
CRYPTO_API_TIMEOUT = 30  # seconds

# Hot wallet settings
HOT_WALLET_BALANCE_THRESHOLD = {
    'BTC': Decimal('1.0'),
    'XMR': Decimal('10.0'),
    'USDT': Decimal('10000.0')
}

# Cold storage settings
COLD_STORAGE_ADDRESSES = {
    'BTC': '',  # Set in .env
    'XMR': '',  # Set in .env
    'USDT': ''  # Set in .env
}

# Exchange rate settings
EXCHANGE_RATE_UPDATE_INTERVAL = 900  # 15 minutes
EXCHANGE_RATE_SOURCE = 'coingecko'  # Options: coingecko, binance, kraken

# Logging settings
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_LEVEL = 'INFO'

# Override with environment-specific settings
try:
    from .local import *  # noqa
except ImportError:
    pass
