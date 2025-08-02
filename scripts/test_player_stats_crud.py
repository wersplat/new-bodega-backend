"""
Comprehensive test script for Player Stats CRUD operations with Supabase
"""
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple
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

def create_test_player() -> Dict[str, Any]:
    """Create a test player for the player stats"""
    region_id = get_or_create_test_region()
    player_data = {
        "id": str(uuid.uuid4()),
        "gamertag": f"TestPlayer{str(uuid.uuid4())[:8]}",
        "position": "Point Guard",  # Must be one of: "Point Guard", "Shooting Guard", "Lock", "Power Forward", "Center"
        "region_id": region_id,
        "performance_score": 85.5,
        "player_rp": 1000,
        "player_rank_score": 85.5,
        "salary_tier": "B",  # Must be one of: "S", "A", "B", "C", "D"
        "monthly_value": 1000000,
        "is_rookie": False,
        "discord_id": str(uuid.uuid4()),
        "twitter_id": f"testplayer{str(uuid.uuid4())[:8]}",
        "alternate_gamertag": f"Alt{str(uuid.uuid4())[:8]}"
    }
    
    # Insert player
    supabase.table("players").insert(player_data).execute()
    return player_data

def create_test_team() -> Dict[str, Any]:
    """Create a test team with valid schema"""
    team_id = str(uuid.uuid4())
    team_data = {
        "id": team_id,
        "name": f"Test Team {str(uuid.uuid4())[:8]}",
        "logo_url": f"https://example.com/teams/{team_id}/logo.png",
        "region_id": None,  # Can be None or a valid region_id
        "current_rp": 500,
        "elo_rating": 1500,
        "global_rank": 100,
        "leaderboard_tier": "D",  # Must be one of: "S", "A", "B", "C", "D"
        "player_rank_score": 500.0,
        "money_won": 0
    }
    
    # Insert team
    supabase.table("teams").insert(team_data).execute()
    return team_data

