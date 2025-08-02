"""
Comprehensive tests for the Players router endpoints using mocks
"""
import os
import sys
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Union
import pytest
from fastapi.testclient import TestClient
from fastapi import status, HTTPException, Depends
from unittest.mock import MagicMock, patch, create_autospec
from pydantic import BaseModel

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import after setting up the path
from main import app
from app.core.auth import get_current_active_user, create_access_token
from app.core.supabase import SupabaseService, supabase as supabase_service

# Test client
client = TestClient(app)

# Mock data
TEST_PLAYER_ID = str(uuid.uuid4())
TEST_USER_ID = str(uuid.uuid4())
TEST_TEAM_ID = str(uuid.uuid4())
TEST_REGION_ID = str(uuid.uuid4())
TEST_GAMERTAG = "testplayer123"

# Test player data
TEST_PLAYER = {
    "id": TEST_PLAYER_ID,
    "user_id": TEST_USER_ID,
    "gamertag": TEST_GAMERTAG,
    "avatar_url": "https://example.com/avatar.jpg",

    "region": "NA",
    "timezone": "America/New_York",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "is_active": True,
    "last_online": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
}

# Mock the auth dependency
async def mock_get_current_user():
    return {
        "id": TEST_USER_ID,
        "email": "test@example.com",
        "is_active": True,
        "is_superuser": False
    }

# Apply the mock
app.dependency_overrides[get_current_active_user] = mock_get_current_user

# Mock for the Supabase client response
class MockSupabaseResponse:
    def __init__(self, data=None, error=None):
        self.data = data or []
        self.error = error

