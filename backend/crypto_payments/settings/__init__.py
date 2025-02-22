"""
Cryptocurrency payment settings module.

This module provides settings for cryptocurrency payment processing,
including node configurations, transaction limits, and security thresholds.

Settings can be overridden in three ways (in order of precedence):
1. Environment variables
2. Django settings
3. Local settings file (local.py)

Default values are defined in defaults.py
"""

import os
from django.conf import settings
from .defaults import *  # noqa

# Override with environment variables
ENV_PREFIXES = ('BTC_', 'XMR_', 'ETH_', 'USDT_', 'MAX_', 'MIN_', 'REQUIRED_')
for key, value in os.environ.items():
    if any(key.startswith(prefix) for prefix in ENV_PREFIXES):
        globals()[key] = value

# Override with Django settings
for setting in dir(settings):
    if setting.isupper() and any(setting.startswith(prefix) for prefix in ENV_PREFIXES):
        globals()[setting] = getattr(settings, setting)

# Validate required settings
required_settings = [
    'BTC_NODE_URL',
    'XMR_NODE_URL',
    'ETH_NODE_URL',
    'USDT_CONTRACT_ADDRESS'
]

for setting in required_settings:
    if not globals().get(setting):
        raise ValueError(f"Required setting {setting} is not configured")
