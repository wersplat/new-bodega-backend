# NBA 2K Global Rankings Backend - Comprehensive Endpoint Review

## Overview

The new-bodega-backend is a comprehensive FastAPI application for managing NBA 2K gaming tournaments, player rankings, and league operations. It uses Supabase as the backend database and implements a well-structured REST API with proper authentication, rate limiting, and comprehensive error handling.

## Application Structure

### Main Entry Points
- **main.py**: Standard FastAPI app entry point
- **main_supabase.py**: Supabase-specific entry point (currently identical to main.py)

### Database Schema
The application has 40+ tables including:
- **Core entities**: `players`, `teams`, `tournaments`, `matches`, `leagues_info`
- **Statistics**: `player_stats`, `team_match_stats`, `match_mvp`, `awards_race`
- **League management**: `league_seasons`, `league_standings`, `league_teams`, `lg_conf`
- **Tournament management**: `tournament_groups`, `tournament_group_members`, `event_results`
- **Roster management**: `team_rosters`, `team_invites`, `team_members`
- **User management**: `users`, `user_profiles`, `discord_users`
- **Financial**: `payments`, `teams_pot_tracker`, `prize_pools`
- **Scheduling**: `upcoming_matches`, `match_schedules`
- **Historical data**: `past_champions`, `championship_history`

## API Endpoints

### 1. Authentication (`/auth`)
- `POST /auth/login` - User login with email/password
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user profile
- `POST /auth/refresh` - Refresh access token
- `POST /auth/forgot-password` - Password reset request
- `POST /auth/reset-password` - Password reset confirmation
- `GET /auth/verify-email/{token}` - Email verification
- `POST /auth/resend-verification` - Resend email verification

### 2. Players (`/players`)
- `GET /players/` - List all players with pagination and filtering
- `GET /players/{player_id}` - Get player details
- `POST /players/` - Create new player (admin only)
- `PUT /players/{player_id}` - Update player information
- `DELETE /players/{player_id}` - Delete player (admin only)
- `GET /players/{player_id}/stats` - Get player statistics
- `GET /players/{player_id}/matches` - Get player match history
- `GET /players/{player_id}/teams` - Get player team history
- `GET /players/{player_id}/tournaments` - Get player tournament history
- `GET /players/search` - Search players by gamertag/name
- `GET /players/leaderboard` - Get player leaderboard
- `GET /players/{player_id}/performance` - Get player performance metrics
- `GET /players/{player_id}/awards` - Get player awards and achievements

### 3. Teams (`/teams`)
- `GET /teams/` - List all teams with pagination and filtering
- `GET /teams/{team_id}` - Get team details
- `POST /teams/` - Create new team
- `PUT /teams/{team_id}` - Update team information
- `DELETE /teams/{team_id}` - Delete team (admin only)
- `GET /teams/{team_id}/players` - Get team roster
- `POST /teams/{team_id}/players` - Add player to team
- `DELETE /teams/{team_id}/players/{player_id}` - Remove player from team
- `GET /teams/{team_id}/matches` - Get team match history
- `GET /teams/{team_id}/tournaments` - Get team tournament history
- `GET /teams/{team_id}/stats` - Get team statistics
- `GET /teams/search` - Search teams by name
- `GET /teams/leaderboard` - Get team leaderboard
- `GET /teams/{team_id}/performance` - Get team performance metrics
- `POST /teams/{team_id}/invite` - Invite player to team
- `GET /teams/{team_id}/invites` - Get team invites
- `POST /teams/{team_id}/invites/{invite_id}/accept` - Accept team invite
- `POST /teams/{team_id}/invites/{invite_id}/decline` - Decline team invite