# Test suite for Players router
class TestPlayersRouter:
    @pytest.fixture(autouse=True)
    def setup_mocks(self, mocker):
        """Setup mocks for each test"""
        # Create a mock for the SupabaseService
        self.mock_supabase_service = mocker.patch('app.core.supabase.SupabaseService')
        
        # Setup mock methods for the SupabaseService
        # Mock get_client
        self.mock_client = mocker.MagicMock()
        self.mock_supabase_service.get_client.return_value = self.mock_client
        
        # Setup table mock
        self.mock_table = mocker.MagicMock()
        self.mock_client.table.return_value = self.mock_table
        
        # Default mock responses
        self.mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = MockSupabaseResponse(data=TEST_PLAYER)
        self.mock_table.select.return_value.eq.return_value.execute.return_value = MockSupabaseResponse(data=[TEST_PLAYER])
        self.mock_table.insert.return_value.execute.return_value = MockSupabaseResponse(data=[TEST_PLAYER])
        self.mock_table.update.return_value.eq.return_value.execute.return_value = MockSupabaseResponse(data=[TEST_PLAYER])
        
        # Mock the search response
        self.mock_table.ilike.return_value.limit.return_value.execute.return_value = MockSupabaseResponse(
            data=[
                {"id": str(uuid.uuid4()), "gamertag": "testplayer1"},
                {"id": str(uuid.uuid4()), "gamertag": "testplayer2"}
            ]
        )
        
        # Mock the empty search response
        self.mock_table.ilike.return_value.limit.return_value.execute.return_value = MockSupabaseResponse(data=[])
        
        # Mock the stats response
        self.mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = MockSupabaseResponse(
            data=[
                {"stat_name": "wins", "stat_value": 10},
                {"stat_name": "losses", "stat_value": 5}
            ]
        )
        
        # Mock the RP history response
        self.mock_client.table.return_value.select.return_value.order.return_value.limit.return_value.offset.return_value.execute.return_value = MockSupabaseResponse(
            data=[
                {"id": str(uuid.uuid4()), "rp_change": 10, "reason": "Match win", "created_at": datetime.now(timezone.utc).isoformat()},
                {"id": str(uuid.uuid4()), "rp_change": -5, "reason": "Match loss", "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()}
            ]
        )
        
        # Mock the player not found response
        self.mock_table.select.return_value.eq.return_value.single.side_effect = Exception("Not found")
        self.mock_table.select.return_value.eq.return_value.execute.return_value = MockSupabaseResponse(data=[])
        
        # Mock the gamertag check response
        self.mock_table.select.return_value.eq.return_value.execute.return_value = MockSupabaseResponse(data=[])
        
        # Mock the update response
        self.mock_table.update.return_value.eq.return_value.execute.return_value = MockSupabaseResponse(
            data=[{**TEST_PLAYER, "gamertag": "updated_gamertag"}]
        )
        
        # Mock the unauthorized response
        self.mock_unauthorized = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        # Mock the not found response
        self.mock_not_found = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
        
        # Mock the bad request response
        self.mock_bad_request = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request data"
        )
        
        # Generate auth token for the test user
        self.auth_token = create_access_token(
            data={"sub": "test@example.com"},
            expires_delta=timedelta(minutes=30)
        )
        
        # Set up auth header
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_create_player(self, mocker):
        """Test creating a new player"""
        self.setup_mocks(mocker)
        
        # Test data
        player_data = {
            "gamertag": TEST_GAMERTAG,
            "avatar_url": "https://example.com/avatar.jpg",
        
            "region": "NA",
            "timezone": "America/New_York"
        }
        
        # Configure the mock to return our test player
        self.mock_table.insert.return_value.execute.return_value = MockSupabaseResponse(
            data=[{**player_data, "id": TEST_PLAYER_ID, "user_id": TEST_USER_ID}]
        )
        
        # Make the request
        response = client.post(
            "/v1/players/",
            json=player_data,
            headers=self.headers
        )
        
        # Verify the response
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["gamertag"] == TEST_GAMERTAG
        assert "id" in response_data
        
        # Verify the Supabase client was called correctly
        self.mock_client.table.assert_called_with("players")
        self.mock_table.insert.assert_called()
        
        # Verify the insert was called with the correct data
        call_args = self.mock_table.insert.call_args[0][0]
        assert call_args["gamertag"] == TEST_GAMERTAG
        assert call_args["user_id"] == TEST_USER_ID
    
    def test_get_player_by_id(self, mocker):
        """Test getting a player by ID"""
        self.setup_mocks(mocker)
        
        # Configure the mock to return our test player
        self.mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = (
            MockSupabaseResponse(data=TEST_PLAYER)
        )
        
        # Make the request
        response = client.get(f"/v1/players/{TEST_PLAYER_ID}")
        
        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == TEST_PLAYER_ID
        assert response_data["gamertag"] == TEST_GAMERTAG
        
        # Verify the Supabase client was called correctly
        self.mock_client.table.assert_called_with("players")
        self.mock_table.select.assert_called_with("*")
        self.mock_table.select.return_value.eq.assert_called_with("id", TEST_PLAYER_ID)
        self.mock_table.select.return_value.eq.return_value.single.assert_called()
    
    def test_get_my_profile(self, mocker):
        """Test getting the current user's profile"""
        self.setup_mocks(mocker)
        
        # Configure the mock to return our test player
        self.mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = (
            MockSupabaseResponse(data=TEST_PLAYER)
        )
        
        # Make the request
        response = client.get("/v1/players/me", headers=self.headers)
        
        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == TEST_PLAYER_ID
        assert response_data["gamertag"] == TEST_GAMERTAG
        
        # Verify the Supabase client was called correctly
        self.mock_client.table.assert_called_with("players")
        self.mock_table.select.assert_called_with("*")
        self.mock_table.select.return_value.eq.assert_called_with("user_id", TEST_USER_ID)
        self.mock_table.select.return_value.eq.return_value.single.assert_called()
    
    def test_update_my_profile(self, mocker):
        """Test updating the current user's profile"""
        self.setup_mocks(mocker)
        
        # Configure the mocks for both the initial fetch and update
        self.mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = (
            MockSupabaseResponse(data=TEST_PLAYER)
        )
        
        # Mock the update response
        updated_player = {
            **TEST_PLAYER,
            "gamertag": "updated_gamertag",

            "avatar_url": "https://example.com/new_avatar.jpg",
            "region": "EU",
            "timezone": "Europe/London"
        }
        self.mock_table.update.return_value.eq.return_value.execute.return_value = MockSupabaseResponse(
            data=[updated_player]
        )
        
        # Test update data
        update_data = {
            "gamertag": "updated_gamertag",

            "avatar_url": "https://example.com/new_avatar.jpg",
            "region": "EU",
            "timezone": "Europe/London"
        }
        
        # Make the request
        response = client.put(
            "/v1/players/me",
            json=update_data,
            headers=self.headers
        )
        
        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["gamertag"] == "updated_gamertag"

        
        # Verify the Supabase client was called correctly
        self.mock_client.table.assert_called_with("players")
        self.mock_table.update.assert_called()
        
        # Verify the update was called with the correct data
        update_call_args = self.mock_table.update.call_args[0][0]
        assert update_call_args["gamertag"] == "updated_gamertag"

        
        # Verify the update was filtered by user_id
        self.mock_table.update.return_value.eq.assert_called_with("user_id", TEST_USER_ID)
    
    def test_search_players(self, mocker):
        """Test searching for players by gamertag"""
        self.setup_mocks(mocker)
        
        # Configure the mock to return test search results
        test_results = [
            {"id": str(uuid.uuid4()), "gamertag": "testplayer1"},
            {"id": str(uuid.uuid4()), "gamertag": "testplayer2"}
        ]
        self.mock_table.ilike.return_value.limit.return_value.execute.return_value = (
            MockSupabaseResponse(data=test_results)
        )
        
        # Test search query
        search_query = "test"
        
        # Make the request
        response = client.get(
            f"/v1/players/search?query={search_query}",
            headers=self.headers
        )
        
        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data) == 2
        assert all("gamertag" in player for player in response_data)
        assert all(player["gamertag"].startswith("testplayer") for player in response_data)
        
        # Verify the Supabase client was called correctly
        self.mock_client.table.assert_called_with("players")
        self.mock_table.ilike.assert_called_with("gamertag", f"%{search_query}%")
        self.mock_table.ilike.return_value.limit.assert_called_with(10)  # Default limit
    
    def test_get_player_not_found(self, mocker):
        """Test getting a non-existent player by ID"""
        self.setup_mocks(mocker)
        
        # Configure the mock to simulate a player not found
        self.mock_table.select.return_value.eq.return_value.single.side_effect = Exception("Not found")
        
        # Make the request with a non-existent player ID
        non_existent_id = str(uuid.uuid4())
        response = client.get(f"/v1/players/{non_existent_id}")
        
        # Verify the response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Player not found" in response.json()["detail"]
        
        # Verify the Supabase client was called correctly
        self.mock_client.table.assert_called_with("players")
        self.mock_table.select.assert_called_with("*")
        self.mock_table.select.return_value.eq.assert_called_with("id", non_existent_id)
        self.mock_table.select.return_value.eq.return_value.single.assert_called()
    
    def test_update_profile_invalid_data(self, mocker):
        """Test updating a profile with invalid data"""
        self.setup_mocks(mocker)
        
        # Configure the mock to return the current player
        self.mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = (
            MockSupabaseResponse(data=TEST_PLAYER)
        )
        
        # Test update with invalid data (missing required fields)
        invalid_data = {
            "gamertag": "",  # Gamertag cannot be empty
            "email": "not-an-email"  # Invalid email format
        }
        
        # Make the request
        response = client.put(
            "/v1/players/me",
            json=invalid_data,
            headers=self.headers
        )
        
        # Verify the response
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        response_data = response.json()
        
        # Check that we got validation errors for both fields
        errors = response_data["detail"]
        error_messages = [error["msg"].lower() for error in errors]
        
        assert any("string_too_short" in msg for msg in error_messages)  # For empty gamertag
        assert any("value is not a valid email" in msg for msg in error_messages)  # For invalid email
        
        # Verify the Supabase client was called to get the current player
        self.mock_client.table.assert_called_with("players")
        self.mock_table.select.assert_called_with("*")
        
        # But no update should have been attempted
        self.mock_table.update.assert_not_called()
    
    def test_get_player_history(self, mocker):
        """Test getting a player's RP history through the dedicated endpoint"""
        self.setup_mocks(mocker)
        
        # Mock the history data
        history_data = [
            {"id": str(uuid.uuid4()), "rp_change": 10, "reason": "Match win", "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "rp_change": -5, "reason": "Match loss", "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()}
        ]
        
        # Configure the mock to return history data
        self.mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.offset.return_value.execute.return_value = (
            MockSupabaseResponse(data=history_data)
        )
        
        # Make the request with pagination parameters
        limit = 10
        offset = 0
        response = client.get(
            f"/v1/players/{TEST_PLAYER_ID}/history?limit={limit}&offset={offset}",
            headers=self.headers
        )
        
        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data) == 2
        assert all("rp_change" in entry for entry in response_data)
        assert all("reason" in entry for entry in response_data)
        
        # Verify the Supabase client was called correctly
        self.mock_client.table.assert_called_with("player_rp_history")
        self.mock_client.table.return_value.select.assert_called_with("*")
        
        # Verify the query was built correctly
        self.mock_client.table.return_value.select.return_value.eq.assert_called_with("player_id", TEST_PLAYER_ID)
        self.mock_client.table.return_value.select.return_value.eq.return_value.order.assert_called_with("created_at", desc=True)
        self.mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.assert_called_with(limit)
        self.mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.offset.assert_called_with(offset)
    
    def test_unauthorized_access(self, mocker):
        """Test accessing protected endpoints without authentication"""
        self.setup_mocks(mocker)
        
        # Test without auth header on various endpoints
        endpoints = [
            ("POST", "/v1/players/", {"gamertag": "testplayer"}),
            ("GET", "/v1/players/me", None),
            ("PUT", "/v1/players/me", {"gamertag": "updated"}),
            ("GET", f"/v1/players/{TEST_PLAYER_ID}/history", None)
        ]
        
        for method, url, json_data in endpoints:
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json=json_data)
            elif method == "PUT":
                response = client.put(url, json=json_data)
                
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Not authenticated" in response.json()["detail"]
        
        # Test with invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.get(
            "/v1/players/me",
            headers=invalid_headers
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Verify no database operations were performed for unauthorized access
        self.mock_table.insert.assert_not_called()
        self.mock_table.update.assert_not_called()
        self.mock_table.delete.assert_not_called()
    
    def test_duplicate_gamertag(self, mocker):
        """Test creating a player with a duplicate gamertag"""
        self.setup_mocks(mocker)
        
        # Mock the gamertag check to return an existing player
        self.mock_table.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": str(uuid.uuid4()), "gamertag": "existing_player"}
        ]
        
        # Test data with duplicate gamertag
        player_data = {
            "gamertag": "existing_player",
            "avatar_url": "https://example.com/avatar.jpg",
        
            "region": "NA",
            "timezone": "America/New_York"
        }
        
        # Make the request
        response = client.post(
            "/v1/players/",
            json=player_data,
            headers=self.headers
        )
        
        # Verify the response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json().get("detail", "").lower()
    
    def test_update_nonexistent_profile(self, mocker):
        """Test updating a profile that doesn't exist"""
        self.setup_mocks(mocker)
        
        # Mock the player not found response
        self.mock_table.select.return_value.eq.return_value.execute.return_value.data = []
        
        # Test update data
        update_data = {
            "gamertag": "new_gamertag"
        }
        
        # Make the request
        response = client.patch(
            "/v1/players/me",
            json=update_data,
            headers=self.headers
        )
        
        # Verify the response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_player_stats(self, mocker):
        """Test getting a player's statistics"""
        self.setup_mocks(mocker)
        
        # Mock the player data
        self.mock_table.select.return_value.eq.return_value.execute.return_value.data = [TEST_PLAYER]
        
        # Mock the stats response
        stats_data = [
            {"stat_name": "wins", "stat_value": 10},
            {"stat_name": "losses", "stat_value": 5},
            {"stat_name": "kills", "stat_value": 150},
            {"stat_name": "deaths", "stat_value": 100},
            {"stat_name": "assists", "stat_value": 75}
        ]
        self.mock_table.table.return_value.select.return_value.eq.return_value.execute.return_value.data = stats_data
        
        # Make the request
        response = client.get(f"/v1/players/{TEST_PLAYER_ID}/stats")
        
        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        assert "wins" in response.json()
        assert response.json()["wins"] == 10
        assert "losses" in response.json()
        assert "kills" in response.json()
        assert "deaths" in response.json()
        assert "assists" in response.json()
        
        # Verify the Supabase client was called correctly
        self.mock_supabase.table.assert_any_call("players")
        self.mock_supabase.table.assert_any_call("player_stats")
    
    def test_search_players_empty_query(self, mocker):
        """Test searching players with an empty query"""
        self.setup_mocks(mocker)
        
        # Make the request with empty query
        response = client.get("/v1/players/search", params={"query": ""})
        
        # Verify the response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "query parameter is required" in response.json()["detail"]
    
    def test_search_players_limit(self, mocker):
        """Test searching players with a custom limit"""
        self.setup_mocks(mocker)
        
        # Mock the search results
        search_results = [
            {"id": str(uuid.uuid4()), "gamertag": f"testplayer{i}"}
            for i in range(5)  # Return 5 results
        ]
        self.mock_table.ilike.return_value.limit.return_value.execute.return_value.data = search_results
        
        # Make the request with limit=5
        response = client.get(
            "/v1/players/search",
            params={"query": "test", "limit": 5}
        )
        
        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5
        
        # Verify the limit was passed to the query
        self.mock_table.ilike.return_value.limit.assert_called_with(5)
