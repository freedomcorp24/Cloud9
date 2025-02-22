"""
Django settings for cloud9 project.
"""
from pathlib import Path
import environ
import os
from decimal import Decimal
from oscar.defaults import *
import dj_database_url

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# Security Settings
SECRET_KEY = env('DJANGO_SECRET_KEY', default='THC9CBD#2025!j8k3m4n5p6q7r8s9t0uvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ')
DEBUG = True  # Force debug mode for local testing
ALLOWED_HOSTS = ['*']  # Allow all hosts for local testing

# Security Headers - All disabled for local testing
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_PROXY_SSL_HEADER = None


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',

    # Third party
    'widget_tweaks',
    'haystack',
    'django_redis',
    'currencies',
    'djmoney',

    # Oscar apps - core
    'oscar.config.Shop',
    'oscar.apps.customer.apps.CustomerConfig',  # For user profiles
    'oscar.apps.address.apps.AddressConfig',  # For addresses
    'oscar.apps.catalogue.apps.CatalogueConfig',  # For products
    'oscar.apps.catalogue.reviews.apps.CatalogueReviewsConfig',
    'oscar.apps.partner.apps.PartnerConfig',  # For stock records
    'oscar.apps.basket.apps.BasketConfig',  # For shopping cart
    'oscar.apps.payment.apps.PaymentConfig',  # For payments
    'oscar.apps.offer.apps.OfferConfig',  # For promotions
    'oscar.apps.order.apps.OrderConfig',  # For orders
    'oscar.apps.checkout.apps.CheckoutConfig',  # For checkout
    'oscar.apps.shipping.apps.ShippingConfig',  # For shipping
    'oscar.apps.voucher.apps.VoucherConfig',  # For vouchers
    'oscar.apps.wishlists.apps.WishlistsConfig',  # For wishlists
    'oscar.apps.communication.apps.CommunicationConfig',  # For emails
    'oscar.apps.search.apps.SearchConfig',  # For search
    'oscar.apps.analytics.apps.AnalyticsConfig',  # For analytics

    # Oscar apps - dashboard
    'oscar.apps.dashboard.apps.DashboardConfig',
    'oscar.apps.dashboard.reports.apps.ReportsDashboardConfig',
    'oscar.apps.dashboard.users.apps.UsersDashboardConfig',
    'oscar.apps.dashboard.orders.apps.OrdersDashboardConfig',
    'oscar.apps.dashboard.catalogue.apps.CatalogueDashboardConfig',
    'oscar.apps.dashboard.offers.apps.OffersDashboardConfig',
    'oscar.apps.dashboard.partners.apps.PartnersDashboardConfig',
    'oscar.apps.dashboard.pages.apps.PagesDashboardConfig',
    'oscar.apps.dashboard.ranges.apps.RangesDashboardConfig',
    'oscar.apps.dashboard.reviews.apps.ReviewsDashboardConfig',
    'oscar.apps.dashboard.vouchers.apps.VouchersDashboardConfig',
    'oscar.apps.dashboard.communications.apps.CommunicationsDashboardConfig',
    'oscar.apps.dashboard.shipping.apps.ShippingDashboardConfig',
    
    # Custom apps
    'support.apps.SupportConfig',
    'marketplace.apps.MarketplaceConfig',
    'crypto_payments.apps.CryptoPaymentsConfig',
    'tor_access.apps.TorAccessConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'tor_access.middleware.javascript.NoJavaScriptMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'marketplace.middleware.vendor.VendorBondMiddleware',
    'marketplace.middleware.online.LastOnlineMiddleware',
    'marketplace.middleware.pgp.PGPAuthenticationMiddleware',
    'marketplace.middleware.auth.TransactionPINMiddleware',
    'oscar.apps.basket.middleware.BasketMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'tor_access.middleware.rate_limit.TorRateLimitMiddleware',
    'tor_access.middleware.captcha.TorCaptchaMiddleware',
    'marketplace.middleware.rate_limit.RateLimitMiddleware',
    'marketplace.middleware.basic_auth.BasicAuthMiddleware',
]