### 4. Tournaments (`/tournaments`)
- `GET /tournaments/` - List all tournaments with pagination and filtering
- `GET /tournaments/{tournament_id}` - Get tournament details
- `POST /tournaments/` - Create new tournament (admin only)
- `PUT /tournaments/{tournament_id}` - Update tournament information
- `DELETE /tournaments/{tournament_id}` - Delete tournament (admin only)
- `GET /tournaments/{tournament_id}/teams` - Get tournament teams
- `GET /tournaments/{tournament_id}/matches` - Get tournament matches
- `GET /tournaments/{tournament_id}/bracket` - Get tournament bracket
- `GET /tournaments/{tournament_id}/standings` - Get tournament standings
- `GET /tournaments/{tournament_id}/results` - Get tournament results
- `GET /tournaments/{tournament_id}/stats` - Get tournament statistics
- `POST /tournaments/{tournament_id}/register` - Register team for tournament
- `DELETE /tournaments/{tournament_id}/register/{team_id}` - Unregister team from tournament
- `GET /tournaments/upcoming` - Get upcoming tournaments
- `GET /tournaments/live` - Get live tournaments
- `GET /tournaments/completed` - Get completed tournaments
- `GET /tournaments/search` - Search tournaments

### 5. Matches (`/matches`)
- `GET /matches/` - List all matches with pagination and filtering
- `GET /matches/{match_id}` - Get match details
- `POST /matches/` - Create new match (admin only)
- `PUT /matches/{match_id}` - Update match information
- `DELETE /matches/{match_id}` - Delete match (admin only)
- `GET /matches/{match_id}/stats` - Get match statistics
- `GET /matches/{match_id}/mvp` - Get match MVP
- `POST /matches/{match_id}/mvp` - Set match MVP (admin only)
- `GET /matches/live` - Get live matches
- `GET /matches/recent` - Get recent matches
- `GET /matches/upcoming` - Get upcoming matches
- `GET /matches/search` - Search matches

### 6. Leagues (`/leagues`)
- `GET /leagues/` - List all leagues with pagination and filtering
- `GET /leagues/{league_id}` - Get league details
- `POST /leagues/` - Create new league (admin only)
- `PUT /leagues/{league_id}` - Update league information
- `DELETE /leagues/{league_id}` - Delete league (admin only)
- `GET /leagues/{league_id}/teams` - Get league teams
- `GET /leagues/{league_id}/seasons` - Get league seasons
- `GET /leagues/{league_id}/standings` - Get league standings
- `GET /leagues/{league_id}/matches` - Get league matches
- `GET /leagues/{league_id}/schedule` - Get league schedule
- `GET /leagues/{league_id}/champions` - Get league champions
- `GET /leagues/{league_id}/stats` - Get league statistics
- `GET /leagues/active` - Get active leagues
- `GET /leagues/search` - Search leagues

### 7. Leaderboard (`/leaderboard`)
- `GET /leaderboard/players` - Get player leaderboard
- `GET /leaderboard/teams` - Get team leaderboard
- `GET /leaderboard/tournaments` - Get tournament leaderboard
- `GET /leaderboard/leagues` - Get league leaderboard
- `GET /leaderboard/global` - Get global leaderboard
- `GET /leaderboard/{league_id}` - Get league-specific leaderboard
- `GET /leaderboard/{tournament_id}` - Get tournament-specific leaderboard

### 8. Admin (`/admin`)
- `GET /admin/users` - List all users (admin only)
- `GET /admin/users/{user_id}` - Get user details (admin only)
- `PUT /admin/users/{user_id}` - Update user information (admin only)
- `DELETE /admin/users/{user_id}` - Delete user (admin only)
- `GET /admin/stats` - Get system statistics
- `GET /admin/logs` - Get system logs
- `POST /admin/backup` - Create system backup
- `POST /admin/restore` - Restore system from backup

### 9. Admin Matches (`/admin/matches`)
- `POST /admin/matches/` - Create match (admin only)
- `PUT /admin/matches/{match_id}` - Update match (admin only)
- `DELETE /admin/matches/{match_id}` - Delete match (admin only)
- `POST /admin/matches/{match_id}/score` - Update match score (admin only)
- `POST /admin/matches/{match_id}/mvp` - Set match MVP (admin only)
- `POST /admin/matches/{match_id}/complete` - Complete match (admin only)
- `GET /admin/matches/pending` - Get pending matches (admin only)

### 10. Discord Integration (`/discord`)
- `POST /discord/webhook` - Discord webhook endpoint
- `GET /discord/user/{discord_id}` - Get Discord user information
- `POST /discord/link` - Link Discord account
- `DELETE /discord/unlink` - Unlink Discord account
- `GET /discord/guilds` - Get Discord guilds
- `POST /discord/notify` - Send Discord notification

