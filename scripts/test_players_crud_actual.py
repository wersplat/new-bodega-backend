"""
Comprehensive test script for Player CRUD operations with Supabase
"""
import os
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY]):
    raise ValueError("Missing required Supabase environment variables")

# Use service role key if available, otherwise use the regular key
supabase_key = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY

# Create a Supabase client with the appropriate key
supabase = create_client(SUPABASE_URL, supabase_key)

def get_existing_region_id() -> Optional[str]:
    """Try to get an existing region_id from the database"""
    try:
        response = supabase.table("regions").select("id").limit(1).execute()
        if hasattr(response, 'data') and response.data:
            return response.data[0]['id']
        return None
    except Exception as e:
        print(f"⚠️  Could not fetch regions: {str(e)}")
        return None

def create_test_player_data() -> Optional[Dict[str, Any]]:
    """Create test player data that matches the actual schema"""
    # Try to get an existing region_id
    region_id = get_existing_region_id()
    if not region_id:
        print("⚠️  No regions found in the database. Creating player with null region_id.")
    
    player_id = str(uuid.uuid4())
    return {
        "id": player_id,
        "gamertag": f"testplayer_{player_id[:8]}",
        "position": "Point Guard",  # Must be one of: "Point Guard", "Shooting Guard", "Lock", "Power Forward", "Center"
        "region_id": region_id,  # Can be None
        "current_team_id": None,  # Can be set to None or a valid team_id (as UUID string)
        "performance_score": 75.5,
        "player_rp": 1000,
        "player_rank_score": 1500,
        "salary_tier": "B",  # Must be one of: "S", "A", "B", "C", "D"
        "monthly_value": 5000,
        "is_rookie": True,
        "discord_id": f"test_discord_{player_id[:8]}",
        "twitter_id": f"test_twitter_{player_id[:8]}",
        "alternate_gamertag": f"alt_{player_id[:8]}",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

def test_players_crud():
    """Test all CRUD operations for the players table"""
    print("🚀 Testing Players Table Operations")
    
    # Create test data
    test_player = create_test_player_data()
    if not test_player:
        print("❌ Test setup failed: Could not create test player data")
        return
        
    player_id = test_player["id"]
    
    try:
        # Test CREATE
        print("\n🆕 Testing CREATE player...")
        response = supabase.table("players").insert(test_player).execute()
        if hasattr(response, 'data') and response.data:
            created_player = response.data[0]
            print(f"✅ Created player: {created_player['gamertag']} (ID: {created_player['id']})")
        else:
            raise Exception("Failed to create player: No data in response")
        
        # Test READ
        print("\n📖 Testing GET player...")
        response = supabase.table("players").select("*").eq("id", player_id).execute()
        if hasattr(response, 'data') and response.data:
            fetched_player = response.data[0]
            print(f"✅ Fetched player: {fetched_player['gamertag']}")
        else:
            raise Exception("Failed to fetch player: Player not found")
        
        # Test UPDATE
        print("\n🔄 Testing UPDATE player...")
        update_data = {
            "player_rp": 1500,
            "position": "Shooting Guard",  # Using full position name
            "performance_score": 85
        }
        response = supabase.table("players").update(update_data).eq("id", player_id).execute()
        if hasattr(response, 'data') and response.data:
            updated_player = response.data[0]
            assert updated_player["player_rp"] == 1500, "Failed to update player RP"
            print(f"✅ Updated player RP: {updated_player['player_rp']}")
        else:
            raise Exception("Failed to update player: No data in response")
        
        # Test QUERY with filters
        print("\n🔍 Testing QUERY players...")
        response = supabase.table("players") \
                         .select("*") \
                         .eq("position", "Shooting Guard") \
                         .limit(5) \
                         .execute()
        players = response.data if hasattr(response, 'data') else []
        print(f"✅ Found {len(players)} shooting guards in the database")
        
        # Test DELETE
        print("\n🗑️  Testing DELETE player...")
        response = supabase.table("players").delete().eq("id", player_id).execute()
        if hasattr(response, 'data') and response.data:
            print("✅ Delete successful")
        else:
            raise Exception("Failed to delete player")
        
        # Verify deletion
        response = supabase.table("players").select("*").eq("id", player_id).execute()
        if hasattr(response, 'data') and response.data:
            print("❌ Player was not deleted successfully")
        else:
            print("✅ Player was deleted successfully")
        
        print("\n🎉 All player operations tested successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during player operations: {str(e)}")
        # Try to clean up if something went wrong
        try:
            supabase.table("players").delete().eq("id", player_id).execute()
        except Exception as cleanup_error:
            print(f"⚠️  Cleanup error: {cleanup_error}")
        raise  # Re-raise the original error

if __name__ == "__main__":
    # Check if Supabase credentials are set
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    else:
        test_players_crud()
