# PrepEdge AI Backend - Production Deployment Guide

## Overview

This document provides comprehensive instructions for deploying the PrepEdge AI backend in a production environment with:
- PostgreSQL database
- Redis caching layer
- Celery task queues
- Nginx reverse proxy
- Docker containerization

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│    Nginx (80/443) - Load Balancer       │
└──────────┬──────────────────────────────┘
           │
    ┌──────┴──────┬──────────┬──────────┐
    ▼             ▼          ▼          ▼
┌───────┐  ┌───────────┐ ┌──────┐ ┌──────────┐
│FastAPI│  │FastAPI    │ │Redis │ │PostgreSQL│
│API    │  │API(n)     │ │Cache │ │Database  │
└───┬───┘  └───────────┘ └──────┘ └──────────┘
    │
    ├──────────┬──────────┬──────────┐
    ▼          ▼          ▼          ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌──────────┐
│Worker1│ │Worker2│ │Worker3│ │Beat      │
│Celery │ │Celery │ │Celery │ │Scheduler │
└───────┘ └───────┘ └───────┘ └──────────┘
```

## Prerequisites

1. **Server Requirements**
   - OS: Ubuntu 22.04 LTS or similar
   - CPU: 4+ cores
   - RAM: 8GB+ (16GB recommended)
   - Storage: 50GB+
   - Docker & Docker Compose installed

2. **External Services** (optional but recommended)
   - SendGrid or Resend (for email)
   - Razorpay (for payments)
   - NVIDIA NIM API key (for AI models)

## Step 1: Server Preparation

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

## Step 2: Application Setup

```bash
# Clone repository
git clone <your-repo-url> /app/prepedge
cd /app/prepedge/backend

# Create .env file
cp .env.example .env

# Edit configuration
nano .env
```

### Key Configuration Variables

```
ENVIRONMENT=production
DATABASE_URL=postgresql://prepedge:strong_password@db:5432/prepedge
REDIS_URL=redis://:redis_password@redis:6379/0
CELERY_BROKER_URL=redis://:redis_password@redis:6379/1
CELERY_RESULT_BACKEND=redis://:redis_password@redis:6379/2
SECRET_KEY=generate_random_32_char_key_here
OPENAI_API_KEY=your-nvidia-nim-key
FRONTEND_URL=https://yourdomain.com
```

## Step 3: SSL Certificate Setup

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot certonly --standalone -d yourdomain.com

# Copy to container volume
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./ssl/
sudo chown -R $(whoami) ./ssl/
```

## Step 4: Database Migration

```bash
# Create database
createdb -U postgres prepedge

# Run migrations
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# Seed initial data (optional)
docker-compose -f docker-compose.prod.yml exec api python -m app.scripts.seed_data
```

## Step 5: Docker Deployment

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Verify services are running
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f api
```

## Step 6: Health Checks

```bash
# Test API
curl https://yourdomain.com/api/v1/health

# Test deep health check
curl https://yourdomain.com/api/v1/health/deep

# Check Celery workers
docker-compose -f docker-compose.prod.yml exec worker celery -A app.tasks.celery_app inspect active

# Monitor logs
docker-compose -f docker-compose.prod.yml logs -f worker
docker-compose -f docker-compose.prod.yml logs -f beat
```

## Step 7: Monitoring & Logging

### View Logs
```bash
# API logs (structured JSON)
docker-compose -f docker-compose.prod.yml exec api tail -f logs/app.json.log

# Error logs
docker-compose -f docker-compose.prod.yml exec api tail -f logs/error.log

# Celery logs
docker-compose -f docker-compose.prod.yml exec worker tail -f logs/celery.json.log
```

### Monitor Metrics
```bash
# CPU and Memory
docker stats

# Network traffic
docker-compose -f docker-compose.prod.yml exec api curl http://localhost:8000/api/v1/metrics
```

### Database Monitoring
```bash
# Connect to PostgreSQL
docker-compose -f docker-compose.prod.yml exec db psql -U prepedge -d prepedge

# Check connections
SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;

# Check cache hit ratio
SELECT 
  sum(heap_blks_read) as heap_read, 
  sum(heap_blks_hit) as heap_hit, 
  sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;
```

## Scaling & Performance

### Horizontal Scaling (Multiple API Instances)

```yaml
# Update docker-compose.prod.yml
services:
  api:
    deploy:
      replicas: 3  # Run 3 instances
