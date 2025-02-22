# Cloud9 Marketplace Backend

A comprehensive THC/CBD marketplace platform built with Django Oscar, supporting multiple platforms (Tor, clearnet, mobile) with advanced security features and cryptocurrency integration.

## Features

- Multi-platform support (Tor, clearnet, mobile)
- Cryptocurrency payments (BTC, XMR, USDT)
- Advanced vendor management with bond system
- Comprehensive product management
- Secure payment processing with separate payment server
- Real-time delivery tracking
- Private listings support

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Setup databases:
```bash
# Create PostgreSQL databases
createdb cloud9_db
createdb cloud9_payment
createdb cloud9_analytics

# Run migrations
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run development server:
```bash
python manage.py runserver
```

## Development

### Database Configuration

The project uses three PostgreSQL databases:
- Main database: Product listings, users, orders
- Payment database: Cryptocurrency transactions
- Analytics database: Usage statistics and metrics

Configure database URLs in `.env`:
```
DATABASE_URL=postgresql://user:pass@localhost:5432/cloud9_db
PAYMENT_DATABASE_URL=postgresql://user:pass@localhost:5433/cloud9_payment
ANALYTICS_DATABASE_URL=postgresql://user:pass@localhost:5434/cloud9_analytics
```

### Payment Server

The payment server runs separately for enhanced security:
```
CRYPTO_WALLET_ENCRYPTION_KEY=your_secure_key
CRYPTO_PAYMENT_SERVER_URL=http://localhost:8001
CRYPTO_PAYMENT_SERVER_API_KEY=your_api_key
```

### Testing

Run tests with:
```bash
python manage.py test
```

## Security Features

- Separate payment server for fund handling
- Full node integration for transaction verification
- Automated and manual account freezing
- PIN authentication for sensitive operations
- PGP key integration for 2FA
- Private listing support
- Soft deletion with order preservation

## License

Proprietary - All rights reserved
