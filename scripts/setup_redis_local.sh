#!/bin/bash

# Redis Local Setup Script
# This script helps install and configure Redis locally

echo "🚀 Redis Local Setup Script"
echo "=========================="

# Detect operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "📱 Detected macOS"
    echo "Installing Redis using Homebrew..."
    
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew not found. Please install Homebrew first:"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    brew install redis
    brew services start redis
    
    echo "✅ Redis installed and started!"
    echo "   To stop: brew services stop redis"
    echo "   To restart: brew services restart redis"
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "🐧 Detected Linux"
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        echo "Installing Redis using apt..."
        sudo apt update
        sudo apt install -y redis-server
        sudo systemctl start redis-server
        sudo systemctl enable redis-server
        
        echo "✅ Redis installed and started!"
        echo "   To stop: sudo systemctl stop redis-server"
        echo "   To restart: sudo systemctl restart redis-server"
        
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        echo "Installing Redis using yum..."
        sudo yum install -y redis
        sudo systemctl start redis
        sudo systemctl enable redis
        
        echo "✅ Redis installed and started!"
        echo "   To stop: sudo systemctl stop redis"
        echo "   To restart: sudo systemctl restart redis"
        
    else
        echo "❌ Unsupported Linux distribution. Please install Redis manually."
        exit 1
    fi
    
else
    echo "❌ Unsupported operating system: $OSTYPE"
    echo "Please install Redis manually:"
    echo "   - macOS: brew install redis"
    echo "   - Ubuntu/Debian: sudo apt install redis-server"
    echo "   - Windows: Download from https://redis.io/download"
    exit 1
fi

# Test Redis connection
echo ""
echo "🧪 Testing Redis connection..."
if redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis is running and responding!"
else
    echo "❌ Redis is not responding. Please check the installation."
    exit 1
fi

echo ""
echo "🎉 Setup complete! Your Redis server is ready."
echo ""
echo "Next steps:"
echo "1. Make sure your .env file has: REDIS_URL=redis://localhost:6379/0"
echo "2. Start your FastAPI application"
echo "3. Or if you don't want Redis, set DISABLE_RATE_LIMITING=true in your .env file" 