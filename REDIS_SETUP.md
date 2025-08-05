# Redis Setup Guide

## Issue
The application is failing with Redis connection errors:
```
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused.
```

## Quick Fix Options

### Option 1: Use Docker Compose (Recommended)
```bash
cd new-bodega-backend
docker-compose up redis
```

### Option 2: Install Redis Locally
```bash
# macOS
brew install redis
redis-server

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# Windows
# Download from https://redis.io/download
```

### Option 3: Use Docker Redis Only
```bash
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

## Test Redis Connection
```bash
cd new-bodega-backend
python scripts/test_redis.py
```

## Environment Configuration
Make sure your `.env` file has the correct Redis URL:
```env
REDIS_URL=redis://localhost:6379/0
```

## Fallback Solution
The application now includes a fallback to in-memory storage when Redis is unavailable. This means:
- Rate limiting will still work (but not persist across restarts)
- The application won't crash when Redis is down
- Performance may be slightly reduced for high-traffic scenarios

## Production Considerations
For production environments:
1. Use a managed Redis service (AWS ElastiCache, Redis Cloud, etc.)
2. Configure proper authentication and security
3. Set up Redis clustering for high availability
4. Monitor Redis performance and memory usage

## Troubleshooting
1. Check if Redis is running: `redis-cli ping`
2. Verify port 6379 is not blocked by firewall
3. Check Redis logs for errors
4. Ensure Redis URL is correct in environment variables 