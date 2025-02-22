# Cloud9 Marketplace Deployment Guide

## Prerequisites

- Python 3.12+
- PostgreSQL 14+
- Redis 6+
- Cryptocurrency nodes (BTC, XMR, USDT)

## Environment Setup

1. System Dependencies
```bash
# Install system packages
apt-get update
apt-get install -y postgresql postgresql-contrib redis-server nginx supervisor
```

2. Python Environment
```bash
python -m venv /opt/cloud9/venv
source /opt/cloud9/venv/bin/activate
pip install -r requirements.txt
```

3. Database Setup
```bash
# Create production databases
createdb -U postgres cloud9_db
createdb -U postgres cloud9_payment
createdb -U postgres cloud9_analytics
```

## Configuration

1. Environment Variables
```bash
# /opt/cloud9/.env
DEBUG=False
ALLOWED_HOSTS=your-domain.com
SECRET_KEY=your-secret-key

# Database URLs
DATABASE_URL=postgresql://user:pass@localhost:5432/cloud9_db
PAYMENT_DATABASE_URL=postgresql://user:pass@localhost:5433/cloud9_payment
ANALYTICS_DATABASE_URL=postgresql://user:pass@localhost:5434/cloud9_analytics

# Crypto Settings
CRYPTO_WALLET_ENCRYPTION_KEY=your-secure-key
CRYPTO_PAYMENT_SERVER_URL=http://localhost:8001
CRYPTO_PAYMENT_SERVER_API_KEY=your-api-key
```

2. Nginx Configuration
```nginx
# /etc/nginx/sites-available/cloud9
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /opt/cloud9/static/;
    }
    
    location /media/ {
        alias /opt/cloud9/media/;
    }
}
```

3. Supervisor Configuration
```ini
# /etc/supervisor/conf.d/cloud9.conf
[program:cloud9]
command=/opt/cloud9/venv/bin/gunicorn cloud9.wsgi:application
directory=/opt/cloud9
user=cloud9
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/cloud9/gunicorn.log
```

## Deployment Steps

1. Application Setup
```bash
# Create application directory
mkdir -p /opt/cloud9
chown -R cloud9:cloud9 /opt/cloud9

# Clone repository
git clone https://github.com/your-org/cloud9.git /opt/cloud9

# Install dependencies
cd /opt/cloud9
source venv/bin/activate
pip install -r requirements.txt
```

2. Database Migration
```bash
python manage.py migrate
python manage.py collectstatic
```

3. Service Setup
```bash
# Enable services
systemctl enable supervisor
systemctl enable nginx
systemctl enable redis-server

# Start services
systemctl start supervisor
systemctl start nginx
systemctl start redis-server
```

4. Security Setup
```bash
# Configure firewall
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# SSL setup with Let's Encrypt
certbot --nginx -d your-domain.com
```

## Monitoring

1. Log Locations
- Application: /var/log/cloud9/gunicorn.log
- Nginx: /var/log/nginx/access.log, /var/log/nginx/error.log
- Supervisor: /var/log/supervisor/supervisord.log

2. Health Checks
```bash
# Check application status
supervisorctl status cloud9

# Check nginx status
systemctl status nginx

# Check database status
pg_isready -d cloud9_db
```

## Backup Procedures

1. Database Backup
```bash
# Backup script
#!/bin/bash
BACKUP_DIR=/opt/cloud9/backups
DATE=$(date +%Y%m%d)

# Backup databases
pg_dump -Fc cloud9_db > $BACKUP_DIR/cloud9_db_$DATE.dump
pg_dump -Fc cloud9_payment > $BACKUP_DIR/cloud9_payment_$DATE.dump
pg_dump -Fc cloud9_analytics > $BACKUP_DIR/cloud9_analytics_$DATE.dump

# Rotate backups (keep last 7 days)
find $BACKUP_DIR -type f -mtime +7 -delete
```

2. Media Backup
```bash
# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /opt/cloud9/media
```

## Troubleshooting

1. Application Issues
- Check gunicorn logs
- Verify database connections
- Check payment server status

2. Database Issues
- Check PostgreSQL logs
- Verify connection settings
- Monitor disk space

3. Payment Processing
- Check cryptocurrency node status
- Verify wallet encryption
- Monitor transaction logs

## Security Maintenance

1. Regular Updates
```bash
# Update system packages
apt-get update
apt-get upgrade

# Update Python packages
pip install -r requirements.txt --upgrade
```

2. Security Checks
- Monitor system logs
- Check for suspicious activities
- Review access logs

3. SSL Certificate Renewal
```bash
certbot renew
```

## Performance Tuning

1. Database Optimization
```bash
# Analyze database
ANALYZE cloud9_db;

# Vacuum database
VACUUM ANALYZE cloud9_db;
```

2. Cache Configuration
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

3. Static File Serving
- Configure CDN for static files
- Enable gzip compression
- Set proper cache headers
