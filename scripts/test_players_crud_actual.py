"""
Test script to verify Supabase operations with the players table
"""
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from app.core.supabase import supabase
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()

def get_existing_region_id() -> Optional[str]:
    """Try to get an existing region_id from the database"""
    try:
        client = supabase.get_client()
        # Try to get one region
        response = client.table("regions").select("id").limit(1).execute()
        if hasattr(response, 'data') and response.data:
            return response.data[0]['id']
        return None
    except Exception as e:
        print(f"⚠️  Could not fetch regions: {str(e)}")
        return None

def create_test_player() -> Optional[Dict[str, Any]]:
    """Create test player data that matches the actual schema"""
    # Try to get an existing region_id
    region_id = get_existing_region_id()
    if not region_id:
        print("⚠️  No regions found in the database. Cannot create test player.")
        print("     Please create at least one region first.")
        return None
    
    player_id = str(uuid.uuid4())
    return {
        "id": player_id,
        "gamertag": f"testplayer_{player_id[:8]}",
        "position": "Point Guard",
        "region_id": region_id,  # Use existing region_id
        "current_team_id": None,  # Can be set to None or a valid team_id (as UUID string)
        "performance_score": 75.5,
        "player_rp": 1000,
        "player_rank_score": 1500,
        "salary_tier": "B",
        "monthly_value": 5000,
        "created_at": datetime.utcnow().isoformat(),
        "is_rookie": True,
        "discord_id": f"test_discord_{player_id[:8]}",
        "twitter_id": f"test_twitter_{player_id[:8]}",
        "alternate_gamertag": f"alt_{player_id[:8]}"
    }

def test_players_crud():
    print("🚀 Testing Players Table Operations")
    
    # Create test data
    test_player = create_test_player()
    if not test_player:
        print("❌ Test skipped: Could not create test player (missing required data)")
        return
        
    player_id = test_player["id"]
    
    try:
        # Test CREATE
        print("\n🆕 Testing CREATE player...")
        created_player = supabase.insert("players", test_player)
        print(f"✅ Created player: {created_player['gamertag']} (ID: {created_player['id']})")
        
        # Test READ
        print("\n📖 Testing GET player...")
        fetched_player = supabase.fetch_by_id("players", player_id)
        print(f"✅ Fetched player: {fetched_player['gamertag']}")
        
        # Test UPDATE
        print("\n🔄 Testing UPDATE player...")
        update_data = {
            "performance_score": 80.0,
            "player_rp": 1200,
            "salary_tier": "A"
        }
        updated_player = supabase.update("players", player_id, update_data)
        print(f"✅ Updated player - New RP: {updated_player['player_rp']}, "
              f"Tier: {updated_player['salary_tier']}")
        
        # Test QUERY with filters
        print("\n🔍 Testing QUERY players...")
        client = supabase.get_client()
        response = client.table("players") \
                       .select("*") \
                       .eq("position", "Point Guard") \
                       .limit(5) \
                       .execute()
        players = response.data if hasattr(response, 'data') else []
        print(f"✅ Found {len(players)} point guards in the database")
        
        # Test DELETE (optional - comment out if you want to keep test data)
        print("\n🗑️  Testing DELETE player...")
        delete_result = supabase.delete("players", player_id)
        print(f"✅ Delete successful: {delete_result}")
        
        # Verify delete
        deleted_player = supabase.fetch_by_id("players", player_id)
        assert deleted_player is None, "Delete verification failed"
        
        print("\n🎉 All player operations tested successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during player operations: {str(e)}")
        # Clean up if something went wrong
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
