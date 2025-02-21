# Cloud 9 Marketplace

A comprehensive THC/CBD marketplace platform built with Django Oscar, supporting Tor, clearnet, and mobile platforms.

## Features
- Multi-platform support (Tor, clearnet, Android app)
- Cryptocurrency payments (BTC, XMR, USDT) with full node integration
- Multiple delivery methods (instant, mail, pickup)
- Advanced search functionality with Elasticsearch
- Vendor management system with bond requirements
- Secure authentication with PGP support
- Market-controlled cryptocurrency wallets
- Secure withdrawal system with multi-level validation

## Backend Setup
1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Configure environment:
```bash
# Copy example configuration
cp .env.example .env

# Configure environment variables following security guidelines
# See docs/SECURITY_GUIDE.md for secure configuration practices
# Important: Never commit credentials or secrets to version control
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## Security Note
Ensure all credentials and sensitive configuration values are properly secured and never committed to version control. See the [Security Guide](docs/SECURITY_GUIDE.md) for best practices.

## Documentation
- [Implementation Guide](IMPLEMENTATION_GUIDE.md)
- [Infrastructure Guide](docs/INFRASTRUCTURE_GUIDE.md)
- [Payment Implementation](docs/PAYMENT_IMPLEMENTATION_GUIDE.md)
- [Authentication Guide](docs/AUTH_IMPLEMENTATION_GUIDE.md)
- [Database Setup](docs/DATABASE_SETUP_GUIDE.md)
