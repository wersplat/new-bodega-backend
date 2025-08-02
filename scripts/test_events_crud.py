"""
Comprehensive test script for Events CRUD operations with Supabase
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

def create_test_event_data() -> Dict[str, Any]:
    """Create test event data that matches the actual schema"""
    event_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    region_id = get_or_create_test_region()
    
    return {
        "id": event_id,
        "name": f"Test Tournament {event_id[:8]}",
        "type": "tournament",  # Must be one of: "tournament", "qualifier", "exhibition", "scrimmage"
        "is_global": False,
        "region_id": region_id,  # Must be a valid region UUID
        "start_date": (now + timedelta(days=7)).isoformat(),
        "end_date": (now + timedelta(days=8)).isoformat(),
        "max_rp": 1000,
        "decay_days": 7,
        "processed": False,
        "description": f"Test tournament description for event {event_id[:8]}",
        "banner_url": "https://example.com/banner.jpg",
        "rules_url": "https://example.com/rules",
        "status": "upcoming",  # Must be one of: "upcoming", "in_progress", "completed", "cancelled"
        "tier": "T1",  # Must be one of: "T1", "T2", "T3"
        "season_number": 1,
        "prize_pool": 25000,  # RP
        "processed_at": None  # Will be set when processed
    }

def test_events_crud():
    """Test all CRUD operations for the events table"""
    print("🚀 Testing Events Table Operations")
    
    # Create test data
    test_event = create_test_event_data()
    event_id = test_event["id"]
    
    try:
        # Test CREATE
        print("\n🆕 Testing CREATE event...")
        response = supabase.table("events").insert(test_event).execute()
        if hasattr(response, 'data') and response.data:
            created_event = response.data[0]
            print(f"✅ Created event: {created_event['name']} (ID: {created_event['id']})")
        else:
            raise Exception("Failed to create event: No data in response")
        
        # Test READ
        print("\n📖 Testing GET event...")
        response = supabase.table("events").select("*").eq("id", event_id).execute()
        if hasattr(response, 'data') and response.data:
            fetched_event = response.data[0]
            print(f"✅ Fetched event: {fetched_event['name']}")
        else:
            raise Exception("Failed to fetch event: Event not found")
        
        # Test UPDATE
        print("\n🔄 Testing UPDATE event...")
        update_data = {
            "status": "in_progress",
            "max_rp": 1500,
            "prize_pool": 50000,
            "description": "Updated description"
        }
        response = supabase.table("events").update(update_data).eq("id", event_id).execute()
        if hasattr(response, 'data') and response.data:
            updated_event = response.data[0]
            assert updated_event["status"] == "in_progress", "Failed to update event status"
            assert updated_event["max_rp"] == 1500, "Failed to update max_rp"
            print(f"✅ Updated event: Status={updated_event['status']}, "
                  f"Max RP={updated_event['max_rp']}")
        else:
            raise Exception("Failed to update event: No data in response")
        
        # Test QUERY with filters
        print("\n🔍 Testing QUERY events...")
        response = supabase.table("events") \
                         .select("*") \
                         .eq("type", "tournament") \
                         .limit(5) \
                         .execute()
        events = response.data if hasattr(response, 'data') else []
        print(f"✅ Found {len(events)} tournament events in the database")
        
        # Test DELETE
        print("\n🗑️  Testing DELETE event...")
        response = supabase.table("events").delete().eq("id", event_id).execute()
        if hasattr(response, 'data') and response.data:
            print("✅ Delete successful")
        else:
            raise Exception("Failed to delete event: No data in response")
        
        # Verify deletion
        response = supabase.table("events").select("*").eq("id", event_id).execute()
        if hasattr(response, 'data') and response.data:
            print("❌ Event was not deleted successfully")
        else:
            print("✅ Event was deleted successfully")
        
        print("\n🎉 All event operations tested successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during event operations: {str(e)}")
        # Try to clean up if something went wrong
        try:
            supabase.table("events").delete().eq("id", event_id).execute()
        except Exception as cleanup_error:
            print(f"⚠️  Cleanup error: {cleanup_error}")
        raise  # Re-raise the original error

if __name__ == "__main__":
    # Check if Supabase credentials are set
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    else:
        test_events_crud()
