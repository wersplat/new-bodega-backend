"""
Script to list all tables and their columns in Supabase
"""
import os
import json
from dotenv import load_dotenv
from app.core.supabase import supabase

def list_tables():
    """List all tables in the Supabase database"""
    try:
        # Try to get a list of tables by querying the information_schema
        client = supabase.get_client()
        
        # This is a workaround since Supabase doesn't directly expose table listing
        # We'll try to get one row from each table we know about
        known_tables = [
            'players', 'teams', 'events', 'matches', 'transactions',
            'player_stats', 'team_members', 'event_participants'
        ]
        
        tables_info = {}
        
        for table in known_tables:
            try:
                # Try to get one row to see if the table exists
                result = client.table(table).select('*').limit(1).execute()
                if hasattr(result, 'data') and result.data:
                    # If successful, get the column names from the first row
                    tables_info[table] = list(result.data[0].keys())
            except Exception as e:
                # If there's an error, the table might not exist or we might not have permissions
                print(f"⚠️  Could not access table '{table}': {str(e)[:100]}...")
        
        return tables_info
        
    except Exception as e:
        print(f"❌ Error listing tables: {str(e)}")
        return {}

def main():
    """Main function to list tables and their columns"""
    print("🔍 Listing Supabase Tables and Columns")
    
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return
    
    tables = list_tables()
    
    if not tables:
        print("\n❌ No tables found or couldn't access the database.")
        print("Please check your Supabase credentials and database permissions.")
        return
    
    print(f"\n📋 Found {len(tables)} tables:")
    for table, columns in tables.items():
        print(f"\n📄 Table: {table}")
        print("-" * (len(table) + 9))
        for col in columns:
            print(f"  - {col}")
    
    # Save to a JSON file for reference
    with open('supabase_schema.json', 'w') as f:
        json.dump(tables, f, indent=2)
    print("\n💾 Schema saved to supabase_schema.json")

if __name__ == "__main__":
    load_dotenv()
    main()
