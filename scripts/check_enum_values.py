import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    exit(1)

supabase = create_client(supabase_url, supabase_key)

def check_enum_values(enum_name):
    print(f"\nChecking values for enum: {enum_name}")
    
    # First approach: Try to get enum values directly
    try:
        query = f"""
        SELECT unnest(enum_range(NULL::{enum_name})) AS enum_value;
        """
        
        response = supabase.rpc('pg_query', {'query': query}).execute()
        
        if hasattr(response, 'data') and response.data:
            print(f"✅ Valid values for '{enum_name}' enum:")
            for row in response.data:
                print(f"- {row['enum_value']}")
            return
    except Exception as e:
        print(f"First approach failed: {e}")
    
    # Second approach: Try information_schema
    try:
        query = """
        SELECT t.typname AS enum_name, 
               e.enumlabel AS enum_value
        FROM pg_type t 
        JOIN pg_enum e ON t.oid = e.enumtypid  
        JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        WHERE n.nspname = 'public' AND t.typname = %(enum_name)s;
        """
        
        response = supabase.rpc('pg_query', {'query': query, 'params': {'enum_name': enum_name}}).execute()
        
        if hasattr(response, 'data') and response.data:
            print(f"✅ Valid values for '{enum_name}' enum:")
            for row in response.data:
                print(f"- {row['enum_value']}")
        else:
            print("❌ Could not retrieve enum values using alternative approach. Response:", response)
            
    except Exception as e:
        print(f"❌ Error querying the database: {e}")
        
        # As a last resort, try to get any enum values from the database
        try:
            print("\nTrying to list all enums in the database...")
            response = supabase.rpc('pg_typeof', {'anyelement': 'stage'}).execute()
            print("Type of 'stage':", response)
        except Exception as e2:
            print(f"❌ Could not get type info: {e2}")

if __name__ == "__main__":
    # Check for salary_tier enum values
    check_enum_values('salary_tier')
    
    # Also check for player_position enum values
    check_enum_values('player_position')
