"""
Comprehensive test for Player CRUD operations with Supabase
"""
import os
import unittest
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, Dict, Optional

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from fastapi import status
from parameterized import parameterized
from supabase import create_client

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the FastAPI app
import sys
import os

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from app.core.supabase import supabase as supabase_client
from app.core.auth import get_current_active_user

# Mock authentication
async def mock_get_current_active_user():
    # Create a simple object with an id attribute that the API expects
    user = SimpleNamespace()
    user.id = 12345  # Match the expected integer type
    user.email = "test@example.com"
    user.is_active = True
    user.is_superuser = False
    return user

# Override the auth dependency
app.dependency_overrides[get_current_active_user] = mock_get_current_active_user

# Test client
client = TestClient(app)

def get_existing_region_id() -> Optional[str]:
    """Try to get an existing region_id from the database"""
    try:
        response = supabase_client.fetch_all('regions', limit=1)
        if response and isinstance(response, list) and len(response) > 0:
            return response[0]['id']
        return None
    except Exception as e:
        print(f"⚠️  Could not fetch regions: {str(e)}")
        return None

def create_test_player_data(
    region_id: Optional[str] = None,
    include_optional: bool = True,
    include_id: bool = True,
    id: Optional[str] = None,  # Default to None, will be generated if not provided
    user_id: Optional[str] = None  # Required field for player creation
) -> Dict[str, Any]:
    """
    Create test player data that matches the actual database schema.
    
    Args:
        region_id: Optional region ID (UUID string)
        include_optional: Whether to include optional fields
        include_id: Whether to include the id field (needed for updates/deletes)
        id: The id to associate with this player (will be generated if not provided)
        user_id: The user ID associated with this player (required)
    """
    if user_id is None:
        # Use the test user ID if available, otherwise generate a random UUID
        user_id = getattr(TestPlayersEndpoints, 'test_user_id', str(uuid.uuid4()))
    # Generate a UUID for the player if not provided
    if id is None:
        id = str(uuid.uuid4())
    
    # Create base player data with required fields
    player_data = {
        "id": id,
        "gamertag": f"testplayer_{id[:8]}",
        "position": "Point Guard",  # Must be one of: "Point Guard", "Shooting Guard", "Lock", "Power Forward", "Center"
        "region_id": region_id,  # Can be None
        "current_team_id": None,  # Can be set to None or a valid team_id (as UUID string)
        "performance_score": 75.5,
        "player_rp": 1000,
        "player_rank_score": 1500,
        "salary_tier": "B",  # Must be one of: "S", "A", "B", "C", "D"
        "monthly_value": 5000,
        "is_rookie": True,
        "discord_id": f"test_discord_{id[:8]}",
        "twitter_id": f"test_twitter_{id[:8]}",
        "alternate_gamertag": f"alt_{id[:8]}",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Remove optional fields if not needed
    if not include_optional:
        optional_fields = [
            "current_team_id", "performance_score", "player_rp", "player_rank_score",
            "salary_tier", "monthly_value", "is_rookie", "discord_id", "twitter_id",
            "alternate_gamertag", "created_at"
        ]
        for field in optional_fields:
            player_data.pop(field, None)
    
    # Remove ID if not needed
    if not include_id:
        player_data.pop("id", None)
    
    return player_data

class TestPlayersEndpoints(unittest.TestCase):
    """Test suite for players endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any tests are run."""
        # Initialize FastAPI test client
        # Import app from main since it's at the root level
        from main import app
        cls.app = app  # Save the app as a class attribute
        cls.client = TestClient(app)
        
        # Initialize Supabase client for test data setup/teardown
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        supabase_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not all([supabase_url, supabase_key]):
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")
        
        # Use service role key if available, otherwise use the regular key
        supabase_key = supabase_service_role_key or supabase_key
        cls.supabase = create_client(supabase_url, supabase_key)
        
        # Try to get an existing region
        try:
            response = cls.supabase.table("regions").select("id").limit(1).execute()
            if hasattr(response, 'data') and response.data:
                cls.test_region_id = response.data[0]['id']
                print(f"✅ Using existing region with ID: {cls.test_region_id}")
            else:
                # If no regions exist, we'll use None and the test will handle it
                cls.test_region_id = None
                print("⚠️  No regions found in the database. Tests will use null region_id.")
        except Exception as e:
            print(f"❌ Error checking for regions: {e}")
            cls.test_region_id = None
            
        # For testing with service role key, we don't need to create a test user
        # as we'll be using the service role key for authentication
        cls.test_user_id = str(uuid.uuid4())  # Generate a random UUID for the test user
        print(f"✅ Using service role key for testing with user ID: {cls.test_user_id}")
        
        # Set up the authenticated client with the service role key
        cls.authenticated_client = TestClient(
            cls.app,
            headers={"Authorization": f"Bearer {supabase_key}"}
        )
        
    @classmethod
    def tearDownClass(cls):
        """Clean up test data after all tests have run."""
        try:
            # Delete any test players that were created
            if hasattr(cls, 'test_data') and 'player' in cls.test_data:
                player_id = cls.test_data['player'].get('id')
                if player_id:
                    response = cls.client.delete(f"/api/players/{player_id}")
                    if response.status_code == 200:
                        print(f"✅ Cleaned up test player: {player_id}")
                    else:
                        print(f"⚠️  Failed to clean up test player {player_id}: {response.text}")
            
            # Delete test user
            if hasattr(cls, 'test_user') and cls.test_user:
                try:
                    # This would require admin privileges in a real scenario
                    print(f"⚠️  Test user {cls.test_user['email']} was not deleted (requires admin)")
                except Exception as e:
                    print(f"⚠️  Error cleaning up test user: {e}")
            
            # Delete test region
            if hasattr(cls, 'test_region_id') and cls.test_region_id:
                try:
                    # This would require proper foreign key handling in a real scenario
                    print(f"⚠️  Test region {cls.test_region_id} was not deleted (requires proper cleanup)")
                except Exception as e:
                    print(f"⚠️  Error cleaning up test region: {e}")
                    
        except Exception as e:
            print(f"⚠️  Error during test teardown: {e}")
    
    def setUp(self):
        """Set up test data before each test method."""
        # Reset test data for this test
        self.test_data = {}
    
    def tearDown(self):
        """Clean up after each test method."""
        # Clean up any test players created during this test
        if hasattr(self, 'test_data') and 'player' in self.test_data:
            player_id = self.test_data['player'].get('id')
            if player_id:
                try:
                    response = self.client.delete(f"/api/players/{player_id}")
                    if response.status_code == 200:
                        print(f"✅ Cleaned up test player: {player_id}")
                    else:
                        print(f"⚠️  Failed to clean up test player {player_id}: {response.text}")
                except Exception as e:
                    print(f"⚠️  Error cleaning up test player: {e}")
    
    def test_create_and_get_player(self):
        """Test creating and retrieving a player with all fields"""
        print("\n🚀 Testing Player Endpoints - Full Player")
        
        # Create test data with all fields
        test_player = create_test_player_data(
            region_id=self.test_region_id,
            include_optional=True,
            user_id=str(self.test_user.id)  # Convert UUID to string if needed
        )
        
        try:
            # Test CREATE via API
            print("\n🆕 Testing POST /api/players/ with all fields...")
            response = self.client.post("/api/players/", json=test_player)
            assert response.status_code == status.HTTP_201_CREATED, \
                f"Failed to create player: {response.text}"
            created_player = response.json()
            player_id = created_player["id"]
            self.test_data["player"] = created_player
            print(f"✅ Created player: {created_player['gamertag']} (ID: {player_id})")
            
            # Test GET by ID
            print(f"\n🔍 Testing GET /api/players/{player_id}...")
            response = self.client.get(f"/api/players/{player_id}")
            assert response.status_code == status.HTTP_200_OK, \
                f"Failed to get player: {response.text}"
            fetched_player = response.json()
            print(f"✅ Retrieved player: {fetched_player['gamertag']}")
            
            # Verify all required fields are present and match
            required_fields = ["gamertag", "user_id", "region_id"]
            for field in required_fields:
                assert field in fetched_player, f"Missing required field in response: {field}"
                assert str(fetched_player[field]) == str(test_player[field]), \
                    f"Mismatch in field {field}: {fetched_player[field]} != {test_player[field]}"
            
            # Verify optional fields if they were included
            if "team_name" in test_player:
                self.assertEqual(fetched_player.get("team_name"), test_player["team_name"])
            
            fetched_player = response.json()
            print(f"✅ Fetched player: {fetched_player['gamertag']}")
            
            # Verify the fetched player matches the created player
            self.assertEqual(fetched_player["id"], created_player["id"])
            self.assertEqual(fetched_player["gamertag"], created_player["gamertag"])
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            raise
    
    def test_create_minimal_player(self):
        """Test creating a player with only required fields"""
        # Create test player data with only required fields
        test_player = create_test_player_data(
            region_id=self.test_region_id,
            include_optional=False
        )
        
        try:
            print("\n🆕 Testing CREATE minimal player...")
            response = self.client.post("/api/players/", json=test_player)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                          f"Failed to create minimal player: {response.text}")
            
            created_player = response.json()
            self.test_data["player"] = created_player
            print(f"✅ Created minimal player: {created_player['gamertag']}")
            
            # Verify the response contains the created player data
            self.assertEqual(created_player["gamertag"], test_player["gamertag"])
            self.assertEqual(created_player["region_id"], str(test_player["region_id"]))
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            raise
    
    @pytest.mark.parametrize("region_id", [
        None,  # Test with null region_id
        "11111111-1111-1111-1111-111111111111",
        "22222222-2222-2222-2222-222222222222"
    ])
    def test_player_regions(self, region_id: str):
        """Test creating players with different region IDs"""
        # Create test player data with the specified region_id
        test_player = create_test_player_data(
            region_id=region_id,
            include_optional=True
        )
        
        try:
            print(f"\n🌍 Testing player with region_id: {region_id}")
            response = self.client.post("/api/players/", json=test_player)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                          f"Failed to create player with region_id {region_id}: {response.text}")
            
            created_player = response.json()
            self.test_data["player"] = created_player
            print(f"✅ Created player with region_id: {created_player.get('region_id')}")
            
            # Verify the region_id was set correctly
            self.assertEqual(created_player.get("region_id"), region_id)
            
        except Exception as e:
            print(f"❌ Test failed for region_id {region_id}: {str(e)}")
            raise
    
    @pytest.mark.parametrize("salary_tier", ["S", "A", "B", "C", "D"])
    @parameterized.expand([
        ("S",),
        ("A",),
        ("B",),
        ("C",),
        ("D",)
    ])
    @pytest.mark.parametrize("salary_tier", ["S", "A", "B", "C", "D"])
    def test_player_salary_tiers(self, salary_tier: str):
        """Test creating players with all possible salary tier values"""
        test_player = create_test_player_data(
            region_id=self.test_region_id,
            include_optional=True
        )
        # Override the salary tier
        test_player["salary_tier"] = salary_tier
        
        try:
            response = self.authenticated_client.post("/api/players/", json=test_player)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                          f"Failed to create player with salary tier {salary_tier}: {response.text}")
            
            created_player = response.json()
            self.test_data[f"player_tier_{salary_tier}"] = created_player
            print(f"✅ Created player with salary tier {salary_tier}")
            
            # Verify the salary tier was saved correctly
            self.assertEqual(created_player["salary_tier"], salary_tier)
            
            # Clean up
            if created_player.get('id'):
                cleanup_response = self.authenticated_client.delete(f"/api/players/{created_player['id']}")
                if cleanup_response.status_code == 200:
                    print(f"✅ Cleaned up test player with tier {salary_tier}")
            
        except Exception as e:
            print(f"❌ Test failed for salary tier {salary_tier}: {str(e)}")
            raise
    
    @pytest.mark.parametrize("position", [
        "Point Guard",
        "Shooting Guard",
        "Lock",
        "Power Forward",
        "Center"
    ])
    @parameterized.expand([
        ("Point Guard",),
        ("Shooting Guard",),
        ("Small Forward",),
        ("Power Forward",),
        ("Center",)
    ])
    def test_player_positions(self, position: str):
        """Test creating players with all possible position values"""
        test_player = create_test_player_data(
            region_id=self.test_region_id,
            include_optional=True
        )
        # Override the position
        test_player["position"] = position
        
        try:
            response = self.authenticated_client.post("/api/players/", json=test_player)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                          f"Failed to create player with position {position}: {response.text}")
            
            created_player = response.json()
            self.test_data[f"player_{position}"] = created_player
            print(f"✅ Created player with position {position}")
            
            # Verify the position was saved correctly
            self.assertEqual(created_player["position"], position)
            
            # Clean up
            if created_player.get('id'):
                cleanup_response = self.authenticated_client.delete(f"/api/players/{created_player['id']}")
                if cleanup_response.status_code == 200:
                    print(f"✅ Cleaned up test player with position {position}")
            
        except Exception as e:
            print(f"❌ Test failed for position {position}: {str(e)}")
            raise
    
    def test_update_player(self):
        """Test updating a player"""
        # First create a test player
        test_player = create_test_player_data(
            region_id=self.test_region_id,
            include_optional=True
        )
        
        try:
            # Create the player
            response = self.client.post("/api/players/", json=test_player)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                          f"Failed to create player: {response.text}")
            
            created_player = response.json()
            player_id = created_player["id"]
            self.test_data["player"] = created_player
            
            # Update the player
            print("\n🔄 Testing UPDATE player...")
            update_data = {
                "player_rp": 1500,
                "position": "Shooting Guard",
                "performance_score": 85.5
            }
            
            response = self.client.put(f"/api/players/{player_id}", json=update_data)
            self.assertEqual(response.status_code, status.HTTP_200_OK,
                          f"Failed to update player: {response.text}")
            
            updated_player = response.json()
            self.assertEqual(updated_player["player_rp"], 1500)
            self.assertEqual(updated_player["position"], "Shooting Guard")
            self.assertEqual(updated_player["performance_score"], 85.5)
            
            print(f"✅ Successfully updated player: {player_id}")
            
            # Test updating with invalid data
            print("\n🧪 Testing update with invalid data...")
            invalid_updates = [
                ({"id": "new-id-123"}, "id should not be updatable"),
                ({"created_at": "2023-01-01T00:00:00"}, "created_at should not be updatable")
            ]
            
            for update_data, error_msg in invalid_updates:
                response = self.client.put(f"/api/players/{player_id}", json=update_data)
                self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY],
                           f"Should not allow {error_msg}: {response.text}")
            
            print("✅ Invalid update attempts handled correctly")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            raise

    def test_delete_player(self):
        """Test deleting a player"""
        # First create a test player
        test_player = create_test_player_data(
            region_id=self.test_region_id,
            include_optional=False
        )
        
        try:
            # Create the player
            response = self.client.post("/api/players/", json=test_player)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                          f"Failed to create player: {response.text}")
            
            created_player = response.json()
            player_id = created_player["id"]
            self.test_data["player"] = created_player
            
            # Delete the player
            print("\n🗑️  Testing player deletion...")
            response = self.client.delete(f"/api/players/{player_id}")
            self.assertEqual(response.status_code, status.HTTP_200_OK,
                          f"Failed to delete player: {response.text}")
            
            # Verify the player was deleted
            response = self.client.get(f"/api/players/{player_id}")
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND,
                          "Player should be deleted but still exists")
            
            print(f"✅ Successfully deleted player: {player_id}")
            
            # Test deleting a non-existent player
            print("\n🧪 Testing deletion of non-existent player...")
            non_existent_id = "00000000-0000-0000-0000-000000000000"
            response = self.client.delete(f"/api/players/{non_existent_id}")
            # Should return 200 or 404 depending on implementation
            self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND],
                        f"Unexpected status code for non-existent player: {response.status_code}")
            
            print("✅ Non-existent player deletion handled correctly")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            raise
