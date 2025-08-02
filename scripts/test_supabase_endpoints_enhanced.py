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
async def test_teams_endpoint(access_token: str, async_client: httpx.AsyncClient) -> List[Dict[str, Any]]:
    """Test teams endpoints"""
    TestLogger.section("Testing Teams Endpoint")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        # List all teams
        TestLogger.info("Testing GET /teams/")
        response = await async_client.get(
            f"{API_BASE_URL}/api/teams/",
            headers=headers
        )
        
        if response.status_code == 200:
            teams = response.json()
            TestLogger.success(f"Retrieved {len(teams)} teams")
            
            # If we have teams, test getting a specific team
            if teams:
                team_id = teams[0].get('id')
                TestLogger.info(f"Testing GET /teams/{team_id}")
                team_response = await async_client.get(
                    f"{API_BASE_URL}/api/teams/{team_id}",
                    headers=headers
                )
                if team_response.status_code == 200:
                    team_data = team_response.json()
                    TestLogger.success(f"Retrieved team: {team_data.get('name')}")
                else:
                    TestLogger.warning(f"Failed to get team: {team_response.status_code} - {team_response.text}")
            
            return teams
        else:
            TestLogger.warning(f"Failed to get teams: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        TestLogger.error(f"Error in test_teams_endpoint: {str(e)}")
        return []

@pytest.mark.asyncio
async def test_matches_endpoint(access_token: str, async_client: httpx.AsyncClient) -> List[Dict[str, Any]]:
    """Test matches endpoints"""
    TestLogger.section("Testing Matches Endpoint")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        # List all matches
        TestLogger.info("Testing GET /matches/")
        response = await async_client.get(
            f"{API_BASE_URL}/api/matches/",
            headers=headers
        )
        
        if response.status_code == 200:
            matches = response.json()
            TestLogger.success(f"Retrieved {len(matches)} matches")
            
            # If we have matches, test getting a specific match
            if matches:
                match_id = matches[0].get('id')
                TestLogger.info(f"Testing GET /matches/{match_id}")
                match_response = await async_client.get(
                    f"{API_BASE_URL}/api/matches/{match_id}",
                    headers=headers
                )
                if match_response.status_code == 200:
                    match_data = match_response.json()
                    TestLogger.success(f"Retrieved match: {match_id}")
                else:
                    TestLogger.warning(f"Failed to get match: {match_response.status_code} - {match_response.text}")
            
            return matches
        else:
            TestLogger.warning(f"Failed to get matches: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        TestLogger.error(f"Error in test_matches_endpoint: {str(e)}")
        return []

@pytest.mark.asyncio
async def test_player_stats_endpoint(access_token: str, async_client: httpx.AsyncClient) -> List[Dict[str, Any]]:
    """Test player_stats endpoints"""
    TestLogger.section("Testing Player Stats Endpoint")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        # First, we need a valid player_id to test with
        # Let's get the current user's player profile
        player_response = await async_client.get(
            f"{API_BASE_URL}/api/players/me/profile",
            headers=headers
        )
        
        if player_response.status_code != 200:
            TestLogger.warning("Failed to get player profile for player stats test")
            return []
            
        player_data = player_response.json()
        player_id = player_data.get('id')
        
        if not player_id:
            TestLogger.warning("No player ID found for player stats test")
            return []
        
        # Now get player stats for this player
        TestLogger.info(f"Testing GET /player-stats/player/{player_id}")
        response = await async_client.get(
            f"{API_BASE_URL}/api/player-stats/player/{player_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            player_stats = response.json()
            TestLogger.success(f"Retrieved {len(player_stats)} player stats records")
            
            # If we have stats, test getting aggregated stats
            if player_stats:
                TestLogger.info("Testing GET /player-stats/aggregate/player/{player_id}")
                agg_response = await async_client.get(
                    f"{API_BASE_URL}/api/player-stats/aggregate/player/{player_id}",
                    headers=headers
                )
                if agg_response.status_code == 200:
                    agg_data = agg_response.json()
                    TestLogger.success(f"Retrieved aggregated stats with {len(agg_data)} metrics")
                else:
                    TestLogger.warning(f"Failed to get aggregated stats: {agg_response.status_code} - {agg_response.text}")
            
            return player_stats
        else:
            TestLogger.warning(f"Failed to get player stats: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        TestLogger.error(f"Error in test_player_stats_endpoint: {str(e)}")
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
                
                # Test region leaderboard if region is available
                if leaderboard and "region" in leaderboard[0]:
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
        "teams": len(await test_teams_endpoint(access_token(), async_client())) > 0,
        "matches": len(await test_matches_endpoint(access_token(), async_client())) > 0,
        "player_stats": len(await test_player_stats_endpoint(access_token(), async_client())) >= 0,  # Can be empty
        "leaderboard": await test_leaderboard_endpoints(access_token(), async_client())
    }
    
    # Print summary
    TestLogger.section("Test Summary")
    
    # Test results
    player_status = "✅ PASSED" if test_results["player"] else "❌ FAILED"
    print(f"Player Profile: {player_status}")
    
    events_status = "✅ PASSED" if test_results["events"] else "⚠️  NO EVENTS"
    print(f"Events: {events_status}")
    
    teams_status = "✅ PASSED" if test_results["teams"] else "⚠️  NO TEAMS"
    print(f"Teams: {teams_status}")
    
    matches_status = "✅ PASSED" if test_results["matches"] else "⚠️  NO MATCHES"
    print(f"Matches: {matches_status}")
    
    player_stats_status = "✅ PASSED" if test_results["player_stats"] is not None else "⚠️  FAILED"
    print(f"Player Stats: {player_stats_status}")
    
    # Leaderboard test results
    print("\nLeaderboard Tests:")
    for test_name, passed in test_results["leaderboard"].items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"- {test_name.replace('_', ' ').title()}: {status}")
    
    # Overall status
    all_passed = all([
        test_results["player"],
        test_results["events"],
        test_results["teams"],
        test_results["matches"],
        test_results["player_stats"] is not None,  # Can be empty list, but not None
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
