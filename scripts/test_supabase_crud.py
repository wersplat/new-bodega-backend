"""
Test script to verify Supabase CRUD operations
"""
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from app.core.supabase import supabase

# Load environment variables
load_dotenv()

def test_crud_operations():
    print("🚀 Testing Supabase CRUD Operations")
    
    # Test table (using a test table to avoid modifying production data)
    test_table = "test_crud_operations"
    
    # Test data
    test_id = str(uuid.uuid4())
    test_data = {
        "id": test_id,
        "name": "Test Item",
        "description": "This is a test item",
        "created_at": datetime.utcnow().isoformat(),
        "is_active": True
    }
    
    try:
        # Test CREATE
        print("\n🆕 Testing CREATE operation...")
        created_item = supabase.insert(test_table, test_data)
        print(f"✅ Created item: {created_item}")
        
        # Test READ
        print("\n📖 Testing READ operation...")
        fetched_item = supabase.fetch_by_id(test_table, test_id)
        print(f"✅ Fetched item: {fetched_item}")
        
        # Test UPDATE
        print("\n🔄 Testing UPDATE operation...")
        update_data = {"name": "Updated Test Item", "is_active": False}
        updated_item = supabase.update(test_table, test_id, update_data)
        print(f"✅ Updated item: {updated_item}")
        
        # Verify update
        verified_item = supabase.fetch_by_id(test_table, test_id)
        assert verified_item["name"] == "Updated Test Item", "Update verification failed"
        
        # Test DELETE
        print("\n🗑️  Testing DELETE operation...")
        delete_result = supabase.delete(test_table, test_id)
        print(f"✅ Delete successful: {delete_result}")
        
        # Verify delete
        deleted_item = supabase.fetch_by_id(test_table, test_id)
        assert deleted_item is None, "Delete verification failed"
        
        print("\n🎉 All CRUD operations tested successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during CRUD operations: {str(e)}")
        raise

if __name__ == "__main__":
    # Check if Supabase credentials are set
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    else:
        test_crud_operations()
