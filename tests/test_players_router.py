"""
Comprehensive tests for the Players router endpoints using Supabase
"""
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import pytest
from fastapi.testclient import TestClient
from fastapi import status

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from app.core.auth import get_current_active_user, create_access_token
from app.core.supabase import supabase as supabase_client

# Override the auth dependency for testing
async def override_get_current_active_user():
    return {"id": str(uuid.uuid4()), "email": "test@example.com", "is_active": True, "is_superuser": False}

# Apply the override
app.dependency_overrides[get_current_active_user] = override_get_current_active_user

# Test client
client = TestClient(app)

def create_test_region() -> Dict[str, Any]:
    """Create a test region in Supabase"""
    region_data = {
        "id": str(uuid.uuid4()),
        "name": "Test Region",
        "code": "TEST",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    supabase_client.insert("regions", region_data)
    return region_data

def create_test_team(region_id: str) -> Dict[str, Any]:
    """Create a test team in Supabase"""
    team_data = {
        "id": str(uuid.uuid4()),
        "name": f"Test Team {str(uuid.uuid4())[:8]}",
        "region_id": region_id,
        "current_rp": 1000,
        "elo_rating": 1500,
        "leaderboard_tier": "CHALLENGER",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    supabase_client.insert("teams", team_data)
    return team_data

def create_test_player(region_id: str, team_id: str = None) -> Dict[str, Any]:
    """Create a test player in Supabase"""
    player_data = {
        "id": str(uuid.uuid4()),
        "gamertag": f"testplayer_{str(uuid.uuid4())[:8]}",
        "position": "Point Guard",
        "region_id": region_id,
        "current_team_id": team_id,
        "performance_score": 75.5,
        "player_rp": 1000,
        "player_rank_score": 1500,
        "salary_tier": "A",
        "monthly_value": 1000,
        "is_rookie": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    supabase_client.insert("players", player_data)
    return player_data

# Test suite for Players router
class TestPlayersRouter:
    @pytest.fixture(autouse=True)
    def setup(self, test_supabase_fixture):
        """Setup test data"""
        self.supabase = test_supabase_fixture
        
        # Create test region
        self.test_region = create_test_region()
        
        # Create test team
        self.test_team = create_test_team(self.test_region["id"])
        
        # Create test players
        self.test_player = create_test_player(
            region_id=self.test_region["id"],
            team_id=self.test_team["id"]
        )
        
        # Create another test player for search tests
        self.other_player = create_test_player(
            region_id=self.test_region["id"]
        )
        
        # Generate auth token for the test user
        self.auth_headers = {"Authorization": f"Bearer {create_access_token(data={'sub': self.test_player['id']})}"}
        
        yield
        
        # Cleanup - Delete test data
        try:
            # Clean up players first (due to foreign key constraints)
            self.supabase.delete("players", self.test_player["id"])
            self.supabase.delete("players", self.other_player["id"])
            
            # Then clean up team and region
            self.supabase.delete("teams", self.test_team["id"])
            self.supabase.delete("regions", self.test_region["id"])
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def test_get_player_by_id(self):
        """Test getting a player by ID"""
        response = client.get(
            f"/api/players/{self.test_player['id']}",
            headers=self.auth_headers
        )
        assert response.status_code == status.HTTP_200_OK, f"Response: {response.text}"
        data = response.json()
        assert data["id"] == self.test_player["id"]
        assert data["gamertag"] == self.test_player["gamertag"]
        assert "position" in data
        assert "player_rp" in data
    
    def test_update_my_profile(self):
        """Test updating the current user's player profile"""
        update_data = {
            "gamertag": "UpdatedGamertag",
            "region": "EU"
        }
        
        response = client.put(
            "/api/players/me/profile",
            json=update_data,
            headers=self.auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["gamertag"] == "UpdatedGamertag"
        assert data["region"] == "EU"
    
    def test_get_player_history(self):
        """Test getting a player's profile with RP history"""
        response = client.get(
            f"/api/players/{self.test_player.id}/history",
            headers=self.auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == self.test_player.id
        assert "rp_history" in data
        assert len(data["rp_history"]) == 2
    
    def test_search_player_by_gamertag(self):
        """Test searching for a player by gamertag"""
        # Search with partial gamertag
        search_term = self.test_player.gamertag[:4]
        response = client.get(f"/api/players/search/{search_term}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == self.test_player.id
        assert search_term.lower() in data["gamertag"].lower()
    
    def test_search_player_not_found(self):
        """Test searching for a non-existent player"""
        response = client.get("/api/players/search/nonexistent")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_unauthorized_access(self):
        """Test accessing protected endpoints without authentication"""
        # Test GET /me/profile without auth
        response = client.get("/api/players/me/profile")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test PUT /me/profile without auth
        response = client.put("/api/players/me/profile", json={"gamertag": "NewGamertag"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_profile_validation(self):
        """Test validation when updating profile"""
        # Test with empty gamertag
        response = client.put(
            "/api/players/me/profile",
            json={"gamertag": ""},
            headers=self.auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test with invalid region
        response = client.put(
            "/api/players/me/profile",
            json={"region": "InvalidRegion"},
            headers=self.auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
