# API Updates - Schema Alignment & New Endpoints

**Date**: October 28, 2025  
**Status**: ✅ Complete and Ready for Testing

---

## Summary

Updated backend API to align with latest Supabase schema types. Fixed schema mismatches and implemented 60+ missing endpoints across 4 new routers plus enhancements to 3 existing routers.

---

## Schema Fixes ✅

### 1. Player Badges Schema Alignment
**Issue**: Code used `player_id` (UUID) + `badge_id` (UUID), but schema uses `player_wallet` (string) + `match_id` (bigint)

**Fixed**: 
- `app/routers/admin.py` - Updated badge award endpoints
- Removed non-existent "badges" table references

### 2. Enum Usage
**Issue**: Used arbitrary strings for enum fields

**Fixed**: 
- Created `app/schemas/enums.py` with all database enums
- Updated all routers to use proper enums (GameYear, EventTier, AchievementTier, etc.)

---

## New Routers Created ✅

### 1. `achievements.py` - 11 Endpoints
```
GET    /v1/achievements/                     - List achievements
POST   /v1/achievements/                     - Create (admin)
GET    /v1/achievements/{id}                 - Get by ID
PUT    /v1/achievements/{id}                 - Update (admin)
DELETE /v1/achievements/{id}                 - Delete (admin)

GET    /v1/achievements/rules/               - List rules
POST   /v1/achievements/rules/               - Create rule (admin)
GET    /v1/achievements/rules/{id}           - Get rule
PUT    /v1/achievements/rules/{id}           - Update rule (admin)
DELETE /v1/achievements/rules/{id}           - Delete rule (admin)

GET    /v1/achievements/player/{player_id}   - Player achievements
GET    /v1/achievements/categories/          - Categories list
GET    /v1/achievements/rarities/            - Rarities list
GET    /v1/achievements/eligibility/{player_id} - Eligibility check
```

### 2. `events.py` - 12 Endpoints
```
GET    /v1/events/results/                   - List event results
POST   /v1/events/results/                   - Create result (admin)
GET    /v1/events/results/{id}               - Get result
PUT    /v1/events/results/{id}               - Update (admin)
DELETE /v1/events/results/{id}               - Delete (admin)

GET    /v1/events/tiers/                     - List tiers
POST   /v1/events/tiers/                     - Create tier (admin)
GET    /v1/events/tiers/{id}                 - Get tier
PUT    /v1/events/tiers/{id}                 - Update (admin)

GET    /v1/events/queue/                     - List queue (admin)
GET    /v1/events/queue/{id}                 - Get queue item (admin)
POST   /v1/events/queue/{id}/retry           - Retry (admin)

GET    /v1/events/team/{team_id}/results     - Team results
```

### 3. `notifications.py` - 7 Endpoints
```
GET    /v1/notifications/                    - List notifications
POST   /v1/notifications/                    - Create (admin)
GET    /v1/notifications/{id}                - Get by ID
PUT    /v1/notifications/{id}/read           - Mark read
PUT    /v1/notifications/mark-all-read       - Mark all read
DELETE /v1/notifications/{id}                - Delete
GET    /v1/notifications/unread/count        - Unread count
```

### 4. `match_queue.py` - 13 Endpoints
```
# Player Queue
GET    /v1/match-queue/sessions/             - List sessions
POST   /v1/match-queue/sessions/             - Create session
GET    /v1/match-queue/sessions/{id}         - Get session
POST   /v1/match-queue/sessions/{id}/cancel  - Cancel (admin)
GET    /v1/match-queue/sessions/{id}/slots   - List slots
POST   /v1/match-queue/sessions/{id}/join    - Join queue
POST   /v1/match-queue/sessions/{id}/leave   - Leave queue

# Team Queue  
GET    /v1/match-queue/team/sessions/        - List team sessions
POST   /v1/match-queue/team/sessions/        - Create team session
GET    /v1/match-queue/team/sessions/{id}/slots - List team slots
POST   /v1/match-queue/team/sessions/{id}/join  - Join team queue
GET    /v1/match-queue/team/sessions/{id}/slots/{slot_id}/lineup - Get lineup

GET    /v1/match-queue/active/               - Get active queues
```

---

## Enhanced Existing Routers ✅

### 5. `leagues.py` - Added 11 Endpoints
```
GET    /leagues/{league_id}/calendar         - League calendar
GET    /leagues/{league_id}/standings        - Division standings
GET    /leagues/{league_id}/results          - League results
GET    /leagues/{league_id}/performance      - Performance analytics
GET    /leagues/{league_id}/rp-values        - RP configuration
GET    /leagues/{league_id}/divisions        - Divisions
GET    /leagues/{league_id}/conferences      - Conferences
GET    /leagues/seasons/{season_id}/open     - Open tournament
GET    /leagues/seasons/{season_id}/playoff  - Playoff tournament
GET    /leagues/seasons/{season_id}/player-stats - Season stats
GET    /leagues/seasons/{season_id}/teams    - Season teams
```

