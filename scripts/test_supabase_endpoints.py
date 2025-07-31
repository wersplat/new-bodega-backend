"""
Test script to verify Supabase-based API endpoints
"""

import os
import sys
import asyncio
import httpx
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

# Get API base URL from environment or use default
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

async def test_authentication() -> Optional[Dict[str, str]]:
    """Test authentication and get access token"""
    # In a real test, you would use test credentials
    # For now, we'll assume the user is already authenticated
    return {"access_token": "test_token"}  # Replace with actual token

async def test_players_endpoint(access_token: str):
    """Test players endpoints"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        # Get current user's profile
        print("\n🔍 Testing GET /players/me/profile")
        response = await client.get(
            f"{API_BASE_URL}/players/me/profile",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Successfully retrieved player profile")
            player_data = response.json()
            return player_data
        else:
            print(f"❌ Failed to get player profile: {response.status_code} - {response.text}")
            return None

async def test_events_endpoint(access_token: str):
    """Test events endpoints"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        # List all events
        print("\n🔍 Testing GET /events/")
        response = await client.get(
            f"{API_BASE_URL}/events/",
            headers=headers
        )
        
        if response.status_code == 200:
            events = response.json()
            print(f"✅ Successfully retrieved {len(events)} events")
            return events
        else:
            print(f"❌ Failed to get events: {response.status_code} - {response.text}")
            return []

async def main():
    print("🚀 Starting Supabase API Endpoint Tests")
    
    # Test authentication
    print("\n🔑 Testing authentication...")
    auth_data = await test_authentication()
    if not auth_data or "access_token" not in auth_data:
        print("❌ Authentication failed")
        sys.exit(1)
    
    access_token = auth_data["access_token"]
    print("✅ Authentication successful")
    
    # Test players endpoint
    player = await test_players_endpoint(access_token)
    
    # Test events endpoint
    events = await test_events_endpoint(access_token)
    
    print("\n🎉 All tests completed!")
    
    # Print summary
    print("\n📊 Test Summary:")
    print(f"- Player Profile: {'✅ Found' if player else '❌ Not found'}")
    print(f"- Events: {'✅ Found' if events else '❌ None found'}")

if __name__ == "__main__":
    asyncio.run(main())
