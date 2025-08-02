"""
Enhanced test script to verify Supabase-based API endpoints including leaderboard
"""

import os
import sys
import asyncio
import pytest
import httpx
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List, Generator, AsyncGenerator
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the FastAPI app
from main import app

# Load environment variables
load_dotenv()

# Get API base URL from environment or use default
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

class TestLogger:
    """Helper class for consistent test output formatting"""
    @staticmethod
    def info(msg: str):
        print(f"ℹ️  {msg}")
    
    @staticmethod
    def success(msg: str):
        print(f"✅ {msg}")
    
    @staticmethod
    def warning(msg: str):
        print(f"⚠️  {msg}")
    
    @staticmethod
    def error(msg: str):
        print(f"❌ {msg}")
    
    @staticmethod
    def section(title: str):
        print(f"\n{'='*50}")
        print(f"🔍 {title}")
        print(f"{'='*50}")

@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI app"""
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="session")
def access_token() -> str:
    """Fixture to provide an access token for authenticated requests"""
    # In a real test, you would authenticate with test credentials
    # For now, we'll use a test token or environment variable
    test_token = os.getenv("TEST_ACCESS_TOKEN", "test_token")
    if not test_token or test_token == "test_token":
        TestLogger.warning("Using test token - some endpoints may require a valid token")
    return test_token

@pytest.fixture(scope="module")
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create an async HTTP client for testing"""
    async with httpx.AsyncClient() as client:
        yield client

