# Cloud 9 Marketplace Implementation Guide

## System Architecture

### Framework
The marketplace is built using Django Oscar, a domain-driven e-commerce framework that provides:
- Customizable product catalog with advanced search capabilities
- Secure checkout process with cryptocurrency support
- Extensible vendor dashboard and management
- Comprehensive order tracking and delivery system
- Built-in analytics and reporting
- Multi-platform support (Tor, clearnet, mobile)

### Database Architecture
The system uses multiple databases for optimal performance and scalability:

1. Main Database (PostgreSQL)
   - User accounts and profiles
   - Product listings
   - Basic marketplace data
   - Schema: See `app/models/user.py` and `app/models/product.py`

2. Payment Database (PostgreSQL)
   - Transaction records
   - Cryptocurrency wallets
   - Payment processing
   - Schema: See `app/models/payment.py`

3. Analytics Database (PostgreSQL)
   - System metrics
   - User behavior analytics
   - Performance monitoring

4. Search Database (Elasticsearch)
   - Product search index
   - Location-based queries
   - Advanced filtering
   - Schema: See `app/search/elastic.py`

### Search Functionality
The search system supports:
- Location-based search (areas, cities, countries)
- Product type and category filtering
- Vendor name search
- Delivery method filtering
- Price range filtering
- Geolocation-based sorting
- Real-time indexing

## Authentication System

### User Registration
- Public username (displayed to others)
- Private username (for login)
- Password (hashed with bcrypt)
- Optional PGP key for 2FA
- Welcome phrase (anti-phishing)
- Country selection
- No email requirement

### Vendor Registration
Additional vendor-specific fields:
- Vendor bond requirement
- Accepted cryptocurrencies
- Store customization options

### Tor Access
- Separate endpoints for Tor users
- No client-side JavaScript
- Rate limiting with circuit monitoring
- DDoS protection measures

## Product Management

### Product Listing Fields
1. Basic Information
   - Product name
   - Category
   - Type
   - Description
   - Images

2. Pricing
   - Base price in vendor's preferred fiat
   - Bulk discount options
   - Automatic currency conversion
   - Accepted cryptocurrencies (BTC, XMR, USDT)

3. Measurements
   - Value
   - Unit types:
     * Milliliters (ml)
     * Grams (g)
     * Ounces (oz)
     * Kilos (kg)
     * Parts

4. Delivery Options
   - Instant Delivery
     * Real-time tracking
     * Driver details
     * Delivery radius
     * Custom pricing
   
   - Mail Delivery
     * Shipping options
     * Tracking integration
     * Custom pricing per option
   
   - Pickup/Collection
     * Location management
     * Scheduling
     * Custom pricing

## Frontend Modification (Grub-based)

### Required Changes to Grub
1. Restaurant to Product Conversion
   - Replace restaurant listings with product listings
   - Modify category system for THC/CBD products
   - Update search filters for product-specific attributes

2. Delivery System Adaptation
   - Extend delivery options to include mail and pickup
   - Add cryptocurrency payment methods
   - Implement escrow system for mail delivery

3. User Interface Updates
   - Add vendor profiles and stores
   - Implement product measurement displays
   - Add bulk pricing calculator
   - Display multiple cryptocurrencies

4. Mobile Optimization
   - Responsive design for all features
   - Native Android app considerations
   - Tor-compatible version

## Security Implementation

### Cryptocurrency Integration
- Market-controlled wallets
- One-time deposit addresses
- Multi-currency support (BTC, XMR, USDT)
- Automated balance checks
- Transaction verification

### DDoS Protection
- Rate limiting per circuit
- Custom captcha system
- Request monitoring
- Circuit analysis

### Data Security
- End-to-end encryption
- PGP integration
- Secure messaging system
- Regular security audits

## Deployment Architecture

### Platform Versions
1. Clearnet
   - Full JavaScript functionality
   - Mobile-optimized interface
   - Real-time features

2. Tor Hidden Service
   - No client-side JavaScript
   - Simplified interface
   - Enhanced security measures

3. Android App
   - Native implementation
   - Location services
   - Push notifications

### Infrastructure
- Nginx reverse proxy
- Load balancing
- Circuit monitoring
- Backup systems
- Disaster recovery

## Development Workflow
1. Set up development environment
2. Initialize databases
3. Configure Elasticsearch
4. Implement backend APIs
5. Modify Grub frontend
6. Set up deployment infrastructure
7. Implement security measures
8. Testing and optimization

## Testing Requirements
- Unit tests for all components
- Integration testing
- Security audits
- Performance testing
- Load testing
- User acceptance testing