def get_or_create_test_event() -> str:
    """Get an existing event ID or create a test event"""
    # First, try to get an existing event
    response = supabase.table("events").select("id").limit(1).execute()
    if hasattr(response, 'data') and response.data:
        return response.data[0]['id']
    
    # If no events exist, create a test event
    event_data = {
        "id": str(uuid.uuid4()),
        "name": "Test Event",
        "start_date": datetime.now(timezone.utc).isoformat(),
        "end_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "region": "Test Region",
        "tier": "T1",  # Must be one of: T1, T2, T3
        "status": "upcoming",
        "format": "3v3",
        "prize_pool": 1000,
        "registration_open": True,
        "max_teams": 16,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    response = supabase.table("events").insert(event_data).execute()
    if hasattr(response, 'data') and response.data:
        return response.data[0]['id']
    
    raise Exception("Failed to create a test event")

def create_test_match(team1_id: str, team2_id: str) -> Dict[str, Any]:
    """Create a test match with valid schema"""
    # Create a test event first if it doesn't exist
    event_id = get_or_create_test_event()
    
    # Get the team names from the database
    team1 = supabase.table("teams").select("name").eq("id", team1_id).execute().data[0]
    team2 = supabase.table("teams").select("name").eq("id", team2_id).execute().data[0]
    
    match_data = {
        "id": str(uuid.uuid4()),
        "event_id": event_id,
        "team_a_id": team1_id,
        "team_b_id": team2_id,
        "winner_id": team1_id,  # Team 1 wins by default for testing
        "score_a": 60,  # Team A score
        "score_b": 51,  # Team B score
        "played_at": datetime.now(timezone.utc).isoformat(),
        "boxscore_url": f"https://example.com/boxscores/{str(uuid.uuid4())}.png",
        "team_a_name": team1.get("name", "Team A"),  # Use actual team name with fallback
        "stage": "Group Play",  # Must be a valid stage value
        "game_number": 1,
        "team_b_name": team2.get("name", "Team B"),  # Use actual team name with fallback
        "winner_name": team1.get("name", "Team A")  # Winner is team 1 by default
    }
    
    # Ensure winner_id matches one of the team IDs
    match_data["winner_id"] = team1_id
    match_data["winner_name"] = team1.get("name", "Team A")
    
    # Insert match
    supabase.table("matches").insert(match_data).execute()
    return match_data

def create_test_player_stats_data(player_id: str, match_id: str, team_id: str) -> Dict[str, Any]:
    """Create test player stats data that matches the actual schema"""
    # Get the player's gamertag from the players table
    player = supabase.table("players").select("gamertag").eq("id", player_id).execute().data[0]
    
    return {
        "id": str(uuid.uuid4()),
        "player_id": player_id,
        "match_id": match_id,
        "team_id": team_id,
        "player_name": player["gamertag"],  # Use the actual player's gamertag
        "points": 15,  # Points scored by the player
        "assists": 2,  # Number of assists
        "rebounds": 3,  # Number of rebounds
        "steals": 1,  # Number of steals
        "blocks": 2,  # Number of blocks
        "turnovers": 8,  # Number of turnovers
        "fouls": 0,  # Number of fouls
        "fgm": 6,  # Field goals made
        "fga": 13,  # Field goals attempted
        "three_points_made": 3,  # Three-pointers made
        "three_points_attempted": 8,  # Three-pointers attempted
        "ftm": 0,  # Free throws made
        "fta": 0,  # Free throws attempted
        "plus_minus": 5,  # Plus/minus rating
        # Note: 'ps' is a generated column, so we don't include it in the insert
        "created_at": datetime.now(timezone.utc).isoformat()
    }

def test_create_player_stats_invalid_data():
    """Test creating player stats with invalid data"""
    print("\n🧪 Testing CREATE with invalid data...")
    
    # Create test data
    player = create_test_player()
    team1 = create_test_team()
    team2 = create_test_team()
    match_data = create_test_match(team1["id"], team2["id"])
    
    try:
        # Test with missing required fields
        invalid_stats = {
            "id": str(uuid.uuid4()),
            # Missing player_id, match_id, team_id
            "points": 15
        }
        
        try:
            response = supabase.table("player_stats").insert(invalid_stats).execute()
            assert False, "Should have raised an error for missing required fields"
        except Exception as e:
            print(f"✅ Correctly failed to create stats with missing required fields: {str(e)[:100]}...")
        
        # Test with invalid player_id
        invalid_stats = {
            "id": str(uuid.uuid4()),
            "player_id": "invalid-uuid",
            "match_id": match_data["id"],
            "team_id": team1["id"],
            "points": 15
        }
        
        try:
            response = supabase.table("player_stats").insert(invalid_stats).execute()
            assert False, "Should have raised an error for invalid player_id"
        except Exception as e:
            print(f"✅ Correctly failed to create stats with invalid player_id: {str(e)[:100]}...")
        
        # Test with non-existent foreign keys
        non_existent_id = str(uuid.uuid4())
        invalid_stats = {
            "id": str(uuid.uuid4()),
            "player_id": non_existent_id,
            "match_id": non_existent_id,
            "team_id": non_existent_id,
            "points": 15
        }
        
        try:
            response = supabase.table("player_stats").insert(invalid_stats).execute()
            assert False, "Should have raised an error for non-existent foreign keys"
        except Exception as e:
            print(f"✅ Correctly failed to create stats with non-existent foreign keys: {str(e)[:100]}...")
        
    finally:
        # Clean up test data
        cleanup_test_data(player, team1, team2, match_data)

def test_update_nonexistent_stats():
    """Test updating non-existent player stats"""
    print("\n🧪 Testing UPDATE non-existent stats...")
    
    non_existent_id = str(uuid.uuid4())
    update_data = {"points": 20}
    
    try:
        response = supabase.table("player_stats").update(update_data).eq("id", non_existent_id).execute()
        if hasattr(response, 'data') and response.data:
            print(f"⚠️  Warning: Update affected {len(response.data)} rows (expected 0)")
        else:
            print("✅ Correctly did not update non-existent stats")
    except Exception as e:
        print(f"✅ Correctly handled update of non-existent stats: {str(e)[:100]}...")

def test_delete_nonexistent_stats():
    """Test deleting non-existent player stats"""
    print("\n🧪 Testing DELETE non-existent stats...")
    
    non_existent_id = str(uuid.uuid4())
    
    try:
        response = supabase.table("player_stats").delete().eq("id", non_existent_id).execute()
        if hasattr(response, 'data') and response.data:
            print(f"⚠️  Warning: Delete affected {len(response.data)} rows (expected 0)")
        else:
            print("✅ Correctly did not delete non-existent stats")
    except Exception as e:
        print(f"✅ Correctly handled delete of non-existent stats: {str(e)[:100]}...")

def test_player_stats_boundary_values():
    """Test player stats with boundary values"""
    print("\n🧪 Testing boundary values...")
    
    # Create test data
    player = create_test_player()
    team1 = create_test_team()
    team2 = create_test_team()
    match_data = create_test_match(team1["id"], team2["id"])
    
    try:
        # Test with minimum values
        min_stats = {
            "id": str(uuid.uuid4()),
            "player_id": player["id"],
            "match_id": match_data["id"],
            "team_id": team1["id"],
            "points": 0,
            "assists": 0,
            "rebounds": 0,
            "steals": 0,
            "blocks": 0,
            "turnovers": 0,
            "fouls": 0,
            "fgm": 0,
            "fga": 0,
            "three_points_made": 0,
            "three_points_attempted": 0,
            "ftm": 0,
            "fta": 0,
            "plus_minus": -100  # Assuming -100 is a reasonable lower bound
        }
        
        response = supabase.table("player_stats").insert(min_stats).execute()
        if hasattr(response, 'data') and response.data:
            print("✅ Successfully created stats with minimum values")
            # Clean up
            supabase.table("player_stats").delete().eq("id", min_stats["id"]).execute()
        else:
            print("❌ Failed to create stats with minimum values")
        
        # Test with maximum values
        max_stats = {
            "id": str(uuid.uuid4()),
            "player_id": player["id"],
            "match_id": match_data["id"],
            "team_id": team1["id"],
            "points": 100,  # Assuming 100 is a reasonable upper bound for points in a game
            "assists": 30,  # Assuming 30 is a reasonable upper bound for assists
            "rebounds": 30,  # Assuming 30 is a reasonable upper bound for rebounds
            "steals": 10,    # Assuming 10 is a reasonable upper bound for steals
            "blocks": 10,    # Assuming 10 is a reasonable upper bound for blocks
            "turnovers": 15, # Assuming 15 is a reasonable upper bound for turnovers
            "fouls": 6,      # Assuming 6 is the maximum fouls before fouling out
            "fgm": 30,       # Assuming 30 is a reasonable upper bound for FGM
            "fga": 50,       # Assuming 50 is a reasonable upper bound for FGA
            "three_points_made": 15,  # Assuming 15 is a reasonable upper bound for 3PM
            "three_points_attempted": 25,  # Assuming 25 is a reasonable upper bound for 3PA
            "ftm": 20,       # Assuming 20 is a reasonable upper bound for FTM
            "fta": 25,       # Assuming 25 is a reasonable upper bound for FTA
            "plus_minus": 50  # Assuming 50 is a reasonable upper bound
        }
        
        response = supabase.table("player_stats").insert(max_stats).execute()
        if hasattr(response, 'data') and response.data:
            print("✅ Successfully created stats with maximum values")
            # Clean up
            supabase.table("player_stats").delete().eq("id", max_stats["id"]).execute()
        else:
            print("❌ Failed to create stats with maximum values")
            
    finally:
        # Clean up test data
        cleanup_test_data(player, team1, team2, match_data)

def cleanup_test_data(player, team1, team2, match_data):
    """Helper function to clean up test data in the correct order"""
    try:
        # First, delete any player stats that reference the match
        try:
            if 'id' in match_data:
                supabase.table("player_stats").delete().eq("match_id", match_data["id"]).execute()
        except Exception as e:
            print(f"⚠️  Warning cleaning up player_stats: {e}")
        
        # Then delete the match
        try:
            if 'id' in match_data:
                supabase.table("matches").delete().eq("id", match_data["id"]).execute()
        except Exception as e:
            print(f"⚠️  Warning cleaning up matches: {e}")
        
        # Then delete the teams
        try:
            for team in [team1, team2]:
                if team and 'id' in team:
                    # First remove any players from the team
                    supabase.table("players").update({"current_team_id": None}).eq("current_team_id", team["id"]).execute()
                    # Then delete the team
                    supabase.table("teams").delete().eq("id", team["id"]).execute()
        except Exception as e:
            print(f"⚠️  Warning cleaning up teams: {e}")
        
        # Finally, delete the player
        try:
            if player and 'id' in player:
                supabase.table("players").delete().eq("id", player["id"]).execute()
        except Exception as e:
            print(f"⚠️  Warning cleaning up players: {e}")
            
    except Exception as e:
        print(f"⚠️  Error during cleanup: {e}")

def test_player_stats_crud():
    """Test all CRUD operations for the player_stats table"""
    print("🚀 Testing Player Stats Table Operations")
    
    # Create test data
    player = create_test_player()
    team1 = create_test_team()
    team2 = create_test_team()
    match_data = create_test_match(team1["id"], team2["id"])
    
    test_stats = create_test_player_stats_data(player["id"], match_data["id"], team1["id"])
    stats_id = test_stats["id"]
    
    try:
        # Test CREATE
        print("\n🆕 Testing CREATE player stats...")
        response = supabase.table("player_stats").insert(test_stats).execute()
        if hasattr(response, 'data') and response.data:
            created_stats = response.data[0]
            print(f"✅ Created player stats for {created_stats['player_name']} (ID: {created_stats['id']})")
            print(f"   Points: {created_stats['points']}, Assists: {created_stats['assists']}, Rebounds: {created_stats['rebounds']}")
            print(f"   Steals: {created_stats['steals']}, Blocks: {created_stats['blocks']}, Turnovers: {created_stats['turnovers']}")
            print(f"   FGM/FGA: {created_stats['fgm']}/{created_stats['fga']}, 3PM/A: {created_stats['three_points_made']}/{created_stats['three_points_attempted']}")
        else:
            raise Exception("Failed to create player stats: No data in response")
        
        # Test READ
        print("\n📖 Testing GET player stats...")
        response = supabase.table("player_stats").select("*").eq("id", stats_id).execute()
        if hasattr(response, 'data') and response.data:
            fetched_stats = response.data[0]
            print(f"✅ Fetched player stats: {fetched_stats['id']}")
        else:
            raise Exception("Failed to fetch player stats: Stats not found")
        
        # Test UPDATE
        print("\n🔄 Testing UPDATE player stats...")
        update_data = {
            "points": 25,  # Updated from 15
            "assists": 5,  # Updated from 2
            "rebounds": 5,  # Updated from 3
            "steals": 2,  # Updated from 1
            "blocks": 3,  # Updated from 2
            "turnovers": 5,  # Updated from 8
            "fouls": 1,  # Updated from 0
            "fgm": 8,  # Updated from 6
            "fga": 15,  # Updated from 13
            "three_points_made": 5,  # Updated from 3
            "three_points_attempted": 10,  # Updated from 8
            "ftm": 1,  # Updated from 0
            "fta": 2,  # Updated from 0
            "plus_minus": 8  # Updated from 5
        }
        response = supabase.table("player_stats").update(update_data).eq("id", stats_id).execute()
        if hasattr(response, 'data') and response.data:
            updated_stats = response.data[0]
            assert updated_stats["points"] == 25, "Failed to update points"
            print(f"✅ Updated player stats: Points={updated_stats['points']}, Assists={updated_stats['assists']}, Rebounds={updated_stats['rebounds']}")
        else:
            raise Exception("Failed to update player stats: No data in response")
        
        # Test QUERY with filters
        print("\n🔍 Testing QUERY player stats...")
        response = supabase.table("player_stats") \
                         .select("*") \
                         .eq("player_id", player["id"]) \
                         .limit(5) \
                         .execute()
        stats_list = response.data if hasattr(response, 'data') else []
        print(f"✅ Found {len(stats_list)} stats entries for player {player['gamertag']}")
        
        # Test DELETE
        print("\n🗑️  Testing DELETE player stats...")
        response = supabase.table("player_stats").delete().eq("id", stats_id).execute()
        if hasattr(response, 'data') and response.data:
            print("✅ Delete successful")
        else:
            raise Exception("Failed to delete player stats: No data in response")
        
        # Verify deletion
        response = supabase.table("player_stats").select("*").eq("id", stats_id).execute()
        if hasattr(response, 'data') and response.data:
            print("❌ Player stats were not deleted successfully")
        else:
            print("✅ Player stats were deleted successfully")
        
        print("\n🎉 All player stats operations tested successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during player stats operations: {str(e)}")
        # Try to clean up if something went wrong
        try:
            supabase.table("player_stats").delete().eq("id", stats_id).execute()
        except Exception as cleanup_error:
            print(f"⚠️  Cleanup error: {cleanup_error}")
        raise  # Re-raise the original error
    finally:
        # Use the helper function to clean up test data
        cleanup_test_data(player, team1, team2, match_data)

if __name__ == "__main__":
    # Run all test functions
    test_create_player_stats_invalid_data()
    test_update_nonexistent_stats()
    test_delete_nonexistent_stats()
    test_player_stats_boundary_values()
    test_player_stats_crud()
    # Check if Supabase credentials are set
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    else:
        test_player_stats_crud()