@pytest.mark.asyncio
async def test_authentication(access_token: str, async_client: AsyncGenerator[httpx.AsyncClient, None]):
    """Test authentication and verify the token works"""
    TestLogger.section("Testing Authentication")
    
    # Get the client from the generator
    client = await async_client.__anext__()
    
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test a protected endpoint
        response = await client.get(
            f"{API_BASE_URL}/api/players/me",
            headers=headers
        )
        
        if response.status_code == 200:
            TestLogger.success("Authentication successful")
            return True
        elif response.status_code == 401:
            TestLogger.warning("Authentication failed - using test token")
            return False
        else:
            TestLogger.warning(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        TestLogger.error(f"Error in test_authentication: {str(e)}")
        return False

@pytest.mark.asyncio
async def test_players_endpoint(access_token: str, async_client: httpx.AsyncClient) -> Optional[Dict[str, Any]]:
    """Test players endpoints"""
    TestLogger.section("Testing Players Endpoint")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        # Get current user's profile
        TestLogger.info("Testing GET /players/me/profile")
        response = await async_client.get(
            f"{API_BASE_URL}/api/players/me/profile",
            headers=headers
        )
        
        if response.status_code == 200:
            player_data = response.json()
            TestLogger.success(f"Retrieved player profile: {player_data.get('gamertag')}")
            return player_data
        else:
            TestLogger.warning(f"Failed to get player profile: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        TestLogger.error(f"Error in test_players_endpoint: {str(e)}")
        return None

@pytest.mark.asyncio
async def test_events_endpoint(access_token: str, async_client: httpx.AsyncClient) -> List[Dict[str, Any]]:
    """Test events endpoints"""
    TestLogger.section("Testing Events Endpoint")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        # List all events
        TestLogger.info("Testing GET /events/")
        response = await async_client.get(
            f"{API_BASE_URL}/api/events/",
            headers=headers
        )
        
        if response.status_code == 200:
            events = response.json()
            TestLogger.success(f"Retrieved {len(events)} events")
            return events
        else:
            TestLogger.warning(f"Failed to get events: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        TestLogger.error(f"Error in test_events_endpoint: {str(e)}")
        return []

@pytest.mark.asyncio
async def test_leaderboard_endpoints(access_token: str, async_client: httpx.AsyncClient) -> Dict[str, Any]:
    """Test leaderboard endpoints"""
    TestLogger.section("Testing Leaderboard Endpoints")
    headers = {"Authorization": f"Bearer {access_token}"}
    results = {
        "global": False,
        "top_players": False,
        "tier_leaderboard": False,
        "platform_leaderboard": False,
        "region_leaderboard": False
    }
    
    try:
        # Test global leaderboard
        TestLogger.info("Testing GET /leaderboard/global")
        response = await async_client.get(
            f"{API_BASE_URL}/api/leaderboard/global?limit=5",
            headers=headers
        )
        
        if response.status_code == 200:
            leaderboard = response.json()
            if leaderboard:
                results["global"] = True
                TestLogger.success(f"Retrieved global leaderboard with {len(leaderboard)} players")
                
                # Test tier leaderboard with the first player's tier if available
                if leaderboard and "tier" in leaderboard[0]:
                    tier = leaderboard[0]["tier"]
                    tier_response = await async_client.get(
                        f"{API_BASE_URL}/api/leaderboard/tier/{tier}?limit=3",
                        headers=headers
                    )
                    if tier_response.status_code == 200:
                        tier_leaderboard = tier_response.json()
                        results["tier_leaderboard"] = True
                        TestLogger.success(f"Retrieved {tier} leaderboard with {len(tier_leaderboard)} players")
                    else:
                        TestLogger.warning(f"Failed to get {tier} leaderboard: {tier_response.status_code}")
                
                # Test platform leaderboard if platform is available
                if leaderboard and "platform" in leaderboard[0]:
                    platform = leaderboard[0]["platform"]
                    platform_response = await async_client.get(
                        f"{API_BASE_URL}/api/leaderboard/platform/{platform}?limit=3",
                        headers=headers
                    )
                    if platform_response.status_code == 200:
                        platform_leaderboard = platform_response.json()
                        results["platform_leaderboard"] = True
                        TestLogger.success(f"Retrieved {platform} leaderboard with {len(platform_leaderboard)} players")
                    else:
                        TestLogger.warning(f"Failed to get {platform} leaderboard: {platform_response.status_code}")
                
                # Test region leaderboard if region is available
                if leaderboard and "region" in leaderboard[0] and leaderboard[0]["region"]:
                    region = leaderboard[0]["region"]
                    region_response = await async_client.get(
                        f"{API_BASE_URL}/api/leaderboard/region/{region}?limit=3",
                        headers=headers
                    )
                    if region_response.status_code == 200:
                        region_leaderboard = region_response.json()
                        results["region_leaderboard"] = True
                        TestLogger.success(f"Retrieved {region} leaderboard with {len(region_leaderboard)} players")
                    else:
                        TestLogger.warning(f"Failed to get {region} leaderboard: {region_response.status_code}")
            else:
                TestLogger.warning("Global leaderboard is empty")
        else:
            TestLogger.error(f"Failed to get global leaderboard: {response.status_code} - {response.text}")
        
        # Test top players endpoint
        TestLogger.info("\nTesting GET /leaderboard/global/top")
        top_response = await async_client.get(
            f"{API_BASE_URL}/api/leaderboard/global/top?limit=3",
            headers=headers
        )
        
        if top_response.status_code == 200:
            top_players = top_response.json()
            if top_players:
                results["top_players"] = True
                TestLogger.success(f"Retrieved top {len(top_players)} players")
            else:
                TestLogger.warning("Top players list is empty")
        else:
            TestLogger.error(f"Failed to get top players: {top_response.status_code} - {top_response.text}")
        
        return results
    except Exception as e:
        TestLogger.error(f"Error in test_leaderboard_endpoints: {str(e)}")
        return results

async def main():
    """Main test function"""
    TestLogger.section("Starting Supabase API Endpoint Tests")
    
    # Test authentication
    auth_result = await test_authentication(access_token(), async_client())
    if not auth_result:
        TestLogger.error("Authentication failed. Exiting tests.")
        sys.exit(1)
    
    # Run tests
    test_results = {
        "player": await test_players_endpoint(access_token(), async_client()) is not None,
        "events": len(await test_events_endpoint(access_token(), async_client())) > 0,
        "leaderboard": await test_leaderboard_endpoints(access_token(), async_client())
    }
    
    # Print summary
    TestLogger.section("Test Summary")
    
    # Player test result
    player_status = "✅ PASSED" if test_results["player"] else "❌ FAILED"
    print(f"Player Profile: {player_status}")
    
    # Events test result
    events_status = "✅ PASSED" if test_results["events"] else "⚠️  NO EVENTS"
    print(f"Events: {events_status}")
    
    # Leaderboard test results
    print("\nLeaderboard Tests:")
    for test_name, passed in test_results["leaderboard"].items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"- {test_name.replace('_', ' ').title()}: {status}")
    
    # Overall status
    all_passed = all([
        test_results["player"],
        test_results["events"],
        all(test_results["leaderboard"].values())
    ])
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED OR HAD ISSUES")
    print("="*50)

if __name__ == "__main__":
    # Run pytest with the current file
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
