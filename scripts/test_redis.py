#!/usr/bin/env python3
"""
Redis connection test script
Tests Redis connectivity and provides diagnostic information
"""

import asyncio
import redis.asyncio as redis
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_redis_connection():
    """Test Redis connection and provide diagnostic information"""
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    print(f"Testing Redis connection to: {redis_url}")
    
    try:
        # Create Redis client
        client = redis.Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # Test connection
        await client.ping()
        print("✅ Redis connection successful!")
        
        # Test basic operations
        await client.set("test_key", "test_value")
        value = await client.get("test_key")
        await client.delete("test_key")
        
        if value == "test_value":
            print("✅ Redis read/write operations successful!")
        else:
            print("❌ Redis read/write operations failed!")
            
        await client.close()
        
    except redis.ConnectionError as e:
        print(f"❌ Redis connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure Redis is running:")
        print("   - Local: redis-server")
        print("   - Docker: docker run -d -p 6379:6379 redis:7-alpine")
        print("   - Docker Compose: docker-compose up redis")
        print("2. Check if Redis URL is correct in your .env file")
        print("3. Verify firewall settings if using remote Redis")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(test_redis_connection()) 