# Rate Limiting Issue

## Problem
The `slowapi` middleware is causing a deployment error:
```
Exception: parameter `response` must be an instance of starlette.responses.Response
```

### Error Details
- **Location**: `slowapi/extension.py`, line 382 in `_inject_headers` method
- **Trigger**: Processing responses from endpoints, particularly `RedirectResponse` objects
- **Stack Trace**: Shows the error propagating through the middleware chain
- **Frequency**: Occurs on every request to affected endpoints

## Current Status
- Rate limiting has been temporarily disabled in both `main.py` and `main_supabase.py`
- The application works correctly without rate limiting
- All endpoints are functional
- The error has been resolved by disabling the slowapi middleware

## Root Cause
The issue appears to be a compatibility problem between:
- `slowapi` version 0.1.8/0.1.9
- FastAPI/Starlette versions
- Python 3.11
- Specific incompatibility with `RedirectResponse` objects in the legacy API redirect endpoint

## Temporary Solution
Rate limiting middleware and decorators have been commented out in both main files:
```python
# app.add_exception_handler(429, rate_limit_exceeded_handler)
# app.add_middleware(SlowAPIMiddleware)
# @limiter.limit(settings.RATE_LIMIT_DEFAULT)
# @limiter.exempt
```

### Changes Made
1. **Disabled slowapi middleware**: Commented out `app.add_middleware(SlowAPIMiddleware)`
2. **Commented rate limiting decorators**: Disabled all `@limiter.limit()` and `@limiter.exempt` decorators
3. **Added explicit status codes**: Added `status_code=307` to `RedirectResponse` objects for better compatibility

## Next Steps
1. Investigate alternative rate limiting solutions
2. Check for newer versions of `slowapi`
3. Consider implementing custom rate limiting middleware
4. Test with different FastAPI/Starlette versions

## Files Modified
- `main.py` - Rate limiting disabled, slowapi middleware commented out
- `main_supabase.py` - Rate limiting disabled (already documented)

## Impact
- **Positive**: Application now starts without errors and all endpoints are functional
- **Negative**: No rate limiting protection is currently active
- **Security**: Consider implementing alternative rate limiting or monitoring for abuse
