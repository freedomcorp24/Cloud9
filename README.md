# Cloud 9 Marketplace

A comprehensive THC/CBD marketplace platform supporting Tor, clearnet, and mobile platforms.

## Features
- Multi-platform support (Tor, clearnet, Android app)
- Cryptocurrency payments (BTC, XMR, USDT)
- Multiple delivery methods (instant, mail, pickup)
- Advanced search functionality
- Vendor management system
- Secure authentication with PGP support

## Backend Setup
1. Install dependencies:
```bash
cd backend
poetry install
```

2. Set up environment variables in `.env`:
```
MAIN_DATABASE_URL=postgresql+asyncpg://user:pass@localhost/cloud9_main
PAYMENT_DATABASE_URL=postgresql+asyncpg://user:pass@localhost/cloud9_payments
ANALYTICS_DATABASE_URL=postgresql+asyncpg://user:pass@localhost/cloud9_analytics
ELASTICSEARCH_URL=http://localhost:9200
SECRET_KEY=your-secret-key
```

3. Run the development server:
```bash
poetry run fastapi dev app/main.py
```
