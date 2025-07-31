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
    """Create a test event with valid data"""
    event_id = str(uuid.uuid4())
    return {
        "id": event_id,
        "name": "Test Tournament",
        "event_type": "Tournament",
        "event_tier": "T1",
        "start_time": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "end_time": (datetime.utcnow() + timedelta(days=8)).isoformat(),
        "status": "Upcoming",
        "league": "UPA",
        "stage": "Group Play",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "is_active": True,
        "max_players": 32,
        "entry_fee": 1000,  # RP
        "prize_pool": 25000,  # RP
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
        print(f"✅ Created event: {created_event['name']} (ID: {created_event['id']})")
        
        # Test READ
        print("\n📖 Testing GET event...")
        fetched_event = supabase.fetch_by_id("events", event_id)
        print(f"✅ Fetched event: {fetched_event['name']}")
        
        # Test UPDATE
        print("\n🔄 Testing UPDATE event...")
        update_data = {
            "status": "In Progress",
            "max_players": 64,
            "prize_pool": 50000
        }
        updated_event = supabase.update("events", event_id, update_data)
        print(f"✅ Updated event: Status={updated_event['status']}, "
              f"Max Players={updated_event['max_players']}")
        
        # Test QUERY with filters
        print("\n🔍 Testing QUERY events...")
        client = supabase.get_client()
        response = client.table("events") \
                       .select("*") \
                       .eq("league", "UPA") \
                       .execute()
        events = response.data if hasattr(response, 'data') else []
        print(f"✅ Found {len(events)} events in the 'UPA' league")
        
        # Test DELETE (optional - comment out if you want to keep test data)
        print("\n🗑️  Testing DELETE event...")
        delete_result = supabase.delete("events", event_id)
        print(f"✅ Delete successful: {delete_result}")
        
        # Verify delete
        deleted_event = supabase.fetch_by_id("events", event_id)
        assert deleted_event is None, "Delete verification failed"
        
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
