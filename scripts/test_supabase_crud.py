"""
Test script to verify Supabase CRUD operations using the player_stats table
"""
import os
import uuid
from datetime import datetime, timezone
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

def create_test_player(player_id):
    """Helper function to create a test player"""
    player_data = {
        "id": player_id,
        "gamertag": f"TestPlayer_{player_id[:8]}",
        "position": "Point Guard",
        "performance_score": 0,
        "player_rp": 1000,
        "player_rank_score": 0,
        "salary_tier": "B",
        "monthly_value": 0,
        "is_rookie": True,
        "discord_id": f"test_discord_{player_id[:8]}",
        "twitter_id": f"test_twitter_{player_id[:8]}"
    }
    response = supabase.table("players").insert(player_data).execute()
    if not (hasattr(response, 'data') and response.data):
        raise Exception(f"Failed to create test player: {response}")
    return response.data[0]

def create_test_team(team_id):
    """Helper function to create a test team"""
    team_data = {
        "id": team_id,
        "name": f"Test Team {team_id[:8]}",
        "logo_url": "https://example.com/logo.png",
        "current_rp": 1000,
        "elo_rating": 1500,
        "global_rank": 1,
        "leaderboard_tier": 1,
        "player_rank_score": 0,
        "money_won": 0
    }
    response = supabase.table("teams").insert(team_data).execute()
    if not (hasattr(response, 'data') and response.data):
        raise Exception(f"Failed to create test team: {response}")
    return response.data[0]

def create_test_event(event_id):
    """Helper function to create a test event"""
    event_data = {
        "id": event_id,
        "name": "Test Event",
        "type": "tournament",
        "is_global": False,
        "start_date": "2025-01-01T00:00:00Z",
        "end_date": "2025-12-31T23:59:59Z",
        "status": "upcoming",
        "tier": "T1"  # Using T1 as a valid tier value (other options: T2, T3)
    }
    response = supabase.table("events").insert(event_data).execute()
    if not (hasattr(response, 'data') and response.data):
        raise Exception(f"Failed to create test event: {response}")
    return response.data[0]

def create_test_match(match_id, event_id, team_a, team_b):
    """Helper function to create a test match
    
    Args:
        match_id: UUID for the new match
        event_id: UUID of the event this match belongs to
        team_a: Dictionary containing team A data (must include 'id' and 'name')
        team_b: Dictionary containing team B data (must include 'id' and 'name')
    """
    match_data = {
        "id": match_id,
        "event_id": event_id,
        "team_a_id": team_a['id'],
        "team_b_id": team_b['id'],
        "team_a_name": team_a['name'],
        "team_b_name": team_b['name'],
        "score_a": 0,
        "score_b": 0,
        "stage": "Group Play",
        "game_number": 1
    }
    response = supabase.table("matches").insert(match_data).execute()
    if not (hasattr(response, 'data') and response.data):
        raise Exception(f"Failed to create test match: {response}")
    return response.data[0]

def test_crud_operations():
    print("🚀 Testing Supabase CRUD Operations with player_stats table")
    
    # Generate test IDs
    test_id = str(uuid.uuid4())
    player_id = str(uuid.uuid4())
    team_a_id = str(uuid.uuid4())
    team_b_id = str(uuid.uuid4())
    match_id = str(uuid.uuid4())
    event_id = str(uuid.uuid4())
    
    try:
        # Create required related records first
        print("\n🔄 Creating test data for foreign key constraints...")
        event = create_test_event(event_id)
        player = create_test_player(player_id)
        team_a = create_test_team(team_a_id)
        team_b = create_test_team(team_b_id)
        match_data = create_test_match(match_id, event_id, team_a, team_b)
        
        print("✅ Successfully created test data")
        
        # Test data for player_stats
        test_data = {
            "id": test_id,
            "player_id": player_id,
            "match_id": match_id,
            "team_id": team_a_id,  # Player is on team A
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
            "player_name": player["gamertag"]
        }
        
        # Test CREATE
        print("\n🆕 Testing CREATE operation...")
        response = supabase.table("player_stats").insert(test_data).execute()
        if hasattr(response, 'data') and response.data:
            created_item = response.data[0]
            print(f"✅ Created player stats with ID: {created_item['id']}")
        else:
            raise Exception("Failed to create player stats: No data in response")
            
        # Test READ
        print("\n📖 Testing READ operation...")
        response = supabase.table("player_stats").select("*").eq("id", test_id).execute()
        if hasattr(response, 'data') and response.data:
            fetched_item = response.data[0]
            assert fetched_item["points"] == 15, "Points don't match"
            print(f"✅ Fetched player stats for player: {fetched_item['player_name']}")
        else:
            raise Exception("Failed to fetch player stats: Item not found")
            
        # Test UPDATE
        print("\n🔄 Testing UPDATE operation...")
        update_data = {
            "points": 22,
            "assists": 8,
            "rebounds": 10
        }
        response = supabase.table("player_stats").update(update_data).eq("id", test_id).execute()
        if hasattr(response, 'data') and response.data:
            updated_item = response.data[0]
            assert updated_item["points"] == 22, "Points update failed"
            print(f"✅ Updated player stats - New stats: {updated_item['points']} pts, {updated_item['assists']} ast, {updated_item['rebounds']} reb")
        else:
            raise Exception("Failed to update player stats: No data in response")
            
        # Verify update
        response = supabase.table("player_stats").select("*").eq("id", test_id).execute()
        if hasattr(response, 'data') and response.data:
            verified_item = response.data[0]
            assert verified_item["points"] == 22, "Update verification failed"
            
        # Test QUERY with filters
        print("\n🔍 Testing QUERY operation...")
        response = supabase.table("player_stats") \
                         .select("*") \
                         .eq("player_id", player_id) \
                         .execute()
        stats = response.data if hasattr(response, 'data') else []
        assert len(stats) > 0, "Query returned no results"
        print(f"✅ Found {len(stats)} stat entries for player {player_id}")
        
        # Test DELETE
        print("\n🗑️  Testing DELETE operation...")
        response = supabase.table("player_stats").delete().eq("id", test_id).execute()
        if hasattr(response, 'data') and response.data:
            print("✅ Delete successful")
        else:
            raise Exception("Failed to delete player stats")
        
        # Verify delete
        response = supabase.table("player_stats").select("*").eq("id", test_id).execute()
        if hasattr(response, 'data') and response.data and len(response.data) > 0:
            print("❌ Player stats were not deleted successfully")
        else:
            print("✅ Player stats were deleted successfully")
            
        print("\n🎉 All CRUD operations tested successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during CRUD operations: {str(e)}")
        raise  # Re-raise the original error
    finally:
        # Clean up all test data
        print("\n🧹 Cleaning up test data...")
        try:
            # Delete player stats
            supabase.table("player_stats").delete().eq("id", test_id).execute()
            # Delete match
            supabase.table("matches").delete().eq("id", match_id).execute()
            # Delete player
            supabase.table("players").delete().eq("id", player_id).execute()
            # Delete teams
            supabase.table("teams").delete().eq("id", team_a_id).execute()
            supabase.table("teams").delete().eq("id", team_b_id).execute()
            print("✅ Test data cleaned up")
        except Exception as cleanup_error:
            print(f"⚠️ Error during cleanup: {cleanup_error}")

if __name__ == "__main__":
    # Check if Supabase credentials are set
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    else:
        test_crud_operations()
