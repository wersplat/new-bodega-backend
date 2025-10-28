# New Endpoints Quick Reference

## Achievements System

### Achievements
```bash
# List achievements
GET /v1/achievements/?category=Scoring&rarity=Legendary

# Get achievement
GET /v1/achievements/{id}

# Create achievement (admin)
POST /v1/achievements/
{
  "name": "Triple Threat",
  "description": "Score 50+ points, 10+ assists, 10+ rebounds in one game",
  "category": "Mixed Stats",
  "rarity": "Legendary",
  "rp_value": 500,
  "is_player": true
}

# Get player achievements
GET /v1/achievements/player/{player_id}?tier=gold
```

### Achievement Rules
```bash
# List rules
GET /v1/achievements/rules/?achievement_name=Triple Threat&is_active=true

# Create rule (admin)
POST /v1/achievements/rules/
{
  "name": "Triple Threat",
  "tier": "gold",
  "scope": "per_game",
  "predicate": {
    "points": {"gte": 50},
    "assists": {"gte": 10},
    "rebounds": {"gte": 10}
  }
}
```

---

## Events System

### Event Results
```bash
# List event results
GET /v1/events/results/?team_id={team_id}&tournament_id={tournament_id}

# Create event result (admin)
POST /v1/events/results/
{
  "team_id": "uuid",
  "placement": 1,
  "rp_awarded": 1000,
  "bonus_rp": 200,
  "prize_amount": 5000,
  "tournament_id": "uuid"
}

# Get team results
GET /v1/events/team/{team_id}/results
```

### Event Tiers
```bash
# List tiers
GET /v1/events/tiers/?event_type=Tournament

# Get tier
GET /v1/events/tiers/{tier_id}
```

### Event Queue (Admin)
```bash
# List queue
GET /v1/events/queue/?status=error

# Retry failed item
POST /v1/events/queue/{queue_id}/retry
```

---

## Notifications

```bash
# List my notifications
GET /v1/notifications/?read=false&page=1&size=20

# Get unread count
GET /v1/notifications/unread/count

# Mark as read
PUT /v1/notifications/{notification_id}/read

# Mark all as read
PUT /v1/notifications/mark-all-read

# Create notification (admin)
POST /v1/notifications/
{
  "title": "Tournament Starting Soon",
  "message": "UPA Season 5 playoffs begin in 1 hour!",
  "type": "info",
  "user_id": null  // null = broadcast to all users
}
```

---

## Match Queue

### Player Queue
```bash
# Create queue session
POST /v1/match-queue/sessions/
{
  "guild_id": "discord_guild_id",
  "channel_id": "discord_channel_id",
  "required_positions": ["Point Guard", "Shooting Guard", "Lock", "Power Forward", "Center"],
  "skill_range": 200
}

# Join queue
POST /v1/match-queue/sessions/{session_id}/join
{
  "discord_id": "user_discord_id",
  "position": "Point Guard",
  "player_id": "player_uuid"
}

# Leave queue
POST /v1/match-queue/sessions/{session_id}/leave?discord_id={discord_id}

# List slots
GET /v1/match-queue/sessions/{session_id}/slots
```

### Team Queue
```bash
# Create team queue session
POST /v1/match-queue/team/sessions/?guild_id={guild}&channel_id={channel}

# Join with team
POST /v1/match-queue/team/sessions/{session_id}/join
{
  "team_id": "team_uuid",
  "captain_discord_id": "captain_discord_id",
  "captain_player_id": "player_uuid",
  "roster_source": "league",
  "selected_league_id": "league_uuid",
  "selected_season_id": "season_uuid"
}

# Get team lineup
GET /v1/match-queue/team/sessions/{session_id}/slots/{slot_id}/lineup
```

### Active Queues
```bash
# Get all active queues
GET /v1/match-queue/active/?guild_id={guild_id}
```

---

## League Enhancements