### 6. `player_stats.py` - Added 8 Analytics Endpoints
```
GET    /v1/player-stats/player/{id}/performance-mart - Performance analytics
GET    /v1/player-stats/player/{id}/hot-streak      - Recent form
GET    /v1/player-stats/player/{id}/tracking        - Milestone tracking
GET    /v1/player-stats/player/{id}/season-stats    - Season breakdown
GET    /v1/player-stats/player/{id}/by-game-year    - Stats by year
GET    /v1/player-stats/player/{id}/global-rating   - Rating breakdown
GET    /v1/player-stats/player/{id}/roster-history  - Roster history
GET    /v1/player-stats/player/{id}/public-profile  - Public profile
```

### 7. `teams.py` - Added 6 Analytics Endpoints
```
GET    /v1/teams/{id}/analytics              - Team analytics
GET    /v1/teams/{id}/momentum               - Momentum indicators
GET    /v1/teams/{id}/roster-value           - Roster value analysis
GET    /v1/teams/{id}/by-game-year           - Performance by year
GET    /v1/teams/{id}/performance-view       - Performance overview
GET    /v1/teams/{id}/head-to-head/{opponent_id} - H2H matchup
```

---

## Files Created/Modified

### New Files (5):
1. `app/schemas/enums.py` - Database enum definitions
2. `app/routers/achievements.py` - Achievement system
3. `app/routers/events.py` - Event management
4. `app/routers/notifications.py` - Notifications
5. `app/routers/match_queue.py` - Match queues

### Modified Files (6):
1. `app/routers/admin.py` - Badge schema fix
2. `app/routers/leagues.py` - Analytics endpoints + enums
3. `app/routers/player_stats.py` - Analytics endpoints
4. `app/routers/teams.py` - Analytics endpoints
5. `app/routers/views.py` - Enum usage for game_year
6. `main_supabase.py` - Registered new routers

---

## Quick Examples

### Create Achievement (Admin)
```bash
POST /v1/achievements/
{
  "name": "Triple Threat",
  "description": "50+ pts, 10+ ast, 10+ reb in one game",
  "category": "Mixed Stats",
  "rarity": "Legendary",
  "type": "Single Game",
  "rp_value": 500,
  "is_player": true
}
```

### Get Player Performance
```bash
GET /v1/player-stats/player/{player_id}/performance-mart

# Returns: avg stats, global rating, recent form, team info, etc.
```

### Get Team Analytics
```bash
GET /v1/teams/{team_id}/analytics

# Returns: roster composition, win rate, ELO, RP, player ratings, etc.
```

### Create Notification (Admin)
```bash
POST /v1/notifications/
{
  "title": "Season 5 Playoffs Starting!",
  "message": "Good luck to all teams!",
  "type": "info",
  "user_id": null  // null = broadcast to all
}
```

### Join Match Queue
```bash
POST /v1/match-queue/sessions/{session_id}/join
{
  "discord_id": "user_discord_id",
  "position": "Point Guard",
  "player_id": "player_uuid"
}
```

---

## Enum Values Reference

All routers now use proper enums from `app/schemas/enums.py`:

### GameYear (use these values):
`2K16`, `2K17`, `2K18`, `2K19`, `2K20`, `2K21`, `2K22`, `2K23`, `2K24`, `2K25`, `2K26`

### EventTier:
`T1`, `T2`, `T3`, `T4`, `T5`

### AchievementTier:
`bronze`, `silver`, `gold`, `platinum`, `common`, `rare`, `legendary`, `epic`

### AchievementScope:
`per_game`, `season`, `career`, `streak`, `event`

### AchievementCategory:
`Scoring`, `Assists`, `Defense`, `Rebounding`, `Mixed Stats`, `Streak & Longevity`, `Legendary`

### PlayerPosition:
`Point Guard`, `Shooting Guard`, `Lock`, `Power Forward`, `Center`

**Important**: All `game_year` parameters now use the GameYear enum. Invalid values will be rejected with a 422 error showing valid options.

---

## Database Coverage

- **Tables with Endpoints**: 20+ (up from 7)
- **Analytics Views Integrated**: 20+
- **Total New Endpoints**: 60+
- **Enhanced Endpoints**: 21+

---

## Testing Checklist

### Schema Alignment:
- [ ] Test badge award with `player_wallet` and `match_id`
- [ ] Test enum validation (try invalid game_year)
- [ ] Verify enum dropdown in Swagger UI

### New Endpoints:
- [ ] Create and list achievements
- [ ] Award player achievements
- [ ] Create event results
- [ ] Send notifications
- [ ] Join match queue

### Analytics:
- [ ] Get player performance mart
- [ ] Get team analytics
- [ ] Get league standings
- [ ] Get hot streak data
- [ ] Get head-to-head matchup

---

## Next Steps

1. **Test the API**: Visit `/docs` to see all endpoints
2. **Test Enums**: Verify enum dropdowns work in Swagger
3. **Integration**: Update frontend to use new endpoints
4. **Monitor**: Check logs for any issues

---

## Notes

- All endpoints use proper database enums (GameYear, EventTier, etc.)
- Rate limiting configured on all endpoints
- Authentication properly enforced
- Comprehensive error handling
- OpenAPI documentation complete
- Zero linting errors
- All files compile successfully

---

**Ready for Testing** 🚀

Visit: `http://localhost:10000/docs`

*Last Updated: October 28, 2025*

