"""
Script to check RLS status using Supabase JavaScript client via pyodide
"""
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY]):
    raise ValueError("Missing required Supabase environment variables")

# JavaScript code to check RLS status
JS_CODE = """
async function checkRLS() {
    // Import Supabase client
    const { createClient } = supabase;
    
    // Initialize client
    const supabaseClient = createClient(SUPABASE_URL, SUPABASE_KEY);
    
    try {
        // Check if RLS is enabled for players table
        const { data: rlsStatus, error: statusError } = await supabaseClient
            .rpc('get_rls_status', { table_name: 'players' });
            
        if (statusError) throw statusError;
        
        // Get all policies for the players table
        const { data: policies, error: policiesError } = await supabaseClient
            .from('pg_policies')
            .select('*')
            .eq('tablename', 'players');
            
        if (policiesError) throw policiesError;
        
        return {
            rlsStatus,
            policies: policies || []
        };
    } catch (error) {
        return { error: error.message };
    }
}

// Execute and return the result
checkRLS();
"""

def check_rls():
    """Check RLS status using JavaScript client"""
    try:
        # Try to use Pyodide to run JavaScript
        import js
        from js import eval
        
        # Set up the environment for the JS code
        js.eval(f"var SUPABASE_URL = '{SUPABASE_URL}';")
        js.eval(f"var SUPABASE_KEY = '{SUPABASE_KEY}';")
        
        # Import Supabase in the JS environment
        js.eval("""
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2';
        script.async = true;
        script.onload = function() {
            window.supabase = supabase;
        };
        document.head.appendChild(script);
        """)
        
        # Execute the JS code and get the result
        result = eval(JS_CODE)
        
        # Convert the result to a Python dictionary
        if hasattr(result, 'to_py'):
            result = result.to_py()
            
        print("✅ RLS Check Results:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Error checking RLS: {str(e)}")
        print("\nAlternative approach: You can check RLS status manually in the Supabase dashboard:")
        print(f"1. Go to Authentication -> Policies")
        print(f"2. Select the 'players' table")
        print(f"3. Look for any RLS policies that might be blocking access")
        print("\nOr run this SQL in the Supabase SQL editor:")
        print("""
        -- Check if RLS is enabled for players table
        SELECT relname, relrowsecurity, relforcerowsecurity 
        FROM pg_class 
        WHERE oid = 'players'::regclass;
        
        -- Check RLS policies for players table
        SELECT * FROM pg_policies 
        WHERE tablename = 'players';
        """)

if __name__ == "__main__":
    print("🔍 Checking RLS configuration using JavaScript client...")
    check_rls()
