"""
Database Views Router

This module provides endpoints for accessing all database views in the system.
Views provide optimized, pre-computed data for complex queries.

API Version: 1.0.0
Base URL: /v1/views
"""

from fastapi import APIRouter, HTTPException, Query, Request, status
from typing import Dict, List, Any, Optional
from app.core.supabase_client import supabase
from app.core.config import settings
from app.core.rate_limiter import limiter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/views", tags=["Database Views"])


# League Views
@router.get("/league-calendar")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_league_calendar(
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status_filter: Optional[str] = Query(None, description="Filter by league status: active, upcoming, completed")
) -> List[Dict[str, Any]]:
    """
    Get league calendar with comprehensive league information.
    
    Returns leagues with their seasons, tournaments, matches, and champions.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("league_calendar").select("*")
        
        if status_filter:
            query = query.eq("league_status", status_filter)
        
        result = query.order("sort_order").range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting league calendar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving league calendar"
        )


@router.get("/league-results")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_league_results(
    request: Request,
    league_id: Optional[str] = Query(None, description="Filter by specific league ID"),
    season_id: Optional[str] = Query(None, description="Filter by specific season ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get detailed league results with team standings, rosters, stats, and leaders.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("league_results").select("*")
        
        if league_id:
            query = query.eq("league_id", league_id)
        if season_id:
            query = query.eq("season_id", season_id)
        
        result = query.order("win_percentage", desc=True).range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting league results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving league results"
        )


@router.get("/league-team-rosters")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_league_team_rosters(
    request: Request,
    league_id: Optional[str] = Query(None, description="Filter by specific league ID"),
    team_id: Optional[str] = Query(None, description="Filter by specific team ID")
) -> List[Dict[str, Any]]:
    """
    Get current team rosters for leagues.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("league_team_rosters").select("*")
        
        if league_id:
            query = query.eq("league_id", league_id)
        if team_id:
            query = query.eq("team_id", team_id)
        
        result = query.execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting league team rosters: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving league team rosters"
        )


@router.get("/league-season-team-rosters")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_league_season_team_rosters(
    request: Request,
    league_id: Optional[str] = Query(None, description="Filter by specific league ID"),
    season_id: Optional[str] = Query(None, description="Filter by specific season ID"),
    team_id: Optional[str] = Query(None, description="Filter by specific team ID")
) -> List[Dict[str, Any]]:
    """
    Get current team rosters for league seasons.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("league_season_team_rosters").select("*")
        
        if league_id:
            query = query.eq("league_id", league_id)
        if season_id:
            query = query.eq("season_id", season_id)
        if team_id:
            query = query.eq("team_id", team_id)
        
        result = query.execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting league season team rosters: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving league season team rosters"
        )


# Player Views
@router.get("/player-performance")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_player_performance(
    request: Request,
    player_id: Optional[str] = Query(None, description="Filter by specific player ID"),
    team_id: Optional[str] = Query(None, description="Filter by specific team ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get player performance overview with aggregated stats.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("player_performance_view").select("*")
        
        if player_id:
            query = query.eq("id", player_id)
        if team_id:
            query = query.eq("current_team_id", team_id)
        
        result = query.order("avg_performance_score", desc=True).range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting player performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving player performance"
        )


@router.get("/player-performance-by-game-year")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_player_performance_by_game_year(
    request: Request,
    player_id: Optional[str] = Query(None, description="Filter by specific player ID"),
    game_year: Optional[int] = Query(None, description="Filter by specific game year"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get player performance broken down by game year.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("player_performance_by_game_year").select("*")
        
        if player_id:
            query = query.eq("player_id", player_id)
        if game_year:
            query = query.eq("game_year", game_year)
        
        result = query.order("game_year", desc=True).order("avg_performance_score", desc=True).range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting player performance by game year: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving player performance by game year"
        )


@router.get("/player-stats-by-league-season")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_player_stats_by_league_season(
    request: Request,
    league_id: Optional[str] = Query(None, description="Filter by specific league ID"),
    season_id: Optional[str] = Query(None, description="Filter by specific season ID"),
    player_id: Optional[str] = Query(None, description="Filter by specific player ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get player statistics aggregated by league season.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("player_stats_by_league_season").select("*")
        
        if league_id:
            query = query.eq("league_id", league_id)
        if season_id:
            query = query.eq("league_season_id", season_id)
        if player_id:
            query = query.eq("player_id", player_id)
        
        result = query.order("performance_score", desc=True).range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting player stats by league season: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving player stats by league season"
        )


@router.get("/player-roster-history")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_player_roster_history(
    request: Request,
    player_id: Optional[str] = Query(None, description="Filter by specific player ID"),
    team_id: Optional[str] = Query(None, description="Filter by specific team ID"),
    league_id: Optional[str] = Query(None, description="Filter by specific league ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get complete player roster history across teams and tournaments.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("player_roster_history").select("*")
        
        if player_id:
            query = query.eq("player_id", player_id)
        if team_id:
            query = query.eq("team_id", team_id)
        if league_id:
            query = query.eq("league_id", league_id)
        
        result = query.order("joined_at", desc=True).range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting player roster history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving player roster history"
        )


@router.get("/top-tournament-performers")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_top_tournament_performers(
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get top performing players in tournaments.
    """
    try:
        client = supabase.get_client()
        
        result = client.table("top_tournament_performers").select("*").order("avg_performance_score", desc=True).range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting top tournament performers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving top tournament performers"
        )


