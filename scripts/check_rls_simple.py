"""
Enhanced script to test RLS by attempting CRUD operations on the players table
"""
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY]):
    raise ValueError("Missing required Supabase environment variables")

# Initialize Supabase client
print(f"🔌 Connecting to Supabase at {SUPABASE_URL}")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_read_operation():
    """Test if we can read from the players table"""
    print("\n🔍 Testing READ operation...")
    try:
        result = supabase.table("players").select("*").limit(1).execute()
        if hasattr(result, 'data') and result.data:
            print(f"✅ Successfully read {len(result.data)} player(s)")
            return True
        else:
            print("ℹ️ No data returned from players table (this might be expected if table is empty)")
            return True
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error reading from players table: {error_msg}")
        return False

def test_insert_operation():
    """Test if we can insert into the players table"""
    print("\n➕ Testing INSERT operation...")
    
    # Generate test data
    player_id = str(uuid.uuid4())
    test_player = {
        "id": player_id,
        "gamertag": f"test_{player_id[:8]}",
        "position": "Point Guard",
        "player_rp": 1000,
        "is_rookie": True,
        "discord_id": f"test_discord_{player_id[:8]}",
        "twitter_id": f"test_twitter_{player_id[:8]}",
    }
    
    try:
        result = supabase.table("players").insert(test_player).execute()
        if hasattr(result, 'data') and result.data:
            print(f"✅ Successfully inserted test player: {result.data[0]['gamertag']}")
            return result.data[0]['id']  # Return the ID for cleanup
        else:
            print("❌ Insert operation returned no data")
            return None
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error inserting into players table: {error_msg}")
        
        # Provide helpful suggestions based on the error
        if "row-level security" in error_msg.lower():
            print("\n🔒 Row Level Security (RLS) is blocking the insert operation")
            print("   To fix this, you need to either:")
            print("   1. Use a service role key with bypass RLS capability")
            print("   2. Update the RLS policies in Supabase to allow this operation")
            print("   3. Temporarily disable RLS for testing (not recommended for production)")
            print("\nTo check/update RLS policies:")
            print(f"1. Go to Authentication -> Policies in the Supabase dashboard")
            print(f"2. Select the 'players' table")
            print(f"3. Review/update the policies as needed")
        
        return None

def test_delete_operation(player_id):
    """Test if we can delete from the players table"""
    if not player_id:
        return False
        
    print(f"\n🗑️  Testing DELETE operation for player ID: {player_id}")
    try:
        result = supabase.table("players").delete().eq("id", player_id).execute()
        if hasattr(result, 'data') and result.data:
            print(f"✅ Successfully deleted test player")
            return True
        else:
            print("❌ Delete operation returned no data")
            return False
    except Exception as e:
        print(f"❌ Error deleting from players table: {str(e)}")
        return False

def check_service_role():
    """Check if we're using a service role key"""
    print("\n🔑 Checking Supabase client configuration...")
    is_service_role = bool(os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
    print(f"   Using key: {'service role key' if is_service_role else 'regular key'}")
    
    # Try to get the current user (should work with service role key)
    try:
        user = supabase.auth.get_user()
        if user and hasattr(user, 'user'):
            print(f"   Authenticated as: {user.user.email}")
            return True
        else:
            print("   Not authenticated with service role key")
            return is_service_role  # If we have service key but can't auth, still try operations
    except Exception as e:
        print(f"   Error checking auth: {str(e)}")
        return is_service_role  # If we have service key but auth check fails, still try operations

if __name__ == "__main__":
    print("🔍 Testing Supabase RLS and Permissions...")
    
    # Check if we're using a service role key
    is_service_role = check_service_role()
    
    # Test read operation
    can_read = test_read_operation()
    
    # Test insert operation
    inserted_id = None
    if can_read or is_service_role:  # Only try insert if we can read or have service role
        inserted_id = test_insert_operation()
    
    # Test delete operation if insert was successful
    if inserted_id:
        test_delete_operation(inserted_id)
    
    # Provide summary and next steps
    print("\n" + "="*50)
    print("TEST SUMMARY:")
    print(f"- Can read from players table: {'✅' if can_read else '❌'}")
    print(f"- Can insert into players table: {'✅' if inserted_id else '❌'}")
    
    if not can_read or not inserted_id:
        print("\nNEXT STEPS:")
        print("1. Check your Supabase RLS policies in the dashboard:")
        print("   - Go to Authentication -> Policies")
        print("   - Select the 'players' table")
        print("   - Review/update the policies as needed")
        print("2. If using RLS, ensure you have the correct policies in place")
        print("3. For testing, you can temporarily disable RLS with:")
        print("   ALTER TABLE players DISABLE ROW LEVEL SECURITY;")
        print("   (Not recommended for production)")
        print("4. Or use a service role key for testing by setting SUPABASE_SERVICE_ROLE_KEY in .env")
