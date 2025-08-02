"""
Test script to verify Supabase CRUD operations using the player_stats table
"""
import os
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
from app.core.supabase import supabase

# Load environment variables
load_dotenv()

def test_crud_operations():
    print("🚀 Testing Supabase CRUD Operations with player_stats table")
    
    # Using player_stats table for testing CRUD operations
    table = "player_stats"
    
    # Generate test data that matches the player_stats schema
    test_id = str(uuid.uuid4())
    player_id = str(uuid.uuid4())
    match_id = str(uuid.uuid4())
    team_id = str(uuid.uuid4())
    
    test_data = {
        "id": test_id,
        "player_id": player_id,
        "match_id": match_id,
        "team_id": team_id,
        "points": 15,
        "assists": 5,
        "rebounds": 8,
        "steals": 2,
        "blocks": 1,
        "turnovers": 3,
        "fouls": 2,
        "fgm": 6,
        "fga": 12,
        "three_points_made": 3,
        "three_points_attempted": 7,
        "ftm": 0,
        "fta": 0,
        "plus_minus": 10,
        "player_name": "Test Player",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ps": 18.5  # Performance score
    }
    
    try:
        # Test CREATE
        print("\n🆕 Testing CREATE operation...")
        created_item = supabase.insert(table, test_data)
        assert created_item is not None, "Failed to create player stats"
        print(f"✅ Created player stats with ID: {created_item['id']}")
        
        # Test READ
        print("\n📖 Testing READ operation...")
        fetched_item = supabase.fetch_by_id(table, test_id)
        assert fetched_item is not None, "Failed to fetch player stats"
        assert fetched_item["points"] == 15, "Points don't match"
        print(f"✅ Fetched player stats for player: {fetched_item['player_name']}")
        
        # Test UPDATE
        print("\n🔄 Testing UPDATE operation...")
        update_data = {
            "points": 22,
            "assists": 8,
            "rebounds": 10
        }
        updated_item = supabase.update(table, test_id, update_data)
        assert updated_item is not None, "Failed to update player stats"
        assert updated_item["points"] == 22, "Points update failed"
        print(f"✅ Updated player stats - New stats: {updated_item['points']} pts, {updated_item['assists']} ast, {updated_item['rebounds']} reb")
        
        # Verify update
        verified_item = supabase.fetch_by_id(table, test_id)
        assert verified_item["points"] == 22, "Update verification failed"
        
        # Test QUERY with filters
        print("\n🔍 Testing QUERY operation...")
        client = supabase.get_client()
        response = client.table(table) \
                       .select("*") \
                       .eq("player_id", player_id) \
                       .execute()
        stats = response.data if hasattr(response, 'data') else []
        assert len(stats) > 0, "Query returned no results"
        print(f"✅ Found {len(stats)} stat entries for player {player_id}")
        
        # Test DELETE
        print("\n🗑️  Testing DELETE operation...")
        delete_result = supabase.delete(table, test_id)
        assert delete_result is not None, "Failed to delete player stats"
        print("✅ Delete successful")
        
        # Verify delete
        deleted_item = supabase.fetch_by_id(table, test_id)
        assert deleted_item is None, "Player stats were not deleted successfully"
        
        print("\n🎉 All CRUD operations tested successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during CRUD operations: {str(e)}")
        # Clean up if something went wrong
        try:
            supabase.delete(table, test_id)
        except:
            pass
        raise

if __name__ == "__main__":
    # Check if Supabase credentials are set
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    else:
        test_crud_operations()