# Environment settings
DJANGO_ENV = env('DJANGO_ENV', default='development')
BASIC_AUTH_USERNAME = env('BASIC_AUTH_USERNAME', default='admin')
BASIC_AUTH_PASSWORD = env('BASIC_AUTH_PASSWORD', default='secure123')

ROOT_URLCONF = 'cloud9.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.core.context_processors.metadata',
            ],
        },
    },
]

WSGI_APPLICATION = 'cloud9.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://cloud9_user:secure_password@localhost:5432/cloud9_db',
        conn_max_age=600
    ),
    'payment': dj_database_url.config(
        env='PAYMENT_DATABASE_URL',
        default='postgresql://cloud9_user:secure_password@localhost:5433/cloud9_payment',
        conn_max_age=600
    ),
    'analytics': dj_database_url.config(
        env='ANALYTICS_DATABASE_URL',
        default='postgresql://cloud9_user:secure_password@localhost:5434/cloud9_analytics',
        conn_max_age=600
    )
}

DATABASE_ROUTERS = [
    'cloud9.routers.PaymentRouter',
    'cloud9.routers.AnalyticsRouter'
]
# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

from django.utils.translation import gettext_lazy as _

# Language settings
LANGUAGES = [
    ('en', _('English')),
    ('es', _('Spanish')),
    ('fr', _('French')),
    ('de', _('German')),
    ('it', _('Italian')),
    ('pt', _('Portuguese')),
    ('ru', _('Russian')),
    ('zh-hans', _('Simplified Chinese')),
    ('ja', _('Japanese')),
    ('ko', _('Korean')),
    ('ar', _('Arabic')),
    ('hi', _('Hindi')),
    ('tr', _('Turkish')),
    ('vi', _('Vietnamese')),
    ('th', _('Thai')),
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

LANGUAGE_COOKIE_NAME = 'cloud9_language'
LANGUAGE_COOKIE_AGE = 365 * 24 * 60 * 60  # 1 year
LANGUAGE_COOKIE_SECURE = True
LANGUAGE_COOKIE_HTTPONLY = True
LANGUAGE_COOKIE_SAMESITE = 'Strict'


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Site ID
SITE_ID = 1

# Supported Currencies
SUPPORTED_CURRENCIES = [
    ('USD', 'US Dollar'),
    ('EUR', 'Euro'),
    ('GBP', 'British Pound'),
    ('BTC', 'Bitcoin'),
    ('XMR', 'Monero'),
    ('USDT', 'Tether')
]

# Countries List
COUNTRIES = [
    ('US', 'United States'),
    ('CA', 'Canada'),
    ('GB', 'United Kingdom'),
    ('AU', 'Australia'),
    ('NZ', 'New Zealand'),
    ('DE', 'Germany'),
    ('FR', 'France'),
    ('ES', 'Spain'),
    ('IT', 'Italy'),
    ('NL', 'Netherlands')
]

# Oscar settings
OSCAR_SHOP_NAME = 'Cloud 9'
OSCAR_SHOP_TAGLINE = 'THC/CBD Marketplace'
OSCAR_DEFAULT_CURRENCY = 'USD'
OSCAR_ALLOW_ANON_CHECKOUT = False
OSCAR_REQUIRED_ADDRESS_FIELDS = ['first_name', 'last_name', 'line1', 'city', 'country']

# Search settings
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
        'EXCLUDED_INDEXES': [
            'oscar.apps.search.search_indexes.ProductIndex'
        ]
    },
}
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Security settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Payment Server Settings
PAYMENT_SERVER_KEY = env('PAYMENT_SERVER_KEY', default='THC9CBD#2025!PaymentKey')
DAILY_WITHDRAWAL_LIMIT = env('DAILY_WITHDRAWAL_LIMIT', default='5.0')
MONTHLY_WITHDRAWAL_LIMIT = env('MONTHLY_WITHDRAWAL_LIMIT', default='100.0')

