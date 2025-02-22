# Cloud9 Marketplace Implementation Guide

## Architecture Overview

The Cloud9 marketplace is built using Django Oscar, providing a robust e-commerce foundation with customized models for THC/CBD product management, vendor operations, and cryptocurrency payments.

### Core Components

1. Product Management
   - Custom ProductListing model extending Oscar's AbstractProduct
   - Vendor-specific product attributes
   - Multiple postage options per listing
   - Private listing support

2. Vendor System
   - Bond requirement (€500) or admin waiver
   - Finalize Early (FE) permissions
   - Automated and manual status controls

3. Order Processing
   - Minimum 7-day timeframe for mail/pickup
   - Maximum 24-hour timeframe for instant delivery
   - Real-time tracking support
   - Dispute handling

4. Payment System
   - Multi-cryptocurrency support (BTC, XMR, USDT)
   - Separate payment server
   - Full node integration
   - Automated security checks

## Development Setup

1. Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

2. Database Configuration
```bash
# Create databases
createdb cloud9_db
createdb cloud9_payment
createdb cloud9_analytics

# Configure .env
cp .env.example .env
# Edit database URLs in .env
```

3. Django Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## Model Structure

### Product Models
```python
# marketplace/models/product.py
class ProductListing(AbstractProduct):
    vendor = models.ForeignKey(VendorProfile)
    cancel_hours = models.IntegerField()
    auto_cancel_hours = models.IntegerField()
    auto_finalize_days = models.IntegerField()
    ships_to = models.CharField()
    postage_options = models.ManyToManyField(PostageOption)
```

### Vendor Models
```python
# marketplace/models/vendor.py
class VendorProfile(AbstractPartner):
    bond_paid = models.BooleanField()
    bond_waived = models.BooleanField()
    rating = models.DecimalField()
```

### Payment Models
```python
# crypto_payments/models.py
class UserWallet(models.Model):
    btc_balance = models.DecimalField()
    xmr_balance = models.DecimalField()
    usdt_balance = models.DecimalField()
```

## Security Implementation

1. Payment Server
   - Separate server for handling funds
   - Encrypted wallet storage
   - Transaction verification through full nodes

2. User Authentication
   - Dual username system (public/private)
   - Optional PGP key integration
   - PIN requirements for financial operations

3. Vendor Security
   - Bond system with admin override
   - Automated status monitoring
   - Manual admin controls

## Testing

Run the test suite:
```bash
python manage.py test
```

### Key Test Areas
1. Product Management
2. Vendor Operations
3. Order Processing
4. Payment Handling
5. Security Features

## Deployment

1. Environment Configuration
```bash
# Production settings
DEBUG=False
ALLOWED_HOSTS=your-domain.com
```

2. Database Setup
```bash
# Configure production databases
DATABASE_URL=postgresql://user:pass@prod-db:5432/cloud9_db
PAYMENT_DATABASE_URL=postgresql://user:pass@prod-db:5433/cloud9_payment
ANALYTICS_DATABASE_URL=postgresql://user:pass@prod-db:5434/cloud9_analytics
```

3. Static Files
```bash
python manage.py collectstatic
```

4. Security Settings
```bash
# Configure security settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Maintenance

1. Database Backups
```bash
pg_dump -Fc cloud9_db > backup.dump
```

2. System Updates
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
```

3. Security Updates
- Regular dependency updates
- Security patch application
- System monitoring

## Troubleshooting

Common issues and solutions:

1. Database Connections
   - Check connection strings
   - Verify database existence
   - Check permissions

2. Payment Processing
   - Verify node connections
   - Check wallet encryption
   - Monitor transaction logs

3. Vendor Issues
   - Verify bond payment
   - Check FE permissions
   - Review status changes

## Support

For technical support:
1. Check logs in /var/log/cloud9/
2. Review database status
3. Check payment server connectivity
4. Verify cryptocurrency node status
