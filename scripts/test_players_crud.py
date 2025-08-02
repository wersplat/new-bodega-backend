"""
Test script to verify Supabase operations with the players table
"""
import os
import uuid
import pytest
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

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

def test_players_crud():
    print("🚀 Testing Players Table Operations")
    
    # Test data for a player - aligned with actual schema
    player_id = str(uuid.uuid4())
    player_data = {
        "id": player_id,
        "gamertag": f"TestPlayer_{player_id[:8]}",  # Required field
        "position": "Point Guard",  # Must use one of the enum values: "Point Guard", "Shooting Guard", "Lock", "Power Forward", "Center"
        "region_id": None,  # Making this optional since we don't have regions in the test DB
        "current_team_id": None,  # Can be None for free agents
        "performance_score": 0,  # Initialize to 0
        "player_rp": 1000,  # Using correct field name for RP
        "player_rank_score": 0,  # Initialize to 0
        "salary_tier": "B",  # Must be one of: "S", "A", "B", "C", "D"
        "monthly_value": 0,  # Initialize to 0
        "created_at": datetime.utcnow().isoformat(),
        "is_rookie": True,  # Default to true for new players
        "discord_id": f"test_discord_{player_id[:8]}",
        "twitter_id": f"test_twitter_{player_id[:8]}",
        "alternate_gamertag": None  # Optional field
    }
    
    try:
        # Test CREATE
        print("\n🆕 Testing CREATE player...")
        response = supabase.table("players").insert(player_data).execute()
        if hasattr(response, 'data') and response.data:
            created_player = response.data[0]
        print(f"✅ Created player: {created_player['gamertag']} (ID: {created_player['id']})")
        
        # Test READ
        print("\n📖 Testing GET player...")
        fetched_player = supabase.fetch_by_id("players", player_id)
        assert fetched_player is not None, "Failed to fetch player"
        print(f"✅ Fetched player: {fetched_player['gamertag']}")
        
        # Test UPDATE
        print("\n🔄 Testing UPDATE player...")
        update_data = {
            "player_rp": 1500,  # Using correct field name
            "position": "SG",  # Updating position
            "performance_score": 85  # Adding performance score
        }
        updated_player = supabase.update("players", player_id, update_data)
        assert updated_player["player_rp"] == 1500, "Failed to update player RP"
        print(f"✅ Updated player RP: {updated_player['player_rp']}")
        
        # Test QUERY
        print("\n🔍 Testing QUERY players...")
        # Assuming get_players_by_team is a custom method in your supabase client
        # If not, you might need to implement it or use a different query method
        players = supabase.client.table("players").select("*").execute()
        print(f"✅ Found {len(players.data)} players in the database")
        
        # Test DELETE
        print("\n🗑️  Testing DELETE player...")
        delete_result = supabase.delete("players", player_id)
        assert delete_result is not None, "Failed to delete player"
        print("✅ Delete successful")
        
        # Verify deletion
        deleted_player = supabase.fetch_by_id("players", player_id)
        assert deleted_player is None, "Player was not deleted successfully"
        
        print("\n🎉 All player operations tested successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during player operations: {str(e)}")
        # Try to clean up if something went wrong
        try:
            supabase.delete("players", player_id)
        except:
            pass
        raise

if __name__ == "__main__":
    # Check if Supabase credentials are set
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    else:
        test_players_crud()