```

### Celery Worker Scaling

```yaml
# Add more workers in docker-compose.prod.yml
  worker2:
    extends: worker
    container_name: prepedge-worker-2
```

### Redis Persistence

```bash
# Enable AOF (Append Only File) for better durability
docker-compose -f docker-compose.prod.yml exec redis redis-cli CONFIG SET appendonly yes
```

### Database Connection Pooling

```python
# In config.py
db_pool_size = 30  # Increase for more connections
db_max_overflow = 60
```

## Security Best Practices

1. **Database Security**
   ```bash
   # Use strong passwords
   # Restrict network access
   docker-compose -f docker-compose.prod.yml down  # Stop before changes
   ```

2. **Redis Security**
   ```bash
   # Enable password authentication (already in setup)
   # Disable dangerous commands
   rdb-compression yes
   maxmemory-policy allkeys-lru
   ```

3. **API Security**
   - Enable HTTPS only
   - Set strong SECRET_KEY
   - Enable rate limiting (already configured with slowapi)
   - Use environment variables for secrets

4. **Backup Strategy**
   ```bash
   # Daily database backup
   docker-compose -f docker-compose.prod.yml exec db pg_dump -U prepedge prepedge > backup_$(date +%Y%m%d).sql
   
   # Automated backup (crontab)
   0 2 * * * cd /app/prepedge/backend && docker-compose -f docker-compose.prod.yml exec db pg_dump -U prepedge prepedge > /backups/backup_$(date +\%Y\%m\%d).sql
   ```

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose logs db

# Test connection
docker-compose exec db psql -U prepedge -c "SELECT version();"
```

### Redis Connection Issues
```bash
# Check Redis logs
docker-compose logs redis

# Test connection
docker-compose exec redis redis-cli ping
```

### Celery Task Issues
```bash
# Check active tasks
docker-compose exec worker celery -A app.tasks.celery_app inspect active

# Check registered tasks
docker-compose exec worker celery -A app.tasks.celery_app inspect registered

# Monitor queue
docker-compose exec redis redis-cli LLEN celery
```

### Out of Memory Issues
```bash
# Set Redis max memory policy
docker-compose exec redis redis-cli CONFIG SET maxmemory 2gb

# Monitor memory usage
docker-compose exec api free -h
```

## Updating & Rollback

```bash
# Pull latest code
git pull origin main

# Stop services
docker-compose -f docker-compose.prod.yml down

# Rebuild images
docker-compose -f docker-compose.prod.yml build

# Run migrations if needed
docker-compose -f docker-compose.prod.yml up -d db
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Rollback if needed
git checkout <previous-commit>
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

## Performance Optimization

1. **Enable Query Caching**
   ```python
   # Use CachedQueries for frequently accessed data
   from app.cache.cached_queries import CachedQueries
   companies = await CachedQueries.get_trending_companies(session)
   ```

2. **Batch Database Operations**
   ```python
   # Use bulk_insert_mappings for large inserts
   session.bulk_insert_mappings(Model, data_list)
   ```

3. **Compress API Responses**
   ```python
   # Already enabled via FastAPI middleware
   ```

4. **Monitor Slow Queries**
   ```sql
   -- Enable slow query log
   ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1s
   SELECT pg_reload_conf();
   ```

## Monitoring with Third-Party Services

### DataDog Integration
```python
# Add to requirements.txt
datadog>=0.47.0

# In main.py
from datadog import initialize, api
initialize({"api_key": DATADOG_API_KEY})
```

### Sentry Integration
```python
# Error tracking
pip install sentry-sdk

# In main.py
import sentry_sdk
sentry_sdk.init("your-sentry-dsn")
```

## Support & Maintenance

- Regular security updates: `apt-get update && apt-get upgrade`
- Database maintenance: Run VACUUM ANALYZE weekly
- Log rotation: Configured via logging_config.py
- Backup verification: Monthly restore tests

## Production Checklist

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database backups configured
- [ ] Monitoring and alerts set up
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Logging aggregation enabled
- [ ] Metrics collection active
- [ ] Security headers configured
- [ ] Health checks passing
- [ ] Load testing completed
- [ ] Documentation updated

---

For more information, see the main README.md and individual module documentation.
