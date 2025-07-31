import os
from dotenv import load_dotenv
from app.core.supabase import supabase

def test_supabase_connection():
    try:
        # Test connection by fetching a table (use a table that exists in your Supabase)
        # Replace 'test_table' with an actual table name in your Supabase
        response = supabase.get_client().table('test_table').select("*").limit(1).execute()
        print("✅ Successfully connected to Supabase!")
        print("Response:", response.data)
    except Exception as e:
        print("❌ Error connecting to Supabase:")
        print(str(e))

if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env file
    
    # Check if required environment variables are set
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        print(f"SUPABASE_URL: {'✅' if os.getenv('SUPABASE_URL') else '❌'}")
        print(f"SUPABASE_KEY: {'✅' if os.getenv('SUPABASE_KEY') else '❌'}")
    else:
        print("🔍 Testing Supabase connection...")
        print(f"Supabase URL: {os.getenv('SUPABASE_URL')}")
        test_supabase_connection()
