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

def get_table_columns(table_name):
    """Get column information for a table"""
    try:
        # This is a hacky way to get schema info since Supabase doesn't expose it directly
        # We'll try to insert a row with invalid data to trigger an error with the expected schema
        test_data = {"id": "00000000-0000-0000-0000-000000000000"}
        response = supabase.table(table_name).insert(test_data).execute()
        # If we get here, the insert succeeded (unlikely with just an ID)
        print(f"Unexpected success inserting into {table_name}")
        return {}
    except Exception as e:
        # The error message should contain schema information
        error_msg = str(e)
        print(f"Error getting schema for {table_name}:")
        print(error_msg)
        return error_msg

def get_table_data_sample(table_name, limit=1):
    """Get a sample of data from a table"""
    try:
        response = supabase.table(table_name).select("*").limit(limit).execute()
        if hasattr(response, 'data') and response.data:
            print(f"\nSample data from {table_name}:")
            for row in response.data:
                print(row)
            return response.data
        else:
            print(f"No data found in {table_name}")
            return []
    except Exception as e:
        print(f"Error getting data from {table_name}: {e}")
        return []

# Get schema for matches table
print("Getting schema for 'matches' table...")
matches_schema = get_table_columns("matches")

# Get sample data from matches table
matches_data = get_table_data_sample("matches")

# Also check if there are any enums in the database
print("\nTrying to get enum types...")
try:
    # This is a PostgreSQL system table query
    response = supabase.rpc('pg_type', {}).execute()
    if hasattr(response, 'data') and response.data:
        print("Found some type information:")
        for row in response.data:
            if row.get('typname') == 'stage':
                print(f"Found 'stage' type: {row}")
    else:
        print("No type information found")
except Exception as e:
    print(f"Error getting type information: {e}")

# As a last resort, try to get the first match and see what stage values exist
if matches_data:
    print("\nFound existing matches. Here's the first one's stage value:")
    print(matches_data[0].get('stage', 'No stage field found'))
else:
    print("\nNo existing matches found in the database.")
