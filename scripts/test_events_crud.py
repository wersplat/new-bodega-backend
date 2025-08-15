"""
Comprehensive test script for Tournaments CRUD operations with Supabase
"""
import os
import uuid
from datetime import datetime, timedelta, timezone
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

def create_test_tournament_data() -> Dict[str, Any]:
    """Create test tournament data that matches the tournaments schema"""
    tournament_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    return {
        "id": tournament_id,
        "name": f"Test Tournament {tournament_id[:8]}",
        "start_date": (now + timedelta(days=7)).isoformat(),
        "end_date": (now + timedelta(days=8)).isoformat(),
        "max_rp": 1000,
        "decay_days": 7,
        "description": f"Test tournament description for {tournament_id[:8]}",
        "banner_url": "https://example.com/banner.jpg",
        "rules_url": "https://example.com/rules",
        "status": "upcoming",  # matches public.status enum
        "tier": "T1",  # matches public.event_tier enum
        "prize_pool": 25000,
        "processed_at": None
    }

def test_tournaments_crud():
    """Test all CRUD operations for the tournaments table"""
    print("🚀 Testing Tournaments Table Operations")
    
    # Create test data
    test_tournament = create_test_tournament_data()
    tournament_id = test_tournament["id"]
    
    try:
        # Test CREATE
        print("\n🆕 Testing CREATE tournament...")
        response = supabase.table("tournaments").insert(test_tournament).execute()
        if hasattr(response, 'data') and response.data:
            created_event = response.data[0]
            print(f"✅ Created tournament: {created_event['name']} (ID: {created_event['id']})")
        else:
            raise Exception("Failed to create tournament: No data in response")
        
        # Test READ
        print("\n📖 Testing GET tournament...")
        response = supabase.table("tournaments").select("*").eq("id", tournament_id).execute()
        if hasattr(response, 'data') and response.data:
            fetched_event = response.data[0]
            print(f"✅ Fetched tournament: {fetched_event['name']}")
        else:
            raise Exception("Failed to fetch tournament: Tournament not found")
        
        # Test UPDATE
        print("\n🔄 Testing UPDATE tournament...")
        update_data = {
            "status": "in_progress",
            "max_rp": 1500,
            "prize_pool": 50000,
            "description": "Updated description"
        }
        response = supabase.table("tournaments").update(update_data).eq("id", tournament_id).execute()
        if hasattr(response, 'data') and response.data:
            updated_event = response.data[0]
            assert updated_event["status"] == "in_progress", "Failed to update event status"
            assert updated_event["max_rp"] == 1500, "Failed to update max_rp"
            print(f"✅ Updated tournament: Status={updated_event['status']}, "
                  f"Max RP={updated_event['max_rp']}")
        else:
            raise Exception("Failed to update tournament: No data in response")
        
        # Test QUERY with filters
        print("\n🔍 Testing QUERY tournaments...")
        response = supabase.table("tournaments") \
                         .select("*") \
                         .limit(5) \
                         .execute()
        tournaments = response.data if hasattr(response, 'data') else []
        print(f"✅ Found {len(tournaments)} tournaments in the database")
        
        # Test DELETE
        print("\n🗑️  Testing DELETE tournament...")
        response = supabase.table("tournaments").delete().eq("id", tournament_id).execute()
        if hasattr(response, 'data') and response.data:
            print("✅ Delete successful")
        else:
            raise Exception("Failed to delete tournament: No data in response")
        
        # Verify deletion
        response = supabase.table("tournaments").select("*").eq("id", tournament_id).execute()
        if hasattr(response, 'data') and response.data:
            print("❌ Tournament was not deleted successfully")
        else:
            print("✅ Tournament was deleted successfully")
        
        print("\n🎉 All tournament operations tested successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during tournament operations: {str(e)}")
        # Try to clean up if something went wrong
        try:
            supabase.table("tournaments").delete().eq("id", tournament_id).execute()
        except Exception as cleanup_error:
            print(f"⚠️  Cleanup error: {cleanup_error}")
        raise  # Re-raise the original error

if __name__ == "__main__":
    # Check if Supabase credentials are set
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    else:
        test_tournaments_crud()
