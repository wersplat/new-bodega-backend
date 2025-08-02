"""
Script to check Row Level Security (RLS) policies directly using SQL
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

def check_table_rls(table_name: str = "players"):
    """Check RLS status and policies for a specific table"""
    try:
        # Check if RLS is enabled for the table
        rls_query = f"""
        SELECT relname, relrowsecurity, relforcerowsecurity 
        FROM pg_class 
        WHERE oid = '{table_name}'::regclass;
        """
        
        # Execute the query
        result = supabase.rpc('execute_sql', {'query': rls_query}).execute()
        
        if hasattr(result, 'data') and result.data:
            rls_info = result.data[0]
            print(f"\n🔍 RLS Status for table '{table_name}':")
            print(f"  - Table Name: {rls_info.get('relname')}")
            print(f"  - RLS Enabled: {'Yes' if rls_info.get('relrowsecurity') else 'No'}")
            print(f"  - RLS Forced: {'Yes' if rls_info.get('relforcerowsecurity') else 'No'}")
        
        # Get RLS policies for the table
        policies_query = f"""
        SELECT * FROM pg_policies 
        WHERE tablename = '{table_name}'
        """
        
        policies_result = supabase.rpc('execute_sql', {'query': policies_query}).execute()
        
        if hasattr(policies_result, 'data') and policies_result.data:
            print(f"\n🔒 RLS Policies for table '{table_name}':")
            for policy in policies_result.data:
                print(f"\n📜 Policy: {policy.get('policyname')}")
                print(f"   - Roles: {policy.get('roles')}")
                print(f"   - Command: {policy.get('cmd')}")
                print(f"   - Using: {policy.get('qual') or 'No condition'}")
                print(f"   - With Check: {policy.get('with_check') or 'No check'}")
        else:
            print(f"\nℹ️ No RLS policies found for table '{table_name}'")
            
    except Exception as e:
        print(f"❌ Error checking RLS: {str(e)}")
        print("This might be due to insufficient permissions or the function not existing.")

if __name__ == "__main__":
    print("🔍 Checking RLS configuration...")
    check_table_rls("players")
    
    # Uncomment to check other tables as needed
    # check_table_rls("teams")
    # check_table_rls("matches")
