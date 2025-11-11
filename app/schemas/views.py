"""
Pydantic schemas for database views
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
from uuid import UUID
from app.schemas.enums import GameYear

# Common Enums
class LeagueStatus(str, Enum):
    ACTIVE = "active"
    UPCOMING = "upcoming"
    COMPLETED = "completed"
    UNKNOWN = "unknown"

class TournamentStatus(str, Enum):
    UPCOMING = "upcoming"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    UNKNOWN = "unknown"

class PlayerPosition(str, Enum):
    POINT_GUARD = "Point Guard"
    SHOOTING_GUARD = "Shooting Guard"
    LOCK = "Lock"
    POWER_FORWARD = "Power Forward"
    CENTER = "Center"

# League Views Schemas
class LeagueCalendarResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    league_id: str
    league_name: str
    season_id: Optional[str] = None
    season_number: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    game_year: Optional[str] = None
    league_logo: Optional[str] = None
    league_website: Optional[str] = None
    discord_link: Optional[str] = None
    twitter_id: Optional[str] = None
    twitch_url: Optional[str] = None
    tournament_count: Optional[int] = None
    total_matches: Optional[int] = None
    last_match_date: Optional[datetime] = None
    upcoming_matches_count: Optional[int] = None
    next_match_time: Optional[datetime] = None
    champion_id: Optional[str] = None
    champion_name: Optional[str] = None
    champion_logo: Optional[str] = None
    championship_date: Optional[datetime] = None
    league_status: Optional[LeagueStatus] = None
    sort_order: Optional[int] = None

class LeagueResultsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    league_id: str
    league_name: str
    season_id: Optional[str] = None
    season_number: Optional[int] = None
    year: Optional[int] = None
    team_id: str
    team_name: str
    logo_url: Optional[str] = None
    conference_name: Optional[str] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    win_percentage: Optional[float] = None
    current_rp: Optional[int] = None
    elo_rating: Optional[float] = None
    points_for: Optional[int] = None
    points_against: Optional[int] = None
    point_differential: Optional[int] = None
    roster: Optional[List[Dict[str, Any]]] = None
    avg_points: Optional[float] = None
    avg_rebounds: Optional[float] = None
    avg_assists: Optional[float] = None
    avg_steals: Optional[float] = None
    avg_blocks: Optional[float] = None
    avg_turnovers: Optional[float] = None
    fg_percentage: Optional[float] = None
    three_pt_percentage: Optional[float] = None
    stat_leaders: Optional[Dict[str, Any]] = None
    team_rankings: Optional[Dict[str, Any]] = None

class LeagueTeamRosterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    team_name: str
    player_name: str
    player_position: Optional[PlayerPosition] = None
    is_captain: Optional[bool] = None
    is_player_coach: Optional[bool] = None
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None
    league_name: str
    league_id: str
    team_id: str
    player_id: str
    season_id: Optional[str] = None
    game_year: Optional[str] = None

# Player Views Schemas
class PlayerPerformanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    gamertag: str
    position: Optional[PlayerPosition] = None
    current_team_id: Optional[str] = None
    team_name: Optional[str] = None
    player_rp: Optional[int] = None
    player_rank_score: Optional[float] = None
    salary_tier: Optional[str] = None
    monthly_value: Optional[int] = None
    games_played: Optional[int] = None
    avg_points: Optional[float] = None
    avg_rebounds: Optional[float] = None
    avg_assists: Optional[float] = None
    avg_steals: Optional[float] = None
    avg_blocks: Optional[float] = None
    avg_performance_score: Optional[float] = None

class PlayerPerformanceByGameYearResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    player_id: str
    gamertag: str
    position: Optional[PlayerPosition] = None
    game_year: Optional[str] = None
    matches_played: Optional[int] = None
    avg_points: Optional[float] = None
    avg_rebounds: Optional[float] = None
    avg_assists: Optional[float] = None
    avg_steals: Optional[float] = None
    avg_blocks: Optional[float] = None
    avg_turnovers: Optional[float] = None
    avg_plus_minus: Optional[float] = None
    avg_performance_score: Optional[float] = None
    total_points: Optional[int] = None
    total_rebounds: Optional[int] = None
    total_assists: Optional[int] = None
    total_steals: Optional[int] = None
    total_blocks: Optional[int] = None
    games_20plus_points: Optional[int] = None
    mvp_count: Optional[int] = None

class PlayerStatsByLeagueSeasonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    league_season_id: str
    league_id: str
    season_number: Optional[int] = None
    game_year: Optional[str] = None
    player_id: str
    player_gamertag: str
    games_played: Optional[int] = None
    points: Optional[int] = None
    rebounds: Optional[int] = None
    assists: Optional[int] = None
    steals: Optional[int] = None
    blocks: Optional[int] = None
    turnovers: Optional[int] = None
    fouls: Optional[int] = None
    fgm: Optional[int] = None
    fga: Optional[int] = None
    ftm: Optional[int] = None
    fta: Optional[int] = None
    three_points_made: Optional[int] = None
    three_points_attempted: Optional[int] = None
    plus_minus: Optional[int] = None
    performance_score: Optional[float] = None
    avg_points: Optional[float] = None
    avg_rebounds: Optional[float] = None
    avg_assists: Optional[float] = None
    avg_steals: Optional[float] = None
    avg_blocks: Optional[float] = None
    avg_turnovers: Optional[float] = None
    avg_fouls: Optional[float] = None

class PlayerRosterHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    player_id: str
    gamertag: str
    position: Optional[PlayerPosition] = None
    team_id: str
    team_name: str
    is_captain: Optional[bool] = None
    is_player_coach: Optional[bool] = None
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None
    status: Optional[str] = None
    league_id: Optional[str] = None
    league_name: Optional[str] = None
    tournament_id: Optional[str] = None
    tournament_name: Optional[str] = None
    season_number: Optional[int] = None
    game_year: Optional[str] = None

class TopTournamentPerformerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    player_id: str
    gamertag: str
    position: Optional[PlayerPosition] = None
    tournaments_played: Optional[int] = None
    total_games: Optional[int] = None
    avg_points: Optional[float] = None
    avg_assists: Optional[float] = None
    avg_rebounds: Optional[float] = None
    avg_steals: Optional[float] = None
    avg_blocks: Optional[float] = None
    avg_performance_score: Optional[float] = None
    fg_percentage: Optional[float] = None
    three_pt_percentage: Optional[float] = None
    ft_percentage: Optional[float] = None
    avg_plus_minus: Optional[float] = None
    games_won: Optional[int] = None
    tournaments_won: Optional[int] = None
    current_team_id: Optional[str] = None
    current_team: Optional[str] = None

class TournamentMVPResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    player_id: str
    gamertag: str
    position: Optional[PlayerPosition] = None
    tournament_id: str
    tournament_name: str
    game_year: Optional[str] = None
    team_id: str
    team_name: str
    games_played: Optional[int] = None
    avg_points: Optional[float] = None
    avg_assists: Optional[float] = None
    avg_rebounds: Optional[float] = None
    avg_steals: Optional[float] = None
    avg_blocks: Optional[float] = None
    avg_performance_score: Optional[float] = None
    is_champion: Optional[bool] = None
    award_type: Optional[str] = None

# Team Views Schemas
class TeamPerformanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    team_id: str
    team_name: str
    logo_url: Optional[str] = None
    current_rp: Optional[int] = None
    elo_rating: Optional[float] = None
    global_rank: Optional[int] = None
    leaderboard_tier: Optional[str] = None
    money_won: Optional[float] = None
    total_matches_played: Optional[int] = None
    matches_won: Optional[int] = None
    matches_lost: Optional[int] = None
    win_percentage: Optional[float] = None
    tournament_appearances: Optional[int] = None
    tournament_wins: Optional[int] = None
    total_prize_earnings: Optional[float] = None
    avg_points_per_match: Optional[float] = None
    avg_field_goals_made: Optional[float] = None
    avg_field_goals_attempted: Optional[float] = None
    field_goal_percentage: Optional[float] = None
    avg_three_points_made: Optional[float] = None
    avg_three_points_attempted: Optional[float] = None
    three_point_percentage: Optional[float] = None
    avg_assists: Optional[float] = None
    avg_rebounds: Optional[float] = None
    avg_steals: Optional[float] = None
    avg_blocks: Optional[float] = None
    avg_turnovers: Optional[float] = None
    championship_count: Optional[int] = None
    roster_last_changed: Optional[datetime] = None
    current_roster_count: Optional[int] = None

class TeamPerformanceByGameYearResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    team_id: str
    team_name: str
    game_year: Optional[str] = None
    total_matches: Optional[int] = None
    matches_won: Optional[int] = None
    matches_lost: Optional[int] = None
    win_percentage: Optional[float] = None
    points_scored: Optional[int] = None
    points_allowed: Optional[int] = None
    avg_points_scored: Optional[float] = None
    avg_points_allowed: Optional[float] = None
    tournament_placements: Optional[int] = None
    best_placement: Optional[int] = None
    total_prize_amount: Optional[float] = None
    current_elo: Optional[float] = None
    current_ranking_points: Optional[int] = None

class TeamRosterCurrentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    team_id: str
    team_name: str
    player_id: str
    gamertag: str
    position: Optional[PlayerPosition] = None
    salary_tier: Optional[str] = None
    monthly_value: Optional[int] = None
    is_captain: Optional[bool] = None
    is_player_coach: Optional[bool] = None
    joined_at: Optional[datetime] = None

class TeamRosterHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    team_id: str
    team_name: str
    team_logo: Optional[str] = None
    player_id: str
    gamertag: str
    position: Optional[PlayerPosition] = None
    is_captain: Optional[bool] = None
    is_player_coach: Optional[bool] = None
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None
    status: Optional[str] = None
    league_id: Optional[str] = None
    league_name: Optional[str] = None
    tournament_id: Optional[str] = None
    tournament_name: Optional[str] = None
    season_number: Optional[int] = None
    game_year: Optional[str] = None

# Tournament Views Schemas
class TournamentCalendarResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    tournament_name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    game_year: Optional[str] = None
    prize_pool: Optional[float] = None
    status: Optional[str] = None
    tier: Optional[str] = None
    banner_url: Optional[str] = None
    description: Optional[str] = None
    organizer_name: Optional[str] = None
    league_logo: Optional[str] = None
    organizer_logo_url: Optional[str] = None
    champion: Optional[str] = None
    champion_name: Optional[str] = None
    champion_logo: Optional[str] = None
    runner_up: Optional[str] = None
    runner_up_name: Optional[str] = None
    runner_up_logo: Optional[str] = None
    third_place_id: Optional[str] = None
    third_place_name: Optional[str] = None
    third_place_logo: Optional[str] = None
    upcoming_matches_count: Optional[int] = None
    next_match_time: Optional[datetime] = None
    tournament_status: Optional[TournamentStatus] = None
    sort_order: Optional[int] = None

class TournamentResultsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    tournament_id: str
    tournament_name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    game_year: Optional[str] = None
    tournament_tier: Optional[str] = None
    prize_pool: Optional[float] = None
    tournament_status: Optional[str] = None
    organizer_id: Optional[str] = None
    organizer_name: Optional[str] = None
    team_id: str
    team_name: str
    logo_url: Optional[str] = None
    final_placement: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    win_percentage: Optional[float] = None
    current_rp: Optional[int] = None
    elo_rating: Optional[float] = None
    points_for: Optional[int] = None
    points_against: Optional[int] = None
    point_differential: Optional[int] = None
    prize_won: Optional[float] = None
    groups: Optional[str] = None
    roster: Optional[List[Dict[str, Any]]] = None
    avg_points: Optional[float] = None
    avg_rebounds: Optional[float] = None
    avg_assists: Optional[float] = None
    avg_steals: Optional[float] = None
    avg_blocks: Optional[float] = None
    avg_turnovers: Optional[float] = None
    fg_percentage: Optional[float] = None
    three_pt_percentage: Optional[float] = None
    stat_leaders: Optional[Dict[str, Any]] = None
    team_rankings: Optional[Dict[str, Any]] = None
    awards: Optional[Dict[str, Any]] = None
    group_standings: Optional[List[Dict[str, Any]]] = None

class TournamentChampionsByYearResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    tournament_id: str
    tournament_name: str
    game_year: Optional[str] = None
    tournament_tier: Optional[str] = None
    prize_pool: Optional[float] = None
    champion_team_id: str
    champion_team_name: str
    champion_logo: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    organizer_name: Optional[str] = None
    organizer_logo: Optional[str] = None
    console: Optional[str] = None

class TournamentPlayerStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    player_id: str
    gamertag: str
    position: Optional[PlayerPosition] = None
    tournament_id: str
    tournament_name: str
    game_year: Optional[str] = None
    tournament_tier: Optional[str] = None
    team_id: str
    team_name: str
    games_played: Optional[int] = None
    total_points: Optional[int] = None
    avg_points: Optional[float] = None
    total_assists: Optional[int] = None
    avg_rebounds: Optional[float] = None
    total_rebounds: Optional[int] = None
    avg_assists: Optional[float] = None
    total_steals: Optional[int] = None
    avg_steals: Optional[float] = None
    total_blocks: Optional[int] = None
    avg_blocks: Optional[float] = None
    total_turnovers: Optional[int] = None
    avg_turnovers: Optional[float] = None
    total_fouls: Optional[int] = None
    avg_fouls: Optional[float] = None
    total_fgm: Optional[int] = None
    total_fga: Optional[int] = None
    fg_percentage: Optional[float] = None
    total_3pm: Optional[int] = None
    total_3pa: Optional[int] = None
    three_pt_percentage: Optional[float] = None
    total_ftm: Optional[int] = None
    total_fta: Optional[int] = None
    ft_percentage: Optional[float] = None
    total_plus_minus: Optional[int] = None
    avg_plus_minus: Optional[float] = None
    avg_performance_score: Optional[float] = None
    total_performance_score: Optional[float] = None

class TournamentTeamStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    team_id: str
    team_name: str
    tournament_id: str
    tournament_name: str
    game_year: Optional[str] = None
    tournament_tier: Optional[str] = None
    games_played: Optional[int] = None
    games_won: Optional[int] = None
    games_lost: Optional[int] = None
    win_percentage: Optional[float] = None
    tournament_result: Optional[str] = None
    avg_team_points: Optional[float] = None
    avg_team_rebounds: Optional[float] = None
    avg_team_assists: Optional[float] = None
    avg_team_steals: Optional[float] = None
    avg_team_blocks: Optional[float] = None
    avg_team_turnovers: Optional[float] = None
    team_fg_percentage: Optional[float] = None
    team_three_pt_percentage: Optional[float] = None
    team_ft_percentage: Optional[float] = None

class TournamentTeamRostersResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    team_id: str
    player_id: str
    is_captain: Optional[bool] = None
    is_player_coach: Optional[bool] = None
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None
    league_id: Optional[str] = None
    tournament_id: str
    tournament_name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    team_name: str
    team_logo: Optional[str] = None
    gamertag: str
    position: Optional[PlayerPosition] = None
    salary_tier: Optional[str] = None
    player_rank_score: Optional[float] = None
    discord_id: Optional[str] = None
    twitter_id: Optional[str] = None

# Advanced Analytics Views Schemas
class PlayerGamePERResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    player_id: str
    match_id: str
    game_date: Optional[datetime] = None
    month: Optional[datetime] = None
    league_id: Optional[str] = None
    season_id: Optional[str] = None
    tournament_id: Optional[str] = None
    ts_pct: Optional[float] = None
    league_ts_avg: Optional[float] = None
    ts_plus: Optional[float] = None
    raw_score: Optional[float] = None

class PlayerMonthlyPERResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    month: Optional[datetime] = None
    league_id: Optional[str] = None
    season_id: Optional[str] = None
    tournament_id: Optional[str] = None
    player_id: str
    games_played: Optional[int] = None
    per_raw: Optional[float] = None
    per15: Optional[float] = None

class PlayerYearlyPERResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    game_year: Optional[str] = None
    league_id: Optional[str] = None
    season_id: Optional[str] = None
    tournament_id: Optional[str] = None
    player_id: str
    games_played: Optional[int] = None
    per_raw: Optional[float] = None
    per15: Optional[float] = None

# Generic response models for pagination
class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper"""
    data: List[Dict[str, Any]]
    pagination: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str
    status_code: int
