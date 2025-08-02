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
    # Get a sample of events to see what tier values are used
    response = supabase.table("events").select("tier").limit(10).execute()
    
    if hasattr(response, 'data') and response.data:
        print("✅ Found the following tier values in existing events:")
        tiers = set()
        for event in response.data:
            if 'tier' in event:
                tiers.add(event['tier'])
        
        if tiers:
            print("Valid tier values:")
            for tier in sorted(tiers):
                print(f"- {tier}")
        else:
            print("No tier values found in existing events")
    else:
        print("❌ No events found in the database")
        
except Exception as e:
    print(f"❌ Error querying events: {e}")
