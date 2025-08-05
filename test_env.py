#!/usr/bin/env python3
"""
Test script to verify environment variables and rate limiter setup
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("🔧 Environment Test")
print("==================")

# Check if .env file exists
if os.path.exists('.env'):
    print("✅ .env file found")
else:
    print("❌ .env file not found")

# Check DISABLE_RATE_LIMITING variable
disable_limiting = os.getenv('DISABLE_RATE_LIMITING', 'not set')
print(f"DISABLE_RATE_LIMITING: {disable_limiting}")

# Test rate limiter import
try:
    from app.core.rate_limiter import limiter
    print("✅ Rate limiter imported successfully")
    
    # Check if it's a dummy limiter
    if hasattr(limiter, '__class__') and 'DummyLimiter' in str(limiter.__class__):
        print("✅ Using dummy rate limiter (no Redis needed)")
    else:
        print("ℹ️  Using real rate limiter")
        
except Exception as e:
    print(f"❌ Failed to import rate limiter: {e}")

print("\n�� Test complete!") 