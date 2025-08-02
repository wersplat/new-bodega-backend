# NBA 2K Global Rankings API Documentation

## Overview

This document provides comprehensive documentation for the NBA 2K Global Rankings API. The API follows RESTful principles with a flattened, versioned structure for improved maintainability and scalability.

## Base URL

```
https://api.example.com
```

Replace `api.example.com` with the actual domain where the API is hosted.

## API Versioning

All API endpoints (except authentication) are versioned to ensure backward compatibility as the API evolves. The current version is `v1`.

## Authentication

Authentication endpoints are available at the root level for ease of access.

### Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/login` | POST | Authenticate a user and receive access tokens |
| `/auth/register` | POST | Register a new user account |
| `/auth/refresh` | POST | Refresh an expired access token |
| `/auth/logout` | POST | Invalidate the current access token |

## API Resources

### Players

Player profiles and statistics.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/players` | GET | List all players with optional filtering |
| `/v1/players/{player_id}` | GET | Get a specific player's profile |
| `/v1/players/{player_id}` | PUT | Update a player's profile |
| `/v1/players/{player_id}` | DELETE | Delete a player's profile |
| `/v1/players/search` | GET | Search for players by name or attributes |
| `/v1/players/{player_id}/stats` | GET | Get a player's statistics |

### Teams

Team management and rosters.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/teams` | GET | List all teams with optional filtering |
| `/v1/teams` | POST | Create a new team |
| `/v1/teams/{team_id}` | GET | Get a specific team's details |
| `/v1/teams/{team_id}` | PUT | Update a team's details |
| `/v1/teams/{team_id}` | DELETE | Delete a team |
| `/v1/teams/{team_id}/players` | GET | Get all players on a team |
| `/v1/teams/{team_id}/players/{player_id}` | POST | Add a player to a team |
| `/v1/teams/{team_id}/players/{player_id}` | DELETE | Remove a player from a team |

### Events

Tournament and league events.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/events` | GET | List all events with optional filtering |
| `/v1/events` | POST | Create a new event |
| `/v1/events/{event_id}` | GET | Get a specific event's details |
| `/v1/events/{event_id}` | PUT | Update an event's details |
| `/v1/events/{event_id}` | DELETE | Delete an event |
| `/v1/events/{event_id}/register` | POST | Register for an event |
| `/v1/events/{event_id}/unregister` | POST | Unregister from an event |
| `/v1/events/{event_id}/participants` | GET | List all participants in an event |

### Matches

Match results and statistics.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/matches` | GET | List all matches with optional filtering |
| `/v1/matches` | POST | Create a new match |
| `/v1/matches/{match_id}` | GET | Get a specific match's details |
| `/v1/matches/{match_id}` | PUT | Update a match's details |
| `/v1/matches/{match_id}` | DELETE | Delete a match |
| `/v1/matches/{match_id}/stats` | GET | Get statistics for a match |

### Leaderboards

Player and team rankings.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/leaderboards/global` | GET | Get the global leaderboard |
| `/v1/leaderboards/region/{region}` | GET | Get a regional leaderboard |
| `/v1/leaderboards/event/{event_id}` | GET | Get an event-specific leaderboard |
| `/v1/leaderboards/tier/{tier}` | GET | Get a tier-specific leaderboard |

### Player Stats

Detailed player statistics and performance metrics.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/player-stats` | GET | List all player stats with optional filtering |
| `/v1/player-stats/{player_id}` | GET | Get a specific player's detailed stats |
| `/v1/player-stats/{player_id}/averages` | GET | Get a player's average statistics |
| `/v1/player-stats/{player_id}/history` | GET | Get a player's statistical history |

### Admin

Administrative operations (requires admin privileges).

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/admin/users` | GET | List all users |
| `/v1/admin/users/{user_id}` | GET | Get a specific user's details |
| `/v1/admin/users/{user_id}` | PUT | Update a user's details |
| `/v1/admin/users/{user_id}/role` | PUT | Update a user's role |

### Integrations

#### Discord Integration

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/integrations/discord/webhook` | POST | Receive Discord webhook events |
| `/v1/integrations/discord/link` | POST | Link a Discord account to a player profile |
| `/v1/integrations/discord/unlink` | POST | Unlink a Discord account from a player profile |

#### Payment Integration

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/integrations/payments/checkout` | POST | Create a payment checkout session |
| `/v1/integrations/payments/webhook` | POST | Receive payment webhook events |
| `/v1/integrations/payments/history` | GET | Get payment history for the authenticated user |

## Health Check

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API root - provides basic API information |
| `/health` | GET | Health check endpoint for monitoring |

## Query Parameters

Most list endpoints support the following query parameters:

| Parameter | Description |
|-----------|-------------|
| `limit` | Maximum number of results to return (default: 20, max: 100) |
| `offset` | Number of results to skip (for pagination) |
| `sort` | Field to sort by (prefix with `-` for descending order) |
| `fields` | Comma-separated list of fields to include in the response |
| `filter` | Filter results by specific criteria |

## Response Format

All API responses follow a consistent JSON format:

```json
{
  "data": [],       // The main response data (array or object)
  "meta": {         // Metadata about the response
    "count": 0,     // Total count of results
    "limit": 20,    // Limit used for the query
    "offset": 0     // Offset used for the query
  },
  "error": null     // Error information (null if no error)
}
```

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests. In case of an error, the response will include an `error` object with details:

```json
{
  "data": null,
  "meta": {},
  "error": {
    "code": "ERROR_CODE",
    "message": "A human-readable error message",
    "details": {}  // Additional error details if available
  }
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse. Rate limit information is included in the response headers:

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Maximum number of requests allowed in the current period |
| `X-RateLimit-Remaining` | Number of requests remaining in the current period |
| `X-RateLimit-Reset` | Time when the rate limit will reset (Unix timestamp) |

## Backward Compatibility

For backward compatibility, all legacy endpoints under `/api/*` are automatically redirected to their corresponding new endpoints. However, it is recommended to update client applications to use the new endpoint structure.

## API Changes and Deprecation Policy

- API changes will be communicated through the API changelog
- Deprecated endpoints will be marked with a `Deprecated` header
- Deprecated endpoints will be supported for at least 6 months before removal
