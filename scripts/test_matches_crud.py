"""
Comprehensive test script for Matches CRUD operations with Supabase
"""
import os
import uuid
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from supabase import create_client
from typing import Dict, Any, Optional, Tuple

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

def get_or_create_test_region() -> str:
    """Get an existing region ID or create a test region"""
    # First, try to get an existing region
    response = supabase.table("regions").select("id").limit(1).execute()
    if hasattr(response, 'data') and response.data:
        return response.data[0]['id']
    
    # If no regions exist, create a test region
    region_data = {
        "id": str(uuid.uuid4()),
        "name": "Test Region",
        "code": "test-region"
    }
    response = supabase.table("regions").insert(region_data).execute()
    if hasattr(response, 'data') and response.data:
        return response.data[0]['id']
    
    raise Exception("Failed to get or create a test region")

def create_test_teams() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Create two test teams for the match"""
    region_id = get_or_create_test_region()
    
    team1_data = {
        "id": str(uuid.uuid4()),
        "name": f"Team Alpha {str(uuid.uuid4())[:8]}",
        "region_id": region_id,
        "logo_url": "https://example.com/team1.png",
        "current_rp": 1000,
        "elo_rating": 1500,
        "global_rank": 1,
        "leaderboard_tier": 1,
        "player_rank_score": 85.5,
        "money_won": 0
    }
    
    team2_data = {
        "id": str(uuid.uuid4()),
        "name": f"Team Beta {str(uuid.uuid4())[:8]}",
        "region_id": region_id,
        "logo_url": "https://example.com/team2.png",
        "current_rp": 900,
        "elo_rating": 1450,
        "global_rank": 2,
        "leaderboard_tier": 1,
        "player_rank_score": 82.0,
        "money_won": 0
    }
    
    # Insert teams
    supabase.table("teams").insert([team1_data, team2_data]).execute()
    return team1_data, team2_data

def create_test_event() -> Dict[str, Any]:
    """Create a test event for the match"""
    region_id = get_or_create_test_region()
    event_data = {
        "id": str(uuid.uuid4()),
        "name": f"Test Event {str(uuid.uuid4())[:8]}",
        "type": "tournament",
        "is_global": False,
        "region_id": region_id,
        "start_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "end_date": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        "status": "upcoming",
        "tier": "T1"
    }
    
    # Insert event
    supabase.table("events").insert(event_data).execute()
    return event_data

def create_test_match_data(team1_id: str, team2_id: str, event_id: str) -> Dict[str, Any]:
    """Create test match data that matches the actual schema"""
    now = datetime.now(timezone.utc)
    
    # Get team names for reference
    team1 = supabase.table("teams").select("name").eq("id", team1_id).execute()
    team2 = supabase.table("teams").select("name").eq("id", team2_id).execute()
    
    team1_name = team1.data[0]["name"] if hasattr(team1, 'data') and team1.data else f"Team {team1_id[:8]}"
    team2_name = team2.data[0]["name"] if hasattr(team2, 'data') and team2.data else f"Team {team2_id[:8]}"
    
    return {
        "id": str(uuid.uuid4()),
        "event_id": event_id,
        "team_a_id": team1_id,
        "team_b_id": team2_id,
        "team_a_name": team1_name,
        "team_b_name": team2_name,
        "stage": "Group Play",
        "game_number": 1,
        "score_a": 0,
        "score_b": 0,
        "played_at": now.isoformat(),
        "boxscore_url": "https://example.com/boxscore"
    }

def test_matches_crud():
    """Test all CRUD operations for the matches table"""
    print("🚀 Testing Matches Table Operations")
    
    # Create test data
    team1, team2 = create_test_teams()
    event = create_test_event()
    test_match = create_test_match_data(team1["id"], team2["id"], event["id"])
    match_id = test_match["id"]
    
    try:
        # Test CREATE
        print("\n🆕 Testing CREATE match...")
        response = supabase.table("matches").insert(test_match).execute()
        if hasattr(response, 'data') and response.data:
            created_match = response.data[0]
            print(f"✅ Created match: {team1['name']} vs {team2['name']} (ID: {created_match['id']})")
        else:
            raise Exception("Failed to create match: No data in response")
        
        # Test READ
        print("\n📖 Testing GET match...")
        response = supabase.table("matches").select("*").eq("id", match_id).execute()
        if hasattr(response, 'data') and response.data:
            fetched_match = response.data[0]
            print(f"✅ Fetched match: {fetched_match['id']}")
        else:
            raise Exception("Failed to fetch match: Match not found")
        
        # Test UPDATE
        print("\n🔄 Testing UPDATE match...")
        update_data = {
            "score_a": 1,
            "score_b": 0,
            "winner_id": team1["id"],
            "winner_name": team1["name"]
        }
        response = supabase.table("matches").update(update_data).eq("id", match_id).execute()
        if hasattr(response, 'data') and response.data:
            updated_match = response.data[0]
            assert updated_match["score_a"] == 1 and updated_match["score_b"] == 0, "Failed to update match scores"
            print(f"✅ Updated match: Score: {updated_match['score_a']}-{updated_match['score_b']}, "
                  f"Winner: {updated_match['winner_name']}")
        else:
            raise Exception("Failed to update match: No data in response")
        
        # Test QUERY with filters
        print("\n🔍 Testing QUERY matches...")
        response = supabase.table("matches") \
                         .select("*") \
                         .eq("event_id", event["id"]) \
                         .limit(5) \
                         .execute()
        matches = response.data if hasattr(response, 'data') else []
        print(f"✅ Found {len(matches)} matches for event {event['name']}")
        
        # Test DELETE
        print("\n🗑️  Testing DELETE match...")
        response = supabase.table("matches").delete().eq("id", match_id).execute()
        if hasattr(response, 'data') and response.data:
            print("✅ Delete successful")
        else:
            raise Exception("Failed to delete match: No data in response")
        
        # Verify deletion
        response = supabase.table("matches").select("*").eq("id", match_id).execute()
        if hasattr(response, 'data') and response.data:
            print("❌ Match was not deleted successfully")
        else:
            print("✅ Match was deleted successfully")
        
        print("\n🎉 All match operations tested successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during match operations: {str(e)}")
        # Try to clean up if something went wrong
        try:
            supabase.table("matches").delete().eq("id", match_id).execute()
        except Exception as cleanup_error:
            print(f"⚠️  Cleanup error: {cleanup_error}")
        raise  # Re-raise the original error
    finally:
        # Clean up test data
        try:
            supabase.table("teams").delete().in_("id", [team1["id"], team2["id"]]).execute()
            supabase.table("events").delete().eq("id", event["id"]).execute()
        except Exception as cleanup_error:
            print(f"⚠️  Cleanup error: {cleanup_error}")

if __name__ == "__main__":
    # Check if Supabase credentials are set
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    else:
        test_matches_crud()
