"""
Test script to verify Supabase operations with the events table
"""
import os
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from app.core.supabase import supabase
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

def create_test_event() -> Dict[str, Any]:
    """Create a test event with valid data according to schema"""
    event_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    return {
        "id": event_id,
        "name": "Test Tournament",
        "type": "tournament",  # Using schema field name 'type' instead of 'event_type'
        "is_global": False,
        "region_id": "us-east-1",  # Assuming this is required
        "start_date": (now + timedelta(days=7)).isoformat(),
        "end_date": (now + timedelta(days=8)).isoformat(),
        "max_rp": 1000,  # Using schema field name 'max_rp' instead of 'entry_fee'
        "decay_days": 7,  # Days until RP starts decaying
        "processed": False,
        "description": "Test tournament description",
        "banner_url": "https://example.com/banner.jpg",
        "rules_url": "https://example.com/rules",
        "status": "upcoming",  # Using lowercase to match likely enum values
        "tier": "T1",  # Using schema field name 'tier' instead of 'event_tier'
        "season_number": 1,
        "prize_pool": 25000,  # RP
        "created_at": now.isoformat(),
        "processed_at": None  # Will be set when processed
    }

def test_events_crud():
    print("🚀 Testing Events Table Operations")
    
    # Create test data
    test_event = create_test_event()
    event_id = test_event["id"]
    
    try:
        # Test CREATE
        print("\n🆕 Testing CREATE event...")
        created_event = supabase.insert("events", test_event)
        assert created_event is not None, "Failed to create event"
        print(f"✅ Created event: {created_event['name']} (ID: {created_event['id']})")
        
        # Test READ
        print("\n📖 Testing GET event...")
        fetched_event = supabase.fetch_by_id("events", event_id)
        assert fetched_event is not None, "Failed to fetch event"
        print(f"✅ Fetched event: {fetched_event['name']}")
        
        # Test UPDATE
        print("\n🔄 Testing UPDATE event...")
        update_data = {
            "status": "in_progress",
            "max_rp": 1500,
            "prize_pool": 50000,
            "description": "Updated description"
        }
        updated_event = supabase.update("events", event_id, update_data)
        assert updated_event is not None, "Failed to update event"
        print(f"✅ Updated event: Status={updated_event['status']}, "
              f"Max RP={updated_event['max_rp']}")
        
        # Test QUERY with filters
        print("\n🔍 Testing QUERY events...")
        # Using the Supabase client directly for more complex queries
        client = supabase.get_client()
        response = client.table("events") \
                       .select("*") \
                       .eq("type", "tournament") \
                       .execute()
        events = response.data if hasattr(response, 'data') else []
        print(f"✅ Found {len(events)} tournament events in the database")
        
        # Test DELETE
        print("\n🗑️  Testing DELETE event...")
        delete_result = supabase.delete("events", event_id)
        assert delete_result is not None, "Failed to delete event"
        print("✅ Delete successful")
        
        # Verify deletion
        deleted_event = supabase.fetch_by_id("events", event_id)
        assert deleted_event is None, "Event was not deleted successfully"
        
        print("\n🎉 All event operations tested successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during event operations: {str(e)}")
        # Clean up if something went wrong
        try:
            supabase.delete("events", event_id)
        except:
            pass
        raise

if __name__ == "__main__":
    # Check if Supabase credentials are set
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    else:
        test_events_crud()
