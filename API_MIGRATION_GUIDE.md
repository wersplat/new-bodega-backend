# API Migration Guide

## Overview

This guide helps developers migrate from the legacy API structure to the new flattened, versioned API structure. The new structure follows RESTful principles and provides better organization, versioning, and scalability.

## Migration Timeline

- **Immediate**: Both old and new endpoints are available
- **6 months**: Legacy endpoints will be marked as deprecated
- **12 months**: Legacy endpoints will be removed

## Endpoint Mapping

The following table maps legacy endpoints to their new counterparts:

| Legacy Endpoint | New Endpoint | Notes |
|----------------|--------------|-------|
| `/api/auth/*` | `/auth/*` | Authentication endpoints moved to root level |
| `/api/players/*` | `/v1/players/*` | Added versioning |
| `/api/events/*` | `/v1/events/*` | Added versioning |
| `/api/leaderboard/*` | `/v1/leaderboards/*` | Renamed to plural form |
| `/api/payments/*` | `/v1/integrations/payments/*` | Moved under integrations |
| `/api/admin/*` | `/v1/admin/*` | Added versioning |
| `/api/discord/*` | `/v1/integrations/discord/*` | Moved under integrations |
| `/api/teams/*` | `/v1/teams/*` | Added versioning |
| `/api/matches/*` | `/v1/matches/*` | Added versioning |
| `/api/player-stats/*` | `/v1/player-stats/*` | Added versioning |

## Automatic Redirects

For backward compatibility, all legacy endpoints are automatically redirected to their new counterparts. This means your existing applications will continue to work without immediate changes. However, we recommend updating your code to use the new endpoints as soon as possible.

## Code Examples

### JavaScript/TypeScript

#### Before:
```javascript
// Legacy API call
const response = await fetch('/api/players/123');
const player = await response.json();
```

#### After:
```javascript
// New API call
const response = await fetch('/v1/players/123');
const player = await response.json();
```

### Python

#### Before:
```python
# Legacy API call
import requests
response = requests.get('https://api.example.com/api/players/123')
player = response.json()
```

#### After:
```python
# New API call
import requests
response = requests.get('https://api.example.com/v1/players/123')
player = response.json()
```

## Benefits of the New API Structure

1. **Versioning**: The `/v1/` prefix allows for future API versions without breaking existing clients
2. **Consistency**: All resource endpoints follow the same pattern and naming conventions
3. **Discoverability**: Related endpoints are grouped together logically
4. **Scalability**: The structure can easily accommodate new resources and endpoints
5. **Maintainability**: Cleaner organization makes the API easier to document and maintain

## Best Practices for Migration

1. **Update API Client Libraries**: If you maintain client libraries, update them to use the new endpoints
2. **Test Thoroughly**: Test your application with the new endpoints before deploying to production
3. **Update Documentation**: Update any internal documentation to reflect the new API structure
4. **Monitor Errors**: Monitor for any errors that might occur during the transition
5. **Gradual Migration**: Consider migrating one endpoint at a time to minimize risk

## Need Help?

If you encounter any issues during migration, please contact our support team at support@example.com or open an issue on our GitHub repository.
