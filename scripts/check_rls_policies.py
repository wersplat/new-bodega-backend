"""
Script to check Row Level Security (RLS) policies for Supabase tables
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY]):
    raise ValueError("Missing required Supabase environment variables")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_rls_policies(table_name: str = "players"):
    """Check RLS policies for a specific table"""
    try:
        # Query the pg_policies table directly
        query = f"""
        SELECT * FROM pg_policies 
        WHERE tablename = '{table_name}'
        """
        
        # Execute the query
        result = supabase.rpc('pg_policies', {'table_name': table_name}).execute()
        
        if hasattr(result, 'data') and result.data:
            print(f"\n🔍 RLS Policies for table '{table_name}':")
            for policy in result.data:
                print(f"\nPolicy Name: {policy.get('policyname')}")
                print(f"  - Command: {policy.get('cmd')}")
                print(f"  - Roles: {policy.get('roles')}")
                print(f"  - Using: {policy.get('qual')}")
                print(f"  - With Check: {policy.get('with_check')}")
        else:
            print(f"No RLS policies found for table '{table_name}' or unable to query policies.")
            
        # Also check if RLS is enabled for the table
        rls_status = supabase.rpc('get_rls_status', {'table_name': table_name}).execute()
        if hasattr(rls_status, 'data') and rls_status.data:
            print(f"\n🔒 RLS is {'ENABLED' if rls_status.data[0].get('rls_enabled') else 'DISABLED'} for table '{table_name}'")
        
    except Exception as e:
        print(f"❌ Error checking RLS policies: {str(e)}")
        print("This might be due to insufficient permissions or the function not existing.")

if __name__ == "__main__":
    print("🔍 Checking RLS policies for Supabase tables...")
    check_rls_policies("players")
    
    # Uncomment to check other tables as needed
    # check_rls_policies("teams")
    # check_rls_policies("matches")
