# Deployment Guide

This guide covers various deployment options for the Spam Detector application, from development setup to production deployment.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Development Deployment](#development-deployment)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Environment Configuration](#environment-configuration)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **npm**: 7 or higher
- **Git**: Latest version
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux

### Hardware Requirements
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Storage | 1 GB | 5+ GB |
| Network | 10 Mbps | 100+ Mbps |

## Development Deployment

### Quick Start (Windows)
```powershell
# Clone the repository
git clone https://github.com/NSharp-mahajan/Spam-detector.git
cd Spam-detector

# Set up Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Environment is pre-configured with .env file

# Start backend server
python Spam-backend/app.py
# Backend runs on http://localhost:5000

# In a new terminal, start frontend
cd frontend-react
npm install
npm start
# Frontend runs on http://localhost:3000
```

### Detailed Development Setup

#### Backend Setup
1. **Virtual Environment**: Creates isolated Python environment
2. **Dependencies**: Installs Flask, scikit-learn, pandas, and other requirements
3. **Environment**: Uses `.env` file for configuration
4. **Database**: SQLite database created automatically (emails.db)
5. **Model**: ML model trained on startup from training_data.csv

#### Frontend Setup  
1. **Node Dependencies**: Installs React 18, TypeScript, and testing libraries
2. **Development Server**: Webpack dev server with hot reload
3. **Type Checking**: TypeScript compilation with strict checking
4. **Testing**: Jest + React Testing Library configured
cd Spam-backend
python app.py

# Start frontend (React)
cd frontend-react
npm install
npm start
```

### Development Environment Variables
Create a `.env` file in the project root:
```bash
# Development Configuration
FLASK_ENV=development
DEBUG=true
HOST=127.0.0.1
PORT=5000

# Database
DATABASE_URL=emails.db

# Model Configuration
MODEL_PATH=spam_model.joblib
DEFAULT_THRESHOLD=0.6
TRAINING_DATA_CSV=Spam-backend/training_data.csv

# Logging
LOG_LEVEL=DEBUG
```

### Development Workflow
1. **Backend Development**:
   - Flask runs in debug mode with auto-reload
   - SQLite database for local development
   - Detailed logging enabled

2. **Frontend Development**:
   - React dev server with hot reload
   - Proxy configuration for API calls
   - Browser dev tools enabled

## Production Deployment

### Server Requirements
- **OS**: Ubuntu 20.04 LTS or similar
- **Python**: 3.9+
- **Web Server**: nginx
- **Process Manager**: systemd or supervisor
- **Database**: PostgreSQL (recommended) or optimized SQLite

### Step-by-Step Production Setup

#### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3 python3-pip python3-venv nginx supervisor postgresql postgresql-contrib -y

# Create application user
sudo useradd -m -s /bin/bash spamdetector
sudo usermod -aG www-data spamdetector
```

#### 2. Application Deployment
```bash
# Switch to application user
sudo su - spamdetector

# Clone repository
git clone https://github.com/your-username/Spam-detector.git
cd Spam-detector

# Set up Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install production WSGI server
pip install gunicorn
```

#### 3. Database Setup (PostgreSQL)
```bash
# Switch to postgres user
sudo su - postgres

# Create database and user
psql -c "CREATE DATABASE spamdetector;"
psql -c "CREATE USER spamdetector WITH PASSWORD 'your_secure_password';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE spamdetector TO spamdetector;"
```

#### 4. Environment Configuration
Create `/home/spamdetector/Spam-detector/.env`:
```bash
# Production Configuration
FLASK_ENV=production
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://spamdetector:your_secure_password@localhost/spamdetector

# Security
SECRET_KEY=your_very_secret_key_here

# Model Configuration
MODEL_PATH=/home/spamdetector/Spam-detector/spam_model.joblib
DEFAULT_THRESHOLD=0.6
TRAINING_DATA_CSV=/home/spamdetector/Spam-detector/Spam-backend/training_data.csv

# Logging
LOG_LEVEL=INFO
LOG_FILE=/home/spamdetector/logs/app.log
```

#### 5. Build Frontend
```bash
# Build React production bundle
cd frontend-react
npm ci --production
npm run build

# Move build files to nginx directory
sudo cp -r build/* /var/www/html/spam-detector/
sudo chown -R www-data:www-data /var/www/html/spam-detector/
```

#### 6. Gunicorn Configuration
Create `/home/spamdetector/Spam-detector/gunicorn.conf.py`:
```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
chdir = "/home/spamdetector/Spam-detector"
```

#### 7. Systemd Service Configuration
Create `/etc/systemd/system/spam-detector.service`:
```ini
[Unit]
Description=Spam Detector Gunicorn Application
After=network.target

[Service]
User=spamdetector
Group=www-data
WorkingDirectory=/home/spamdetector/Spam-detector
Environment="PATH=/home/spamdetector/Spam-detector/.venv/bin"
ExecStart=/home/spamdetector/Spam-detector/.venv/bin/gunicorn -c gunicorn.conf.py Spam-backend.app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### 8. Nginx Configuration
Create `/etc/nginx/sites-available/spam-detector`:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Frontend static files
    location / {
        root /var/www/html/spam-detector;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, no-transform";
        }
    }
    
    # API proxy to backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
        proxy_connect_timeout 10s;
    }
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy strict-origin-when-cross-origin;
}
```

#### 9. Enable and Start Services
```bash
# Enable nginx site
sudo ln -s /etc/nginx/sites-available/spam-detector /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl reload nginx

# Start application service
sudo systemctl daemon-reload
sudo systemctl enable spam-detector
sudo systemctl start spam-detector

# Check status
sudo systemctl status spam-detector
```

#### 10. SSL Configuration (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Docker Deployment

### Dockerfile (Backend)
Create `Dockerfile` in the project root:
```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/stats || exit 1

# Start command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "Spam-backend.app:app"]
```

### Docker Compose Configuration
Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://spam:password@db:5432/spamdetector
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - spam-network

  frontend:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./frontend-react/build:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - spam-network

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=spamdetector
      - POSTGRES_USER=spam
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - spam-network

  redis:
    image: redis:alpine
    restart: unless-stopped
    networks:
      - spam-network

volumes:
  postgres_data:

networks:
  spam-network:
    driver: bridge
```

### Build and Deploy
```bash
# Build and start services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Scale backend
docker-compose up -d --scale backend=3
```

## Cloud Deployment

### AWS Deployment (EC2 + RDS)

#### 1. Create EC2 Instance
```bash
# Launch Ubuntu 20.04 instance
# Instance type: t3.medium or larger
# Security group: Allow ports 22, 80, 443
```

#### 2. Set up RDS PostgreSQL
```bash
# Create RDS instance
# Engine: PostgreSQL 13
# Instance class: db.t3.micro or larger
# Storage: 20 GB GP2
```

#### 3. Deploy Application
Follow the production deployment steps, using RDS connection string:
```bash
DATABASE_URL=postgresql://username:password@rds-endpoint:5432/spamdetector
```

### Heroku Deployment

#### 1. Prepare for Heroku
Create `Procfile`:
```
web: gunicorn -c gunicorn.conf.py Spam-backend.app:app
release: python Spam-backend/migrate.py
```

Create `runtime.txt`:
```
python-3.9.19
```

#### 2. Deploy to Heroku
```bash
# Install Heroku CLI and login
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set DEBUG=false

# Deploy
git push heroku main

# Run database migrations
heroku run python Spam-backend/migrate.py
```

### Azure Deployment (App Service)

#### 1. Create App Service
```bash
# Install Azure CLI
az webapp create --name spam-detector --resource-group myResourceGroup --plan myAppServicePlan --runtime "PYTHON|3.9"
```

#### 2. Configure Application
```bash
# Set environment variables
az webapp config appsettings set --name spam-detector --resource-group myResourceGroup --settings FLASK_ENV=production DEBUG=false

# Deploy code
az webapp deployment source config-zip --name spam-detector --resource-group myResourceGroup --src spam-detector.zip
```

## Environment Configuration

### Environment Variables Reference
```bash
# Application Settings
FLASK_ENV=production|development
DEBUG=true|false
HOST=0.0.0.0
PORT=5000

# Database
DATABASE_URL=sqlite:///emails.db|postgresql://user:pass@host:port/db

# Security
SECRET_KEY=your-secret-key
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Model Configuration
MODEL_PATH=spam_model.joblib
DEFAULT_THRESHOLD=0.6
TRAINING_DATA_CSV=training_data.csv

# Logging
LOG_LEVEL=INFO|DEBUG|WARNING|ERROR
LOG_FILE=/path/to/logfile.log

# Performance
WORKERS=4
MAX_REQUESTS=1000
TIMEOUT=30

# Features
ENABLE_RETRAINING=true|false
ENABLE_HISTORY=true|false
CACHE_TTL=300
```

### Security Configuration
```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Set secure file permissions
chmod 600 .env
chmod 700 logs/

# Disable debug mode in production
DEBUG=false
FLASK_ENV=production
```

## Monitoring and Maintenance

### Health Checks
```bash
# Backend health check
curl http://localhost:5000/stats

# Database connection check
python -c "import sqlite3; sqlite3.connect('emails.db').execute('SELECT 1')"

# Log analysis
tail -f logs/app.log | grep ERROR
```

### Backup Strategy
```bash
# Database backup
pg_dump spamdetector > backup_$(date +%Y%m%d_%H%M%S).sql

# Model backup
cp spam_model.joblib backups/spam_model_$(date +%Y%m%d_%H%M%S).joblib

# Configuration backup
tar -czf config_backup_$(date +%Y%m%d_%H%M%S).tar.gz .env nginx.conf
```

### Log Rotation
Create `/etc/logrotate.d/spam-detector`:
```
/home/spamdetector/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 spamdetector spamdetector
    postrotate
        systemctl reload spam-detector
    endscript
}
```

### Monitoring Setup
```bash
# Install monitoring tools
pip install prometheus-client

# Add metrics endpoint to Flask app
from prometheus_client import Counter, Histogram, generate_latest

# Set up alerts
# - High error rate
# - Slow response times
# - Database connection issues
# - Disk space usage
```

### Update Procedure
```bash
# 1. Backup current version
git tag -a v$(date +%Y%m%d) -m "Pre-update backup"

# 2. Pull latest changes
git pull origin main

# 3. Update dependencies
pip install -r requirements.txt

# 4. Test in staging
./scripts/test.sh

# 5. Restart services
sudo systemctl restart spam-detector
sudo systemctl reload nginx

# 6. Verify deployment
curl -f http://localhost/api/stats
```

This deployment guide provides comprehensive instructions for various deployment scenarios. Choose the approach that best fits your infrastructure requirements and technical expertise.