### 11. Payments (`/payments`)
- `POST /payments/create` - Create payment intent
- `POST /payments/confirm` - Confirm payment
- `GET /payments/{payment_id}` - Get payment details
- `GET /payments/history` - Get payment history
- `POST /payments/refund` - Process refund (admin only)
- `GET /payments/analytics` - Get payment analytics (admin only)

## Database Views

The application includes comprehensive database views for optimized data access:

### League Views
- **`league_calendar`** - Comprehensive league calendar with seasons, tournaments, matches, and champions
- **`league_results`** - Detailed league results with team standings, rosters, stats, and leaders
- **`league_season_team_rosters`** - Current team rosters for league seasons
- **`league_team_rosters`** - Current team rosters for leagues

### Player Views
- **`player_performance_view`** - Player performance overview with aggregated stats
- **`player_performance_by_game_year`** - Player performance broken down by game year
- **`player_stats_by_league_season`** - Player statistics aggregated by league season
- **`player_roster_history`** - Complete player roster history across teams and tournaments
- **`top_tournament_performers`** - Top performing players in tournaments
- **`tournament_mvps`** - Tournament MVP winners and statistics

### Team Views
- **`team_performance_view`** - Team performance overview with comprehensive stats
- **`team_performance_by_game_year`** - Team performance broken down by game year
- **`team_roster_current`** - Current team rosters
- **`team_roster_history`** - Complete team roster history

### Tournament Views
- **`tournament_calendar`** - Comprehensive tournament calendar with status and details
- **`tournament_results`** - Detailed tournament results with standings, rosters, and stats
- **`tournament_champions_by_year`** - Tournament champions organized by year
- **`tournament_player_stats`** - Player statistics for tournaments
- **`tournament_team_stats`** - Team statistics for tournaments
- **`tournament_team_rosters`** - Team rosters for tournaments

### Advanced Analytics Views
- **`v_player_game_per`** - Player game-level performance metrics with True Shooting Percentage
- **`v_player_monthly_per`** - Player monthly performance metrics with PER calculations
- **`v_player_yearly_per`** - Player yearly performance metrics with PER calculations

## Key Features

### Authentication & Authorization
- JWT-based authentication with refresh tokens
- Role-based access control (admin, user, team captain)
- Email verification and password reset functionality
- Discord account linking

### Rate Limiting
- Configurable rate limiting per endpoint
- IP-based and user-based rate limiting
- Graceful handling of rate limit exceeded scenarios

### Data Validation
- Comprehensive input validation using Pydantic schemas
- Database constraint validation
- Custom validation rules for business logic

### Error Handling
- Structured error responses with appropriate HTTP status codes
- Detailed error messages for debugging
- Graceful handling of database errors and edge cases

### Performance Optimizations
- Database views for complex queries
- Efficient pagination for large datasets
- Caching strategies for frequently accessed data
- Optimized database indexes

### Security Features
- Input sanitization and validation
- SQL injection prevention
- XSS protection
- CORS configuration
- Secure password hashing

## API Documentation

The API includes comprehensive OpenAPI/Swagger documentation available at:
- `/docs` - Interactive Swagger UI
- `/redoc` - ReDoc documentation
- `/openapi.json` - OpenAPI specification

## Testing

The application includes comprehensive test coverage:
- Unit tests for all endpoints
- Integration tests for database operations
- Mock data for testing scenarios
- Automated test execution in CI/CD pipeline

## Deployment

The application supports multiple deployment options:
- Docker containerization
- Environment-specific configuration
- Database migration support
- Health check endpoints
- Logging and monitoring integration

## Conclusion

The new-bodega-backend provides a robust, scalable, and well-documented API for managing NBA 2K gaming tournaments and player rankings. With comprehensive endpoint coverage, advanced database views, and strong security features, it serves as a solid foundation for a competitive gaming platform.

The API design follows RESTful principles with clear separation of concerns, proper error handling, and extensive documentation. The database views provide optimized access to complex data relationships, while the authentication and authorization system ensures secure access to sensitive operations.
