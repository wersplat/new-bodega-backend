"""
Script to test Supabase authentication and JWT functionality
"""
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client
import jwt
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

def test_key(key_type: str, key: str, supabase_url: str):
    """Test authentication with a specific key type"""
    print(f"\n🔐 Testing {key_type} key...")
    
    try:
        # Initialize client with the specified key
        supabase = create_client(supabase_url, key)
        
        # Test authentication
        print("   Testing authentication...")
        auth_response = supabase.auth.get_user()
        
        if auth_response and hasattr(auth_response, 'user'):
            print(f"   ✅ Authenticated as: {auth_response.user.email or 'Service Role'}")
        else:
            print("   ℹ️ Not authenticated (expected for anonymous key)")
        
        # Test a simple query
        print("   Testing players table access...")
        result = supabase.table("players").select("*").limit(1).execute()
        
        if hasattr(result, 'data'):
            print(f"   ✅ Successfully queried players table ({len(result.data)} rows)")
            return True
        else:
            print("   ❌ Failed to query players table")
            return False
            
    except Exception as e:
        print(f"   ❌ Error with {key_type} key: {str(e)}")
        return False

def test_jwt_auth() -> bool:
    """Test JWT token generation and verification"""
    print("\n🔐 Testing JWT Authentication...")
    
    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM", "HS256")
    
    if not secret_key:
        print("❌ SECRET_KEY not found in environment variables")
        return False
    
    # Test JWT token creation
    try:
        # Create a test token
        payload = {
            "sub": "test_user_id",
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "role": "authenticated"
        }
        
        token = jwt.encode(payload, secret_key, algorithm=algorithm)
        print(f"✅ Successfully created JWT token: {token[:50]}...")
        
        # Test token verification
        try:
            decoded = jwt.decode(token, secret_key, algorithms=[algorithm])
            print(f"✅ Successfully verified JWT token")
            print(f"   Payload: {decoded}")
            return True
            
        except jwt.ExpiredSignatureError:
            print("❌ Token verification failed: Token has expired")
        except jwt.InvalidTokenError as e:
            print(f"❌ Token verification failed: {str(e)}")
            
    except Exception as e:
        print(f"❌ Error during JWT operations: {str(e)}")
        
    return False

def main():
    """Main function to test authentication"""
    print("🔍 Testing Authentication...")
    
    # Get environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_KEY")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    secret_key = os.getenv("SECRET_KEY")
    
    # Test Supabase authentication
    supabase_tests = True
    if all([supabase_url, service_key, anon_key]):
        print("\n🔐 Testing Supabase Authentication...")
        service_success = test_key("Service Role", service_key, supabase_url)
        anon_success = test_key("Anonymous", anon_key, supabase_url)
        supabase_tests = service_success and anon_success
    else:
        print("⚠️  Skipping Supabase tests - missing URL or keys")
        supabase_tests = False
    
    # Test JWT authentication
    jwt_success = test_jwt_auth() if secret_key else False
    
    # Print summary
    print("\n" + "="*50)
    print("AUTHENTICATION TEST SUMMARY:")
    
    if supabase_url and service_key and anon_key:
        print(f"- Supabase Service Role: {'✅ Success' if service_success else '❌ Failed'}")
        print(f"- Supabase Anonymous:    {'✅ Success' if anon_success else '❌ Failed'}")
    
    print(f"- JWT Authentication:   {'✅ Success' if jwt_success else '❌ Failed'}")
    
    # Print troubleshooting info if needed
    if not all([supabase_tests, jwt_success]):
        print("\nTROUBLESHOOTING:")
        
        if not supabase_tests:
            if not all([supabase_url, service_key, anon_key]):
                print("1. Missing Supabase environment variables. Please check your .env file:")
                print("   - SUPABASE_URL")
                print("   - SUPABASE_KEY (service role key)")
                print("   - SUPABASE_ANON_KEY")
            else:
                print("1. Check your Supabase project settings and RLS policies")
        
        if not jwt_success:
            if not secret_key:
                print("2. SECRET_KEY is missing from environment variables")
            else:
                print("2. Check your JWT configuration (SECRET_KEY and ALGORITHM)")

if __name__ == "__main__":
    main()
