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
    # Get a sample of tournaments to see what tier values are used
    response = supabase.table("tournaments").select("tier").limit(10).execute()
    
    if hasattr(response, 'data') and response.data:
        print("✅ Found the following tournament tier values in existing tournaments:")
        tiers = set()
        for t in response.data:
            if 'tier' in t and t['tier']:
                tiers.add(t['tier'])
        
        if tiers:
            print("Valid tournament tier values:")
            for tier in sorted(tiers):
                print(f"- {tier}")
        else:
            print("No tier values found in existing tournaments")
    else:
        print("❌ No tournaments found in the database")
        
except Exception as e:
    print(f"❌ Error querying tournaments: {e}")
