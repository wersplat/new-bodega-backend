"""
Script to inspect the Supabase database schema using direct SQL queries
"""
import os
from dotenv import load_dotenv
from app.core.supabase import supabase

def get_table_columns(table_name: str) -> list:
    """Get column information for a specific table using information_schema"""
    client = supabase.get_client()
    
    # SQL query to get column information
    query = """
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_name = %(table_name)s
    ORDER BY ordinal_position;
    """
    
    try:
        # Use rpc to execute raw SQL with parameters
        result = client.rpc('rpc', {
            'query': query,
            'params': {'table_name': table_name}
        }).execute()
        
        if hasattr(result, 'data') and result.data:
            return result.data
        return []
    except Exception as e:
        print(f"Error getting columns for table {table_name}: {str(e)}")
        return []

def list_tables() -> list:
    """List all tables in the public schema"""
    client = supabase.get_client()
    
    # SQL query to list all tables
    query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    ORDER BY table_name;
    """
    
    try:
        result = client.rpc('rpc', {
            'query': query,
            'params': {}
        }).execute()
        
        if hasattr(result, 'data') and result.data:
            return [table['table_name'] for table in result.data]
        return []
    except Exception as e:
        print(f"Error listing tables: {str(e)}")
        return []

def main():
    """Main function to inspect the database schema"""
    print("🔍 Inspecting Supabase Database Schema")
    
    # List all tables
    print("\n📋 Listing all tables:")
    tables = list_tables()
    
    if not tables:
        print("No tables found or couldn't list tables.")
        return
    
    for i, table in enumerate(tables, 1):
        print(f"{i}. {table}")
    
    # Get columns for each table
    print("\n📊 Table Schemas:")
    for table in tables:
        columns = get_table_columns(table)
        if columns:
            print(f"\nTable: {table}")
            print("-" * (len(table) + 7))
            for col in columns:
                print(f"  - {col['column_name']} ({col['data_type']}) "
                      f"{'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
        else:
            print(f"\nTable: {table} (could not retrieve schema)")

if __name__ == "__main__":
    # Check if Supabase credentials are set
    load_dotenv()
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    else:
        main()
