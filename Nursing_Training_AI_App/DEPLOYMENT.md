# 🚀 Nursing Training AI - Production Deployment Guide

Complete guide for deploying the Nursing Training AI platform to production.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Database Setup](#database-setup)
6. [Stripe Configuration](#stripe-configuration)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Disaster Recovery](#backup--disaster-recovery)
9. [Performance Optimization](#performance-optimization)
10. [Security Checklist](#security-checklist)

## Prerequisites

### System Requirements
- **Server**: Ubuntu 20.04+ or similar Linux distribution
- **RAM**: Minimum 4GB (8GB recommended for production)
- **Storage**: Minimum 50GB SSD
- **CPU**: 2+ cores

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git
- Node.js 18+ (for mobile build)
- Python 3.10+

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/Ginx172/Nursing-Training-AI.git
cd Nursing-Training-AI
```

### 2. Environment Variables

Create `.env` file in `Nursing_Training_AI_App/backend/`:

```bash
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/nursing_ai
POSTGRES_USER=nursing_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=nursing_training_ai

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# JWT & Security
SECRET_KEY=your_secret_key_here_minimum_32_characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Email (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=noreply@nursingtrainingai.com

# AI Services (Optional)
OPENAI_API_KEY=your_openai_key

# Sentry (Error Tracking)
SENTRY_DSN=your_sentry_dsn

# Application
DEBUG=False
CORS_ORIGINS=https://yourdomai.com,https://app.yourdomain.com
```

## Docker Deployment

### 1. Build Images

```bash
cd Nursing_Training_AI_App
docker-compose build
```

### 2. Start Services

```bash
docker-compose up -d
```

### 3. Check Status

```bash
docker-compose ps
docker-compose logs -f backend
```

### 4. Initialize Database

```bash
docker-compose exec backend python scripts/init_db.py
```

## Cloud Deployment

### AWS Deployment

#### Using ECS (Elastic Container Service)

```bash
# Install AWS CLI
aws configure

# Create ECR repositories
aws ecr create-repository --repository-name nursing-ai-backend
aws ecr create-repository --repository-name nursing-ai-frontend

# Build and push images
docker build -t nursing-ai-backend ./backend
docker tag nursing-ai-backend:latest your-account.dkr.ecr.region.amazonaws.com/nursing-ai-backend:latest
docker push your-account.dkr.ecr.region.amazonaws.com/nursing-ai-backend:latest
```

#### Using EC2

```bash
# SSH into EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone and run
git clone https://github.com/Ginx172/Nursing-Training-AI.git
cd Nursing-Training-AI/Nursing_Training_AI_App
docker-compose up -d
```

### Azure Deployment

```bash
# Login to Azure
az login

# Create Resource Group
az group create --name NursingAI --location ukwest

# Create Container Registry
az acr create --resource-group NursingAI --name nursingairegistry --sku Basic

# Deploy to App Service
az webapp create --resource-group NursingAI --plan AppServicePlan --name nursing-ai-app
```

### Google Cloud Platform

```bash
# Setup GCP
gcloud init

# Create GKE Cluster
gcloud container clusters create nursing-ai-cluster --num-nodes=3

# Deploy
kubectl apply -f k8s/deployment.yaml
```

## Database Setup

### PostgreSQL Initialization

```sql
-- Connect to database
psql -h localhost -U nursing_user -d nursing_training_ai

-- Create tables (run init.sql)
\i database/schemas/init.sql

-- Verify tables
\dt
```

### Database Migrations

```bash
cd Nursing_Training_AI_App/backend

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### Database Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U nursing_user nursing_training_ai > backup.sql

# Restore
docker-compose exec -T postgres psql -U nursing_user nursing_training_ai < backup.sql
```

## Stripe Configuration

### 1. Create Products in Stripe Dashboard

1. Go to https://dashboard.stripe.com/products
2. Create products for each plan:
   - Basic (Monthly & Annual)
   - Professional (Monthly & Annual)
   - Enterprise (Monthly & Annual)
3. Copy Price IDs to `stripe_config.py`

### 2. Configure Webhooks

1. Go to https://dashboard.stripe.com/webhooks
2. Add endpoint: `https://yourdomain.com/api/payments/webhooks/stripe`
3. Select events:
   - `customer.subscription.*`
   - `invoice.payment_*`
4. Copy Webhook Secret to `.env`

### 3. Test Mode vs Live Mode

Development:
```bash
STRIPE_SECRET_KEY=sk_test_...
```

Production:
```bash
STRIPE_SECRET_KEY=sk_live_...
```

## Monitoring & Logging

### Sentry Setup

```bash
# Install Sentry SDK (already in requirements.txt)
pip install sentry-sdk[fastapi]
```

Add to `main.py`:
```python
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=1.0
)
```

### Log Files

Logs are stored in:
- Backend: `Nursing_Training_AI_App/backend/logs/`
- Nginx: `/var/log/nginx/`

View logs:
```bash
docker-compose logs -f backend
tail -f Nursing_Training_AI_App/backend/logs/app.log
```

## Backup & Disaster Recovery

### Automated Backups

Create cron job:
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/backup_script.sh
```

### Backup Script

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U nursing_user nursing_training_ai > backups/db_$DATE.sql
tar -czf backups/files_$DATE.tar.gz Nursing_Training_AI_App/
```

## Performance Optimization

### 1. Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_questions_specialty ON questions(specialty, band);
CREATE INDEX idx_user_progress_user_id ON user_progress(user_id);

-- Analyze and vacuum
ANALYZE;
VACUUM;
```

### 2. Redis Caching

Configure cache TTLs in `core/cache.py`:
- User data: 1 hour
- Questions: 24 hours
- Analytics: 5 minutes

### 3. CDN Configuration

Use CloudFlare or AWS CloudFront for:
- Static assets
- Mobile app bundles
- Images and media

### 4. Database Connection Pooling

In `config/database.py`:
```python
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 40
```

## Security Checklist

### ✅ Required Before Production

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY (32+ characters)
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up firewall rules
- [ ] Use environment variables (never commit secrets)
- [ ] Enable database encryption
- [ ] Configure backup encryption
- [ ] Set up monitoring and alerting
- [ ] Enable audit logging
- [ ] Configure Stripe webhook signature verification
- [ ] Set DEBUG=False in production
- [ ] Enable HSTS headers
- [ ] Configure CSP headers
- [ ] Enable SQL injection protection
- [ ] Set up DDoS protection
- [ ] Regular security updates
- [ ] Implement rate limiting per user

### SSL Certificate Setup

Using Let's Encrypt:
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (cron)
0 0 1 * * certbot renew --quiet
```

## Health Checks

### API Health Check

```bash
curl https://yourdomain.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-18T12:00:00",
  "components": {
    "api": {"status": "healthy"},
    "database": {"status": "healthy"},
    "cache": {"status": "healthy"}
  }
}
```

### Monitoring Endpoints

- Health: `/api/health`
- Metrics: `/api/admin/platform/realtime`
- System: `/api/admin/config`

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
services:
  backend:
    deploy:
      replicas: 3
  
  nginx:
    # Load balancer configuration
```

### Database Read Replicas

Configure PostgreSQL replication for read-heavy workloads.

## Troubleshooting

### Common Issues

**Issue**: Database connection failed
```bash
# Check if postgres is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart service
docker-compose restart postgres
```

**Issue**: High memory usage
```bash
# Check container stats
docker stats

# Increase limits in docker-compose.yml
```

**Issue**: Slow API responses
```bash
# Check Redis cache
docker-compose exec redis redis-cli INFO stats

# Check database queries
docker-compose exec postgres psql -U nursing_user -c "SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

## Maintenance

### Regular Maintenance Tasks

**Daily**:
- Monitor error logs
- Check backup completion
- Review system metrics

**Weekly**:
- Database vacuum and analyze
- Review slow queries
- Check disk space

**Monthly**:
- Security updates
- Performance review
- Cost optimization review

## Support & Contact

For deployment support:
- Email: devops@nursingtrainingai.com
- Documentation: https://docs.nursingtrainingai.com

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Status**: Production Ready ✅

