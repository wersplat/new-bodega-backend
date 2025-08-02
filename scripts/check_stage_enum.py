import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database connection parameters from environment variables
DB_URL = os.getenv("DATABASE_URL")  # Should be in format: postgresql://user:password@host:port/dbname

if not DB_URL:
    print("❌ Error: DATABASE_URL environment variable not set")
    exit(1)

try:
    # Connect to the database
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    # Query to get all enum types and their values
    cursor.execute("""
        SELECT t.typname AS enum_name, 
               e.enumlabel AS enum_value
        FROM pg_type t 
        JOIN pg_enum e ON t.oid = e.enumtypid  
        JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        WHERE n.nspname = 'public'
        ORDER BY enum_name, e.enumsortorder;
    """)
    
    # Get the results
    enums = {}
    for enum_name, enum_value in cursor.fetchall():
        if enum_name not in enums:
            enums[enum_name] = []
        enums[enum_name].append(enum_value)
    
    # Print the results
    if enums:
        print("✅ Found the following enum types and values:")
        for enum_name, values in enums.items():
            print(f"\nEnum: {enum_name}")
            print(f"Values: {', '.join(values)}")
    else:
        print("No enum types found in the database.")
    
    # Close the connection
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error querying the database: {e}")
    exit(1)
