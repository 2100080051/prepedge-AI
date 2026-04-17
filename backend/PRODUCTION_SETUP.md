# PrepEdge AI Backend - Production Ready Setup

## 📋 Overview

This is a production-ready FastAPI backend for PrepEdge AI with enterprise-grade features:

- **Caching**: Redis-based caching layer for hot data
- **Task Queues**: Celery for background jobs and async processing
- **Database**: PostgreSQL with connection pooling and migrations
- **Monitoring**: Comprehensive logging and metrics collection
- **Security**: SSL/TLS, rate limiting, security headers
- **Deployment**: Docker containerization with docker-compose
- **Load Balancing**: Nginx reverse proxy with health checks
- **High Availability**: Multi-instance deployment support

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- 4+ CPU cores
- 8+ GB RAM
- 50+ GB storage

### 5-Minute Setup

```bash
# 1. Clone and setup
cd backend

# 2. Configure environment
cp .env.example .env
nano .env  # Edit with your settings

# 3. Deploy
chmod +x deploy.sh
./deploy.sh full-deploy

# 4. Verify
curl http://localhost:8000/api/v1/health
```

## 📦 Architecture

```
Client → Nginx (Port 443)
         ↓
    [Load Balancer]
    ↙    ↓    ↘
API-1  API-2  API-3  (FastAPI instances)
    ↘     ↓    ↙
    [PostgreSQL Database]
    
[Redis Cache] ← API instances
[Redis Queue] ← Celery Workers
              ← Celery Beat (Task Scheduler)
```

## 🔧 Key Components

### 1. **Caching System** (`app/cache/`)
- **RedisCache**: Distributed cache with TTL support
- **CachedQueries**: Database queries with automatic caching
- **Decorators**: `@cached` for easy function result caching

```python
from app.cache.cached_queries import CachedQueries

# Automatically cached with 1-hour TTL
companies = await CachedQueries.get_trending_companies(session)
```

### 2. **Task Queue** (`app/tasks/`)
- **Celery Workers**: Process background jobs
- **Periodic Tasks**: Scheduled via Celery Beat
- **Task Examples**: 
  - Email sending
  - Job indexing
  - ML recommendations
  - Stats computation

```python
from app.tasks.jobs import send_email_notification

# Queue async email
send_email_notification.delay(user_id=1, template="welcome")
```

### 3. **Database** (`app/models/`, `app/database.py`)
- PostgreSQL with SQLAlchemy ORM
- Async query support
- Migration system (Alembic)
- Connection pooling

### 4. **Monitoring** (`app/monitoring/`, `app/logging_config.py`)
- Structured JSON logging
- Metrics collection
- Performance tracking
- Error aggregation

### 5. **Security** (`nginx.conf`)
- SSL/TLS encryption
- Rate limiting
- CORS protection
- Security headers
- Request validation

## 📊 Service Deployment

### Using Docker Compose

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f api

# Check status
docker-compose -f docker-compose.prod.yml ps

# Run migrations
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
```

### Using Deploy Script

```bash
./deploy.sh start          # Start services
./deploy.sh stop           # Stop services
./deploy.sh restart        # Restart services
./deploy.sh logs api       # View API logs
./deploy.sh migrate        # Run migrations
./deploy.sh backup         # Backup database
./deploy.sh restore file   # Restore from backup
./deploy.sh health         # Check health
./deploy.sh stats          # System stats
```

## 🔄 Data Flow Examples

### Example 1: Getting Trending Companies (with caching)

```
Request → API → Check Redis Cache
                 ↓ Cache Hit
                 Return cached data (instant)
                 
                 ↓ Cache Miss
                 Query PostgreSQL
                 Cache result in Redis
                 Return data
```

### Example 2: Sending Email (with Celery)

```
Request → API → Queue task in Redis
         ↓ (Returns immediately)
         
Celery Worker → Fetch task from queue
               → Get user data
               → Render email template
               → Send via SendGrid
               → Update task status
```

### Example 3: Scheduled Recommendation Generation

```
Celery Beat (3 AM daily) → Queue recommendation task
                        ↓
Celery Workers → Get user preferences
              → Run ML model
              → Cache recommendations in Redis
              → Update PostgreSQL
```

## 📈 Performance Optimization

### Caching Strategy
- **Hot Data TTL**: 1 hour (trending companies, recommendations)
- **Warm Data TTL**: 2 hours (company stats)
- **Cool Data TTL**: Query-time (detailed company info)

### Database Optimization
- Connection pooling: 20 base + 40 overflow
- Query timeouts: 60 seconds for reads, 30 seconds for writes
- Periodic VACUUM ANALYZE

### Redis Configuration
- Max memory: 2GB (with LRU eviction)
- Persistence: AOF enabled for durability
- 3 databases: 0=cache, 1=queue broker, 2=results

## 🛡️ Security Features

✅ **SSL/TLS Encryption** - All traffic encrypted
✅ **Rate Limiting** - 100 req/s for API, 10 req/min for auth
✅ **CORS Protection** - Whitelist allowed origins
✅ **Security Headers** - HSTS, CSP, X-Frame-Options
✅ **Request Validation** - Pydantic schema validation
✅ **Password Hashing** - Bcrypt with salt
✅ **JWT Tokens** - Expiring access tokens
✅ **SQL Injection Protection** - Parameterized queries
✅ **CSRF Protection** - Token-based validation

## 📝 Configuration

### Environment Variables

```env
# Core
ENVIRONMENT=production
DEBUG=false