@router.get("/tournament-mvps")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_tournament_mvps(
    request: Request,
    tournament_id: Optional[str] = Query(None, description="Filter by specific tournament ID"),
    game_year: Optional[int] = Query(None, description="Filter by specific game year"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get tournament MVP winners and statistics.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("tournament_mvps").select("*")
        
        if tournament_id:
            query = query.eq("tournament_id", tournament_id)
        if game_year:
            query = query.eq("game_year", game_year)
        
        result = query.order("tournament_name", desc=True).order("avg_performance_score", desc=True).range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting tournament MVPs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving tournament MVPs"
        )


# Team Views
@router.get("/team-performance")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_team_performance(
    request: Request,
    team_id: Optional[str] = Query(None, description="Filter by specific team ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get team performance overview with comprehensive stats.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("team_performance_view").select("*")
        
        if team_id:
            query = query.eq("team_id", team_id)
        
        result = query.order("current_rp", desc=True).range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting team performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving team performance"
        )


@router.get("/team-performance-by-game-year")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_team_performance_by_game_year(
    request: Request,
    team_id: Optional[str] = Query(None, description="Filter by specific team ID"),
    game_year: Optional[int] = Query(None, description="Filter by specific game year"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get team performance broken down by game year.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("team_performance_by_game_year").select("*")
        
        if team_id:
            query = query.eq("team_id", team_id)
        if game_year:
            query = query.eq("game_year", game_year)
        
        result = query.order("game_year", desc=True).order("win_percentage", desc=True).range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting team performance by game year: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving team performance by game year"
        )


@router.get("/team-roster-current")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_team_roster_current(
    request: Request,
    team_id: Optional[str] = Query(None, description="Filter by specific team ID")
) -> List[Dict[str, Any]]:
    """
    Get current team rosters.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("team_roster_current").select("*")
        
        if team_id:
            query = query.eq("team_id", team_id)
        
        result = query.execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting current team rosters: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving current team rosters"
        )


@router.get("/team-roster-history")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_team_roster_history(
    request: Request,
    team_id: Optional[str] = Query(None, description="Filter by specific team ID"),
    league_id: Optional[str] = Query(None, description="Filter by specific league ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get complete team roster history.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("team_roster_history").select("*")
        
        if team_id:
            query = query.eq("team_id", team_id)
        if league_id:
            query = query.eq("league_id", league_id)
        
        result = query.order("joined_at", desc=True).range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting team roster history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving team roster history"
        )


# Tournament Views
@router.get("/tournament-calendar")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_tournament_calendar(
    request: Request,
    status_filter: Optional[str] = Query(None, description="Filter by tournament status: upcoming, in_progress, completed"),
    game_year: Optional[int] = Query(None, description="Filter by specific game year"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get comprehensive tournament calendar with status and details.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("tournament_calendar").select("*")
        
        if status_filter:
            query = query.eq("tournament_status", status_filter)
        if game_year:
            query = query.eq("game_year", game_year)
        
        result = query.order("sort_order").range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting tournament calendar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving tournament calendar"
        )


@router.get("/tournament-results")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_tournament_results(
    request: Request,
    tournament_id: Optional[str] = Query(None, description="Filter by specific tournament ID"),
    team_id: Optional[str] = Query(None, description="Filter by specific team ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get detailed tournament results with standings, rosters, and stats.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("tournament_results").select("*")
        
        if tournament_id:
            query = query.eq("tournament_id", tournament_id)
        if team_id:
            query = query.eq("team_id", team_id)
        
        result = query.order("final_placement").range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting tournament results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving tournament results"
        )


@router.get("/tournament-champions-by-year")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_tournament_champions_by_year(
    request: Request,
    game_year: Optional[int] = Query(None, description="Filter by specific game year"),
    tournament_tier: Optional[str] = Query(None, description="Filter by tournament tier"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get tournament champions organized by year.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("tournament_champions_by_year").select("*")
        
        if game_year:
            query = query.eq("game_year", game_year)
        if tournament_tier:
            query = query.eq("tournament_tier", tournament_tier)
        
        result = query.order("game_year", desc=True).order("end_date", desc=True).range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting tournament champions by year: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving tournament champions by year"
        )


@router.get("/tournament-player-stats")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_tournament_player_stats(
    request: Request,
    tournament_id: Optional[str] = Query(None, description="Filter by specific tournament ID"),
    player_id: Optional[str] = Query(None, description="Filter by specific player ID"),
    team_id: Optional[str] = Query(None, description="Filter by specific team ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get player statistics for tournaments.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("tournament_player_stats").select("*")
        
        if tournament_id:
            query = query.eq("tournament_id", tournament_id)
        if player_id:
            query = query.eq("player_id", player_id)
        if team_id:
            query = query.eq("team_id", team_id)
        
        result = query.order("avg_performance_score", desc=True).range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting tournament player stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving tournament player stats"
        )


@router.get("/tournament-team-stats")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_tournament_team_stats(
    request: Request,
    tournament_id: Optional[str] = Query(None, description="Filter by specific tournament ID"),
    team_id: Optional[str] = Query(None, description="Filter by specific team ID"),
    game_year: Optional[int] = Query(None, description="Filter by specific game year"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get team statistics for tournaments.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("tournament_team_stats").select("*")
        
        if tournament_id:
            query = query.eq("tournament_id", tournament_id)
        if team_id:
            query = query.eq("team_id", team_id)
        if game_year:
            query = query.eq("game_year", game_year)
        
        result = query.order("win_percentage", desc=True).range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting tournament team stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving tournament team stats"
        )


@router.get("/tournament-team-rosters")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_tournament_team_rosters(
    request: Request,
    tournament_id: Optional[str] = Query(None, description="Filter by specific tournament ID"),
    team_id: Optional[str] = Query(None, description="Filter by specific team ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get team rosters for tournaments.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("tournament_team_rosters").select("*")
        
        if tournament_id:
            query = query.eq("tournament_id", tournament_id)
        if team_id:
            query = query.eq("team_id", team_id)
        
        result = query.order("start_date", desc=True).range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting tournament team rosters: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving tournament team rosters"
        )


# Advanced Analytics Views
@router.get("/player-game-per")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_player_game_per(
    request: Request,
    player_id: Optional[str] = Query(None, description="Filter by specific player ID"),
    league_id: Optional[str] = Query(None, description="Filter by specific league ID"),
    season_id: Optional[str] = Query(None, description="Filter by specific season ID"),
    tournament_id: Optional[str] = Query(None, description="Filter by specific tournament ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get player game-level performance metrics with True Shooting Percentage.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("v_player_game_per").select("*")
        
        if player_id:
            query = query.eq("player_id", player_id)
        if league_id:
            query = query.eq("league_id", league_id)
        if season_id:
            query = query.eq("season_id", season_id)
        if tournament_id:
            query = query.eq("tournament_id", tournament_id)
        
        result = query.order("raw_score", desc=True).range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting player game PER: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving player game PER"
        )


@router.get("/player-monthly-per")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_player_monthly_per(
    request: Request,
    player_id: Optional[str] = Query(None, description="Filter by specific player ID"),
    league_id: Optional[str] = Query(None, description="Filter by specific league ID"),
    season_id: Optional[str] = Query(None, description="Filter by specific season ID"),
    tournament_id: Optional[str] = Query(None, description="Filter by specific tournament ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get player monthly performance metrics with PER calculations.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("v_player_monthly_per").select("*")
        
        if player_id:
            query = query.eq("player_id", player_id)
        if league_id:
            query = query.eq("league_id", league_id)
        if season_id:
            query = query.eq("season_id", season_id)
        if tournament_id:
            query = query.eq("tournament_id", tournament_id)
        
        result = query.order("per15", desc=True).range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting player monthly PER: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving player monthly PER"
        )


@router.get("/player-yearly-per")
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def get_player_yearly_per(
    request: Request,
    player_id: Optional[str] = Query(None, description="Filter by specific player ID"),
    league_id: Optional[str] = Query(None, description="Filter by specific league ID"),
    season_id: Optional[str] = Query(None, description="Filter by specific season ID"),
    tournament_id: Optional[str] = Query(None, description="Filter by specific tournament ID"),
    game_year: Optional[int] = Query(None, description="Filter by specific game year"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get player yearly performance metrics with PER calculations.
    """
    try:
        client = supabase.get_client()
        
        query = client.table("v_player_yearly_per").select("*")
        
        if player_id:
            query = query.eq("player_id", player_id)
        if league_id:
            query = query.eq("league_id", league_id)
        if season_id:
            query = query.eq("season_id", season_id)
        if tournament_id:
            query = query.eq("tournament_id", tournament_id)
        if game_year:
            query = query.eq("game_year", game_year)
        
        result = query.order("game_year", desc=True).order("per15", desc=True).range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting player yearly PER: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving player yearly PER"
        )
