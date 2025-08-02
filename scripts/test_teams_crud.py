"""
Comprehensive test script for Teams CRUD operations with Supabase
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
        "code": "test-region",
        "is_active": True
    }
    response = supabase.table("regions").insert(region_data).execute()
    if hasattr(response, 'data') and response.data:
        return response.data[0]['id']
    
    raise Exception("Failed to get or create a test region")

def create_test_team_data() -> Dict[str, Any]:
    """Create test team data that matches the actual schema"""
    team_id = str(uuid.uuid4())
    region_id = get_or_create_test_region()
    
    return {
        "id": team_id,
        "name": f"Test Team {team_id[:8]}",
        "region_id": region_id,
        "logo_url": "https://example.com/logo.png",
        "current_rp": 1000,
        "elo_rating": 1500,
        "global_rank": 1,
        "leaderboard_tier": 1,
        "player_rank_score": 85.5,
        "money_won": 0
    }

def test_teams_crud():
    """Test all CRUD operations for the teams table"""
    print("🚀 Testing Teams Table Operations")
    
    # Create test data
    test_team = create_test_team_data()
    team_id = test_team["id"]
    
    try:
        # Test CREATE
        print("\n🆕 Testing CREATE team...")
        response = supabase.table("teams").insert(test_team).execute()
        if hasattr(response, 'data') and response.data:
            created_team = response.data[0]
            print(f"✅ Created team: {created_team['name']} (ID: {created_team['id']})")
        else:
            raise Exception("Failed to create team: No data in response")
        
        # Test READ
        print("\n📖 Testing GET team...")
        response = supabase.table("teams").select("*").eq("id", team_id).execute()
        if hasattr(response, 'data') and response.data:
            fetched_team = response.data[0]
            print(f"✅ Fetched team: {fetched_team['name']}")
        else:
            raise Exception("Failed to fetch team: Team not found")
        
        # Test UPDATE
        print("\n🔄 Testing UPDATE team...")
        update_data = {
            "name": f"Updated Team {team_id[:8]}",
            "logo_url": "https://example.com/updated-logo.png",
            "current_rp": 1100,
            "elo_rating": 1550
        }
        response = supabase.table("teams").update(update_data).eq("id", team_id).execute()
        if hasattr(response, 'data') and response.data:
            updated_team = response.data[0]
            assert updated_team["name"] == update_data["name"], "Failed to update team name"
            print(f"✅ Updated team: Name={updated_team['name']}, RP={updated_team['current_rp']}")
        else:
            raise Exception("Failed to update team: No data in response")
        
        # Test QUERY with filters
        print("\n🔍 Testing QUERY teams...")
        response = supabase.table("teams") \
                         .select("*") \
                         .limit(5) \
                         .execute()
        teams = response.data if hasattr(response, 'data') else []
        print(f"✅ Found {len(teams)} teams in the database")
        
        # Test DELETE
        print("\n🗑️  Testing DELETE team...")
        response = supabase.table("teams").delete().eq("id", team_id).execute()
        if hasattr(response, 'data') and response.data:
            print("✅ Delete successful")
        else:
            raise Exception("Failed to delete team: No data in response")
        
        # Verify deletion
        response = supabase.table("teams").select("*").eq("id", team_id).execute()
        if hasattr(response, 'data') and response.data:
            print("❌ Team was not deleted successfully")
        else:
            print("✅ Team was deleted successfully")
        
        print("\n🎉 All team operations tested successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during team operations: {str(e)}")
        # Try to clean up if something went wrong
        try:
            supabase.table("teams").delete().eq("id", team_id).execute()
        except Exception as cleanup_error:
            print(f"⚠️  Cleanup error: {cleanup_error}")
        raise  # Re-raise the original error

if __name__ == "__main__":
    # Check if Supabase credentials are set
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    else:
        test_teams_crud()