# Database
DATABASE_URL=postgresql://user:pass@localhost/prepedge

# Caching
REDIS_URL=redis://:password@localhost:6379/0

# Task Queue
CELERY_BROKER_URL=redis://:password@localhost:6379/1
CELERY_RESULT_BACKEND=redis://:password@localhost:6379/2

# API
FRONTEND_URL=https://yourdomain.com
SECRET_KEY=<32+ char random string>

# Services
OPENAI_API_KEY=<nvidia-nim-key>
SENDGRID_API_KEY=<key>
RAZORPAY_KEY_ID=<id>
RAZORPAY_KEY_SECRET=<secret>
```

See `.env.example` for complete list.

## 🩺 Health Checks

### API Health
```bash
# Basic health
curl http://localhost:8000/api/v1/health

# Deep health (all services)
curl http://localhost:8000/api/v1/health/deep

# Kubernetes readiness
curl http://localhost:8000/api/v1/health/ready

# Kubernetes liveness
curl http://localhost:8000/api/v1/health/live
```

### Database Health
```bash
docker-compose exec db psql -U prepedge -c "SELECT COUNT(*) FROM users;"
```

### Redis Health
```bash
docker-compose exec redis redis-cli INFO server
```

### Celery Health
```bash
docker-compose exec worker celery -A app.tasks.celery_app inspect active
```

## 📊 Monitoring & Logging

### Log Files
```
logs/
├── app.log              # Application logs
├── app.json.log         # Structured JSON logs
├── error.log            # Errors only
└── celery.json.log      # Task queue logs
```

### View Logs
```bash
# API logs
docker-compose logs -f api

# Worker logs
docker-compose logs -f worker

# All services
docker-compose logs -f

# Specific pod line
tail -f logs/app.json.log | jq .
```

### Metrics
```bash
# Get metrics summary
curl http://localhost:8000/api/v1/metrics

# Response includes:
# - Request counts
# - Database query stats
# - Cache hit rates
# - Task execution times
```

## 🔄 Scaling

### Horizontal Scaling (Multiple API Instances)

Update `docker-compose.prod.yml`:
```yaml
services:
  api:
    deploy:
      replicas: 5  # Run 5 instances
```

### Vertical Scaling (More Resources)

```bash
# Increase worker concurrency
worker:
  command: celery -A app.tasks.celery_app worker -l info --concurrency=8

# Increase database pool
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=100
```

### Load Testing

```bash
# Install Apache Bench
apt-get install apache2-utils

# Run load test (1000 requests, 100 concurrent)
ab -n 1000 -c 100 http://localhost:8000/api/v1/health
```

## 🔧 Maintenance

### Regular Tasks

| Task | Frequency | Command |
|------|-----------|---------|
| Database Backup | Daily | `./deploy.sh backup` |
| Vacuum Database | Weekly | `docker-compose exec db vacuumdb -U prepedge prepedge` |
| Logs Rotation | Auto | Configured in `logging_config.py` |
| Security Updates | Monthly | `apt-get update && apt-get upgrade` |

### Database Maintenance

```bash
# Analyze query performance
docker-compose exec db psql -U prepedge -d prepedge -c "ANALYZE;"

# Cleanup old data
docker-compose exec db psql -U prepedge -d prepedge -c "
  DELETE FROM logs WHERE created_at < now() - interval '30 days';
"

# Check table sizes
docker-compose exec db psql -U prepedge -d prepedge -c "
  SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
  FROM pg_tables WHERE schemaname != 'pg_catalog'
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

## 🐛 Troubleshooting

### API Not Responding

```bash
# Check if container is running
docker ps | grep api

# View logs
docker-compose logs api

# Restart service
docker-compose restart api
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose exec db pg_isready

# View database logs
docker-compose logs db

# Check connection pool
docker-compose exec db psql -U prepedge -c "SELECT COUNT(*) FROM pg_stat_activity;"
```

### Celery Tasks Not Processing

```bash
# Check workers are alive
docker-compose exec worker celery -A app.tasks.celery_app inspect active

# Check queue
docker-compose exec redis redis-cli LLEN celery

# View worker logs
docker-compose logs worker
```

### Redis Memory Issues

```bash
# Check memory usage
docker-compose exec redis redis-cli INFO memory

# Set max memory policy
docker-compose exec redis redis-cli CONFIG SET maxmemory 2gb
```

## 📚 Documentation

- [DEPLOYMENT.md](./DEPLOYMENT.md) - Detailed production deployment guide
- [API Docs](http://localhost:8000/docs) - Interactive Swagger UI
- [Models](./app/models/) - Database models
- [Routes](./app/routes/) - API endpoints

## 🆘 Support

For issues and questions:
1. Check [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed guides
2. Review logs: `docker-compose logs -f`
3. Run health checks: `./deploy.sh health`
4. Check [Troubleshooting](#troubleshooting) section

## 📄 License

[Your License Here]

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Maintainer**: PrepEdge AI Team
