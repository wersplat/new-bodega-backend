"""
Test script to verify Supabase operations with the players table
"""
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from app.core.supabase import supabase

# Load environment variables
load_dotenv()

def test_players_crud():
    print("🚀 Testing Players Table Operations")
    
    # Test data for a player
    player_id = str(uuid.uuid4())
    player_data = {
        "id": player_id,
        "name": "Test Player",
        "position": "Point Guard",
        "created_at": datetime.utcnow().isoformat(),
        "is_active": True,
        # Add other required fields from your schema
        "rp_balance": 1000,
        "team_id": None,  # Set to an existing team ID if required
        "discord_id": f"test_discord_{player_id[:8]}",
        "email": f"test_{player_id[:8]}@example.com"
    }
    
    try:
        # Test CREATE
        print("\n🆕 Testing CREATE player...")
        created_player = supabase.insert("players", player_data)
        print(f"✅ Created player: {created_player['name']} (ID: {created_player['id']})")
        
        # Test READ
        print("\n📖 Testing GET player...")
        fetched_player = supabase.fetch_by_id("players", player_id)
        print(f"✅ Fetched player: {fetched_player['name']}")
        
        # Test UPDATE
        print("\n🔄 Testing UPDATE player...")
        update_data = {"rp_balance": 1500, "position": "Shooting Guard"}
        updated_player = supabase.update("players", player_id, update_data)
        print(f"✅ Updated player RP: {updated_player['rp_balance']}")
        
        # Test QUERY with filters
        print("\n🔍 Testing QUERY players...")
        players = supabase.get_players_by_team(None)  # Or pass a team_id if needed
        print(f"✅ Found {len(players)} players in the database")
        
        # Test DELETE (optional - comment out if you want to keep test data)
        print("\n🗑️  Testing DELETE player...")
        delete_result = supabase.delete("players", player_id)
        print(f"✅ Delete successful: {delete_result}")
        
        print("\n🎉 All player operations tested successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during player operations: {str(e)}")
        raise

if __name__ == "__main__":
    # Check if Supabase credentials are set
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    else:
        test_players_crud()
