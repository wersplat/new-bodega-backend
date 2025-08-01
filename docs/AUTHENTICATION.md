# Authentication System

This document outlines the authentication system used in the NBA 2K Global Rankings backend, including Supabase authentication, JWT handling, and security considerations.

## Table of Contents
- [Authentication Flow](#authentication-flow)
- [Environment Variables](#environment-variables)
- [Supabase Authentication](#supabase-authentication)
- [JWT Authentication](#jwt-authentication)
- [Security Considerations](#security-considerations)
- [Testing Authentication](#testing-authentication)
- [Troubleshooting](#troubleshooting)

## Authentication Flow

1. **Client Authentication**:
   - Users authenticate through Supabase Auth
   - On successful authentication, Supabase returns a JWT
   - The JWT is stored client-side (typically in localStorage or cookies)

2. **API Requests**:
   - Include the JWT in the `Authorization: Bearer <token>` header
   - The backend verifies the JWT for protected routes
   - Row Level Security (RLS) enforces data access permissions

## Environment Variables

Required environment variables for authentication:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key

# JWT Configuration
SECRET_KEY=your-jwt-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Supabase Authentication

### Service Role Key
- **Purpose**: Full access to the database (bypasses RLS)
- **Usage**: Server-side operations only
- **Environment Variable**: `SUPABASE_KEY`

### Anonymous Key
- **Purpose**: Client-side operations with RLS restrictions
- **Usage**: Public API endpoints and client-side code
- **Environment Variable**: `SUPABASE_ANON_KEY`

## JWT Authentication

### Token Generation
Tokens are generated by Supabase Auth and contain the following claims:

```json
{
  "sub": "user-id",
  "email": "user@example.com",
  "role": "authenticated",
  "exp": 1754098735
}
```

### Token Verification
1. Extract token from `Authorization` header
2. Verify signature using `SECRET_KEY`
3. Check token expiration
4. Validate required claims

### Example Protected Route

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except jwt.PyJWTError:
        raise credentials_exception
```

## Security Considerations

1. **Never expose the service role key in client-side code**
2. **Use HTTPS** for all API requests
3. **Set appropriate token expiration times**
4. **Implement refresh tokens** for long-lived sessions
5. **Enable CORS** only for trusted origins
6. **Rate limit** authentication endpoints

## Testing Authentication

### Test Scripts
- `scripts/check_auth.py`: Tests Supabase and JWT authentication
- `scripts/check_rls_simple.py`: Tests Row Level Security policies

### Running Tests

```bash
# Test authentication
python scripts/check_auth.py

# Test RLS policies
python scripts/check_rls_simple.py
```

## Troubleshooting

### Common Issues

#### 1. Authentication Failing
- Verify environment variables are set correctly
- Check Supabase project is running
- Ensure the JWT secret key matches between client and server

#### 2. RLS Policy Issues
- Check RLS policies in Supabase dashboard
- Verify the service role key is being used for admin operations
- Test with `check_rls_simple.py` to diagnose RLS problems

#### 3. Token Validation Failures
- Check token expiration
- Verify the signing algorithm matches
- Ensure the secret key hasn't changed

### Getting Help
For additional support, refer to:
- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [JWT.io](https://jwt.io/) for JWT debugging
- Project issue tracker for known issues
