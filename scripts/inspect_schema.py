"""
Script to inspect the Supabase database schema
"""
import os
from dotenv import load_dotenv
from app.core.supabase import supabase

def get_table_columns(table_name: str) -> list:
    """Get column information for a specific table"""
    client = supabase.get_client()
    
    # This is a workaround to get column information since Supabase doesn't have a direct API for this
    # We'll try to get one row to see the structure
    try:
        result = client.table(table_name).select("*").limit(1).execute()
        if result.data:
            # Return the column names from the first row
            return list(result.data[0].keys())
        else:
            # If no data, try to get the schema from the error message
            try:
                # This will fail but might give us the column names in the error
                client.table(table_name).select("non_existent_column").execute()
            except Exception as e:
                error_msg = str(e)
                if "Could not find the" in error_msg and "column of" in error_msg:
                    # Extract the column name from the error message
                    column_part = error_msg.split("'")[1]
                    return [column_part]
            return []
    except Exception as e:
        print(f"Error getting columns for table {table_name}: {str(e)}")
        return []

def list_tables():
    """List all tables in the database"""
    # This is a workaround since Supabase doesn't have a direct API for listing tables
    # We'll try to get a list of tables from the type information
    client = supabase.get_client()
    
    # Try to get a list of tables by querying a known system table or view
    try:
        # This is a common PostgreSQL system view that lists tables
        result = client.rpc('pg_tables', {}).execute()
        if hasattr(result, 'data'):
            return [table['tablename'] for table in result.data 
                   if table['schemaname'] == 'public' and 
                   not table['tablename'].startswith('pg_') and
                   not table['tablename'].startswith('sql_')]
    except Exception as e:
        print(f"Error listing tables: {str(e)}")
    
    # If the above fails, try to get tables from the type information
    try:
        # This might work if the Supabase client has type information
        return list(client.table('').__dict__.get('_table_names', []))
    except Exception as e:
        print(f"Error getting table names from client: {str(e)}")
    
    return []

def main():
    """Main function to inspect the database schema"""
    print("🔍 Inspecting Supabase Database Schema")
    
    # List all tables
    print("\n📋 Listing all tables:")
    tables = list_tables()
    for i, table in enumerate(tables, 1):
        print(f"{i}. {table}")
    
    if not tables:
        print("No tables found or couldn't list tables.")
        return
    
    # Get columns for each table
    print("\n📊 Table Schemas:")
    for table in tables:
        columns = get_table_columns(table)
        if columns:
            print(f"\nTable: {table}")
            print("-" * (len(table) + 7))
            for col in columns:
                print(f"  - {col}")
        else:
            print(f"\nTable: {table} (could not retrieve schema)")

if __name__ == "__main__":
    # Check if Supabase credentials are set
    load_dotenv()
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    else:
        main()