# Cryptocurrency Settings
CRYPTO_API_TIMEOUT = env.int('CRYPTO_API_TIMEOUT', default=30)
MAX_WITHDRAWALS_PER_HOUR = env.int('MAX_WITHDRAWALS_PER_HOUR', default=5)
MAX_WITHDRAWALS_TO_ADDRESS = env.int('MAX_WITHDRAWALS_TO_ADDRESS', default=3)
MAX_ADDRESS_RISK_SCORE = env.float('MAX_ADDRESS_RISK_SCORE', default=0.7)
MAX_TRANSACTION_AMOUNT = Decimal(env('MAX_TRANSACTION_AMOUNT', default='10000.00'))
BTC_MIN_CONFIRMATIONS = env.int('BTC_MIN_CONFIRMATIONS', default=3)
XMR_MIN_CONFIRMATIONS = env.int('XMR_MIN_CONFIRMATIONS', default=10)

# Currency Exchange Configuration
EXCHANGE_BACKEND = env('EXCHANGE_BACKEND', default='marketplace.utils.exchange_rates.CoinGeckoExchangeBackend')
EXCHANGE_API_KEY = env('EXCHANGE_API_KEY', default='')  # For future paid API support
CURRENCIES_CACHE_TIMEOUT = 900  # 15 minutes

# Currency configuration
OSCAR_DEFAULT_CURRENCY = 'USD'
OSCAR_CURRENCY_FORMAT = {
    'USD': {'currency_digits': False, 'format_type': 'accounting'},
    'EUR': {'currency_digits': False, 'format_type': 'accounting'},
    'GBP': {'currency_digits': False, 'format_type': 'accounting'},
    'JPY': {'currency_digits': False, 'format_type': 'accounting'},
    'CNY': {'currency_digits': False, 'format_type': 'accounting'},
    'AUD': {'currency_digits': False, 'format_type': 'accounting'},
    'CAD': {'currency_digits': False, 'format_type': 'accounting'},
    'CHF': {'currency_digits': False, 'format_type': 'accounting'},
    'NZD': {'currency_digits': False, 'format_type': 'accounting'},
    'SGD': {'currency_digits': False, 'format_type': 'accounting'},
    'INR': {'currency_digits': False, 'format_type': 'accounting'},
    'BRL': {'currency_digits': False, 'format_type': 'accounting'},
    'RUB': {'currency_digits': False, 'format_type': 'accounting'},
    'ZAR': {'currency_digits': False, 'format_type': 'accounting'},
    'MXN': {'currency_digits': False, 'format_type': 'accounting'},
    'ARS': {'currency_digits': False, 'format_type': 'accounting'},
    'SEK': {'currency_digits': False, 'format_type': 'accounting'},
    'NOK': {'currency_digits': False, 'format_type': 'accounting'},
    'DKK': {'currency_digits': False, 'format_type': 'accounting'},
    'PLN': {'currency_digits': False, 'format_type': 'accounting'},
    'THB': {'currency_digits': False, 'format_type': 'accounting'},
    'IDR': {'currency_digits': False, 'format_type': 'accounting'},
    'HKD': {'currency_digits': False, 'format_type': 'accounting'},
    'KRW': {'currency_digits': False, 'format_type': 'accounting'},
}

# Generate currency choices from format settings
OSCAR_CURRENCY_CHOICES = [(k, k) for k in OSCAR_CURRENCY_FORMAT.keys()]
DISPLAY_CURRENCY_ONLY = True  # Only use currency for display
WITHDRAWAL_CONFIRMATION_BLOCKS = env.int('WITHDRAWAL_CONFIRMATION_BLOCKS', default=6)

# Node Configuration
BTC_NODE_URL = env('BTC_NODE_URL', default='http://localhost:8332')
BTC_RPC_USER = env('BTC_RPC_USER', default='btcuser')
BTC_RPC_PASSWORD = env('BTC_RPC_PASSWORD', default='btcpass')

XMR_NODE_URL = env('XMR_NODE_URL', default='http://localhost:18081')
XMR_RPC_PORT = env('XMR_RPC_PORT', default='18081')

# Delivery Tracking Settings
MAPBOX_TOKEN = env('MAPBOX_TOKEN', default=None)
TRACKING_UPDATE_INTERVAL = env.int('TRACKING_UPDATE_INTERVAL', default=30)  # seconds
TRACKING_RATE_LIMIT = env.int('TRACKING_RATE_LIMIT', default=60)  # requests per minute