```bash
# Get league calendar
GET /leagues/{league_id}/calendar

# Get standings
GET /leagues/{league_id}/standings?season_id={season_id}

# Get performance
GET /leagues/{league_id}/performance?season_id={season_id}

# Get RP values
GET /leagues/{league_id}/rp-values?game_year=2K25

# Get divisions
GET /leagues/{league_id}/divisions?season_id={season_id}

# Get season open tournament
GET /leagues/seasons/{season_id}/open

# Get season playoff
GET /leagues/seasons/{season_id}/playoff

# Get season player stats
GET /leagues/seasons/{season_id}/player-stats?stage=regular_season

# Get season teams
GET /leagues/seasons/{season_id}/teams
```

---

## Player Analytics

```bash
# Performance mart (comprehensive analytics)
GET /v1/player-stats/player/{player_id}/performance-mart

# Hot streak (recent form)
GET /v1/player-stats/player/{player_id}/hot-streak

# Stats tracking (milestones)
GET /v1/player-stats/player/{player_id}/tracking

# Season breakdown
GET /v1/player-stats/player/{player_id}/season-stats?season_id={season_id}

# Stats by game year
GET /v1/player-stats/player/{player_id}/by-game-year

# Global rating
GET /v1/player-stats/player/{player_id}/global-rating

# Roster history
GET /v1/player-stats/player/{player_id}/roster-history?limit=50&offset=0

# Public profile
GET /v1/player-stats/player/{player_id}/public-profile
```

---

## Team Analytics

```bash
# Comprehensive analytics
GET /v1/teams/{team_id}/analytics

# Momentum indicators
GET /v1/teams/{team_id}/momentum

# Roster value analysis
GET /v1/teams/{team_id}/roster-value

# Performance by game year
GET /v1/teams/{team_id}/by-game-year

# Performance overview
GET /v1/teams/{team_id}/performance-view

# Head-to-head matchup
GET /v1/teams/{team_id}/head-to-head/{opponent_team_id}
```

---

## Response Examples

### Achievement Response
```json
{
  "id": "uuid",
  "name": "Triple Threat",
  "description": "Score 50+ points with 10+ assists and rebounds",
  "type": "Mixed Stats",
  "category": "Mixed Stats",
  "rarity": "Legendary",
  "achievement_badge": "https://...",
  "rp_value": 500,
  "is_player": true,
  "is_team": false,
  "created_at": "2025-01-15T10:30:00Z"
}
```

### Notification Response
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "New Achievement Unlocked!",
  "message": "You earned Triple Threat!",
  "type": "success",
  "read": false,
  "created_at": "2025-10-28T10:30:00Z",
  "updated_at": "2025-10-28T10:30:00Z"
}
```

### Player Performance Mart Response
```json
{
  "player_id": "uuid",
  "gamertag": "ProGamer123",
  "games_played": 150,
  "avg_points": 22.5,
  "avg_assists": 6.3,
  "avg_rebounds": 8.1,
  "global_rating": 1850,
  "rating_tier": "A",
  "recent_avg_points": 25.4,
  "recent_games": 10,
  "team_name": "Elite Squad",
  "current_team_id": "uuid"
}
```

### Team Analytics Response
```json
{
  "team_id": "uuid",
  "team_name": "Elite Squad",
  "games_played": 50,
  "wins": 35,
  "losses": 15,
  "win_percentage": 70.0,
  "current_rp": 2500,
  "elo_rating": 1750,
  "roster_size": 8,
  "elite_players": 2,
  "avg_player_rating": 1650,
  "total_achievements": 45
}
```

---

## Common Query Parameters

### Pagination:
- `limit` or `size`: Number of items (default: varies, max: 1000)
- `offset` or `page`: Starting position or page number
- `skip`: Alternative to offset

### Filtering:
- `league_id`: Filter by league UUID
- `tournament_id`: Filter by tournament UUID
- `season_id`: Filter by season UUID
- `game_year`: Filter by game year (2K24, 2K25, etc)
- `status`: Filter by status
- `tier`: Filter by tier (T1-T5)

### Sorting:
- `sort_by`: Field to sort by
- `sort_order`: asc or desc

---

## Error Codes

- `400` - Bad Request (invalid input)
- `401` - Unauthorized (not authenticated)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `409` - Conflict (duplicate or constraint violation)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

---

*Quick Reference - October 28, 2025*

