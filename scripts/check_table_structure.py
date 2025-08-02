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

def get_table_structure(table_name):
    """Get the structure of a table by trying to insert a minimal row"""
    print(f"\nChecking structure of table: {table_name}")
    
    # Try to get one row to see the structure
    try:
        response = supabase.table(table_name).select("*").limit(1).execute()
        if hasattr(response, 'data') and response.data:
            print(f"\nSample row from {table_name}:")
            for key, value in response.data[0].items():
                print(f"- {key}: {value} (type: {type(value).__name__})")
            return
    except Exception as e:
        print(f"Error getting sample row: {e}")
    
    # If we can't get a sample row, try to get column information from the error
    try:
        # This will fail but should give us column information in the error
        supabase.table(table_name).select("non_existent_column").execute()
    except Exception as e:
        error_msg = str(e)
        print("\nError details from attempting to query non-existent column:")
        print(error_msg)
        
        # Try to extract column names from the error message
        if "Could not find the" in error_msg and "column of" in error_msg:
            # Extract the column name from the error message
            column_part = error_msg.split("'")[1]
            print(f"\nDetected column: {column_part}")

if __name__ == "__main__":
    # Check the players table structure
    get_table_structure("players")
    
    # Also check the player_stats table structure
    get_table_structure("player_stats")
    
    # Also check the teams table structure
    get_table_structure("teams")
    
    # Also check the matches table structure
    get_table_structure("matches")
