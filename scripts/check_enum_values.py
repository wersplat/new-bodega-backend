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

try:
    # Query to get the enum values for the 'stage' column in 'matches' table
    # This is a direct query to the information_schema
    query = """
    SELECT unnest(enum_range(NULL::stage)) AS stage_value;
    """
    
    # Execute the raw query
    response = supabase.rpc('pg_query', {'query': query}).execute()
    
    if hasattr(response, 'data') and response.data:
        print("✅ Valid values for 'stage' enum in 'matches' table:")
        for row in response.data:
            print(f"- {row['stage_value']}")
    else:
        print("❌ Could not retrieve enum values. Response:", response)
        
        # Try an alternative approach using the information_schema
        print("\nTrying alternative approach...")
        query = """
        SELECT t.typname AS enum_name, 
               e.enumlabel AS enum_value
        FROM pg_type t 
        JOIN pg_enum e ON t.oid = e.enumtypid  
        JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        WHERE n.nspname = 'public' AND t.typname = 'stage';
        """
        
        response = supabase.rpc('pg_query', {'query': query}).execute()
        
        if hasattr(response, 'data') and response.data:
            print("✅ Valid values for 'stage' enum in 'matches' table:")
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
