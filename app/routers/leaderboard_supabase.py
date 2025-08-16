"""
Leaderboard Router

This module provides a unified API endpoint for retrieving player rankings and leaderboards
with support for filtering, sorting, and pagination.

Endpoint:
- GET /: Get leaderboard with comprehensive filtering options
  - Filter by: tier, region, tournament_id, league_id, min_games
  - Sort by: RP, peak RP, wins, win rate
  - Pagination support
"""

import logging
from enum import Enum
import uuid
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, status, Request, Query, Path

from app.core.supabase import supabase
from app.core.rate_limiter import limiter
from app.core.config import settings
from app.schemas.player import PlayerProfile, LeaderboardTier

# Initialize router with rate limiting and explicit prefix
router = APIRouter(
    prefix="/v1/leaderboard",
    tags=["Leaderboards"],
    responses={404: {"description": "Not found"}},
)

# Configure logging
logger = logging.getLogger(__name__)

class LeaderboardSortBy(str, Enum):
    """Available fields to sort the leaderboard by."""
    CURRENT_RP = "player_rp"
    PEAK_RP = "player_rank_score"
    WINS = "wins"
    WIN_RATE = "win_rate"
    RANK = "rank"

@router.get(
    "/",
    response_model=List[PlayerProfile],
    responses={
        200: {"description": "Leaderboard retrieved successfully"},
        400: {"description": "Invalid query parameters"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_leaderboard(
    request: Request,
    # Pagination
    limit: int = Query(100, ge=1, le=1000, description="Number of entries to return (1-1000)"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    
    # Filtering
    tier: Optional[LeaderboardTier] = Query(None, description="Filter by player tier"),
    region: Optional[str] = Query(None, description="Filter by region code (e.g., 'NA', 'EU')"),
    tournament_id: Optional[str] = Query(None, description="Filter by tournament ID"),
    league_id: Optional[str] = Query(None, description="Filter by league (leagues_info.id)"),
    min_games: Optional[int] = Query(None, ge=1, description="Minimum number of games played"),
    
    # Sorting
    sort_by: LeaderboardSortBy = Query(
        LeaderboardSortBy.CURRENT_RP,
        description="Field to sort the leaderboard by"
    ),
    descending: bool = Query(True, description="Sort in descending order"),
    
    # Top players shortcut
    top: Optional[int] = Query(
        None, 
        ge=1, 
        le=100, 
        description="Shortcut to get top N players (overrides limit and offset)"
    )
) -> List[Dict[str, Any]]:
    """
    Get leaderboard with comprehensive filtering and sorting options.
    
    This endpoint provides a unified way to query player rankings with support for:
    - Filtering by tier, region, tournament_id, league_id, and minimum games played
    - Sorting by RP, peak RP, wins, or win rate
    - Pagination and top-N shortcuts
    
    Args:
        request: The FastAPI request object (used for rate limiting)
        limit: Maximum number of entries to return (1-1000)
        offset: Pagination offset
        tier: Filter by player tier
        region: Filter by region code
        tournament_id: Filter by specific tournament. Mutually exclusive with league_id.
        league_id: Filter by specific league (leagues_info.id). Mutually exclusive with tournament_id.
        min_games: Minimum number of games played
        sort_by: Field to sort the leaderboard by
        descending: Whether to sort in descending order
        top: Shortcut to get top N players (overrides limit and offset)
        
    Returns:
        List[Dict[str, Any]]: List of player profiles with ranking information
        
    Raises:
        HTTPException: If there's an error retrieving the leaderboard
    """
    try:
        # Handle top-N shortcut
        if top is not None:
            limit = top
            offset = 0
            
        logger.info(
            f"Fetching leaderboard - sort_by: {sort_by}, "
            f"descending: {descending}, tier: {tier}, region: {region}, "
            f"tournament_id: {tournament_id}, league_id: {league_id}, min_games: {min_games}, "
            f"limit: {limit}, offset: {offset}"
        )
        
        client = supabase.get_client()
        
        # Back-compat: accept 'event_id' query param as alias for 'tournament_id'
        if not tournament_id:
            legacy_event_id = request.query_params.get("event_id")
            if legacy_event_id:
                tournament_id = legacy_event_id
                logger.info("Using deprecated query parameter 'event_id' as alias for 'tournament_id'")

        # Validate mutually exclusive filters
        if tournament_id and league_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide either tournament_id or league_id, not both."
            )

        # Base query - select only necessary fields for better performance
        query = client.table("players").select(
            "id, gamertag, avatar_url, player_rp, player_rank_score, "
            "wins, losses, win_rate, tier, region, created_at, total_games"
        )
        
        # Apply filters
        if tier:
            query = query.eq("tier", tier.value if hasattr(tier, 'value') else tier)
            
        if region:
            query = query.eq("region", region.upper())
            
        if min_games:
            query = query.gte("total_games", min_games)
            
        # Handle tournament- and league-specific filtering
        team_ids_filter: Optional[List[str]] = None

        # Tournament filter
        if tournament_id:
            try:
                teams_resp = (
                    client.table("event_results")
                    .select("team_id")
                    .eq("tournament_id", tournament_id)
                    .execute()
                )
                tournament_team_ids = sorted({row.get("team_id") for row in (teams_resp.data or []) if row.get("team_id")})
            except Exception as e:
                logger.error(f"Failed to fetch teams for tournament {tournament_id}: {str(e)}", exc_info=True)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail="Error applying tournament filter")
            if team_ids_filter is None:
                team_ids_filter = tournament_team_ids
            else:
                # Intersect if we already have a filter from another source
                team_ids_filter = sorted(list(set(team_ids_filter).intersection(set(tournament_team_ids))))

        # League filter
        if league_id:
            try:
                lg_resp = (
                    client.table("event_results")
                    .select("team_id")
                    .eq("league_id", league_id)
                    .execute()
                )
                league_team_ids = sorted({row.get("team_id") for row in (lg_resp.data or []) if row.get("team_id")})
            except Exception as e:
                logger.error(f"Failed to fetch teams for league {league_id}: {str(e)}", exc_info=True)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail="Error applying league filter")
            if team_ids_filter is None:
                team_ids_filter = league_team_ids
            else:
                team_ids_filter = sorted(list(set(team_ids_filter).intersection(set(league_team_ids))))

        # Apply combined team filter, if any
        if team_ids_filter is not None:
            if not team_ids_filter:
                return []  # No teams match the filters
            query = query.in_("current_team_id", team_ids_filter)
            
        # Apply sorting
        sort_field = sort_by.value if hasattr(sort_by, 'value') else sort_by
        query = query.order(sort_field, desc=descending)
        
        # Apply pagination
        query = query.range(offset, offset + limit - 1)
        
        # Execute query
        result = query.execute()
        
        if not hasattr(result, 'data') or not result.data:
            return []
            
        # Add ranking position
        ranked_players = []
        for idx, player in enumerate(result.data, start=offset + 1):
            player['rank'] = idx
            ranked_players.append(player)
            
        return ranked_players
        
    except Exception as e:
        logger.error(f"Error retrieving leaderboard: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the leaderboard"
        )

@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_tier_leaderboard(
    request: Request,
    tier: LeaderboardTier = Path(..., description="Tier to get leaderboard for"),
    limit: int = Query(100, ge=1, le=1000, description="Number of entries to return (1-1000)"),
    offset: int = Query(0, ge=0, description="Pagination offset")
) -> List[Dict[str, Any]]:
    """
    Get leaderboard for a specific player tier.
    
    This endpoint retrieves a paginated leaderboard of players within a specific tier,
    sorted by their current RP in descending order by default.
    
    Args:
        request: The FastAPI request object (used for rate limiting)
        tier: The player tier to filter by (e.g., BRONZE, SILVER, GOLD, etc.)
        limit: Maximum number of entries to return (1-1000)
        offset: Pagination offset
        
    Returns:
        List[Dict[str, Any]]: List of player profiles within the specified tier
        
    Raises:
        HTTPException: If there's an error retrieving the tier leaderboard
    """
    try:
        logger.info(
            f"Fetching leaderboard for tier {tier.value} - "
            f"limit: {limit}, offset: {offset}"
        )
        
        client = supabase.get_client()
        
        # First validate the tier exists by checking if there are any players in it
        count_result = (
            client.table("players")
            .select("id", count="exact")
            .eq("tier", tier.value)
            .execute()
        )
        
        total_players = count_result.count if hasattr(count_result, 'count') else 0
        
        if total_players == 0:
            # Check if the tier is valid by looking at the enum values
            valid_tiers = [t.value for t in LeaderboardTier]
            if tier.value not in valid_tiers:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tier '{tier.value}' not found. Valid tiers are: {', '.join(valid_tiers)}"
                )
        
        # Get the tier leaderboard with only necessary fields
        result = (
            client.table("players")
            .select(
                "id, gamertag, avatar_url, player_rp, player_rank_score, "
                "wins, losses, win_rate, tier, region, created_at"
            )
            .eq("tier", tier.value)
            .order("player_rp", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        
        players = result.data if hasattr(result, 'data') else []
        
        # Add rank based on the current sort order within the tier
        for i, player in enumerate(players, start=1):
            player["rank"] = offset + i
        
        logger.info(f"Retrieved {len(players)} players from {tier.value} tier leaderboard")
        return players
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving leaderboard for tier {tier.value}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the {tier.value} tier leaderboard"
        )

@router.get(
    "/peak-rp",
    response_model=List[PlayerProfile],
    responses={
        200: {"description": "Peak RP leaderboard retrieved successfully"},
        400: {"description": "Invalid query parameters"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_peak_rp_leaderboard(
    request: Request,
    limit: int = Query(100, ge=1, le=1000, description="Number of entries to return (1-1000)"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    min_games: int = Query(1, ge=1, description="Minimum number of games played")
) -> List[Dict[str, Any]]:
    """
    Get leaderboard sorted by peak RP (Reputation Points).
    
    This endpoint retrieves a paginated leaderboard of players sorted by their
    peak RP (player_rank_score) in descending order. It allows filtering by
    minimum number of games played to ensure meaningful rankings.
    
    Args:
        request: The FastAPI request object (used for rate limiting)
        limit: Maximum number of entries to return (1-1000)
        offset: Pagination offset
        min_games: Minimum number of games a player must have played to appear in the leaderboard
        
    Returns:
        List[Dict[str, Any]]: List of player profiles with peak RP information
        
    Raises:
        HTTPException: If there's an error retrieving the leaderboard
    """
    try:
        logger.info(
            f"Fetching peak RP leaderboard - "
            f"limit: {limit}, offset: {offset}, min_games: {min_games}"
        )
        
        client = supabase.get_client()
        
        # Build the query with only necessary fields for better performance
        query = (
            client.table("players")
            .select(
                "id, gamertag, avatar_url, player_rp, player_rank_score, "
                "wins, losses, win_rate, tier, region, created_at, "
                "(wins + losses) as games_played"
            )
            .gte("wins + losses", min_games)  # Filter by minimum games played
            .order("player_rank_score", desc=True)
            .range(offset, offset + limit - 1)
        )
        
        # Execute the query
        result = query.execute()
        players = result.data if hasattr(result, 'data') else []
        
        # Add rank based on the current sort order
        for i, player in enumerate(players, start=1):
            player["rank"] = offset + i
            
            # Calculate games played if not already present
            if "games_played" not in player and all(k in player for k in ["wins", "losses"]):
                player["games_played"] = player.get("wins", 0) + player.get("losses", 0)
        
        logger.info(f"Retrieved {len(players)} players from peak RP leaderboard")
        return players
        
    except Exception as e:
        logger.error(
            f"Error retrieving peak RP leaderboard: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the peak RP leaderboard"
        )

@router.get(
    "/region/{region}",
    response_model=List[PlayerProfile],
    responses={
        200: {"description": "Region leaderboard retrieved successfully"},
        400: {"description": "Invalid query parameters or region"},
        404: {"description": "Region not found or no players in region"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_region_leaderboard(
    request: Request,
    region: str = Path(..., description="Region code (e.g., 'NA', 'EU', 'APAC')"),
    limit: int = Query(100, ge=1, le=1000, description="Number of entries to return (1-1000)"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    min_tier: Optional[LeaderboardTier] = Query(None, description="Minimum player tier to include"),
    sort_by: str = Query("player_rp", description="Field to sort by (player_rp, player_rank_score, win_rate)")
) -> List[Dict[str, Any]]:
    """
    Get leaderboard for a specific region.
    
    This endpoint retrieves a paginated leaderboard of players within a specific region,
    sorted by the specified field in descending order. It supports filtering by minimum tier
    and various sorting options.
    
    Args:
        request: The FastAPI request object (used for rate limiting)
        region: The region code to filter by (case-insensitive, will be converted to uppercase)
        limit: Maximum number of entries to return (1-1000)
        offset: Pagination offset
        min_tier: Optional minimum player tier to include in results
        sort_by: Field to sort results by. Must be one of: player_rp, player_rank_score, win_rate
        
    Returns:
        List[Dict[str, Any]]: List of player profiles within the specified region
        
    Raises:
        HTTPException: If there's an error retrieving the region leaderboard or invalid parameters
    """
    try:
        # Normalize region to uppercase
        region_upper = region.upper()
        
        # Validate sort_by parameter
        valid_sort_fields = {"player_rp", "player_rank_score", "win_rate"}
        if sort_by not in valid_sort_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by parameter. Must be one of: {', '.join(valid_sort_fields)}"
            )
        
        logger.info(
            f"Fetching leaderboard for region {region_upper} - "
            f"limit: {limit}, offset: {offset}, min_tier: {min_tier}, sort_by: {sort_by}"
        )
        
        client = supabase.get_client()
        
        # First check if the region exists and has players
        count_query = (
            client.table("players")
            .select("id", count="exact")
            .eq("region", region_upper)
        )
        
        # Apply min_tier filter if provided
        if min_tier is not None:
            count_query = count_query.gte("tier", min_tier.value)
        
        count_result = count_query.execute()
        total_players = count_result.count if hasattr(count_result, 'count') else 0
        
        if total_players == 0:
            # Verify if the region exists in the database at all
            region_exists = (
                client.table("players")
                .select("region")
                .ilike("region", f"%{region}%")
                .limit(1)
                .execute()
            )
            
            suggestion = ""
            if hasattr(region_exists, 'data') and region_exists.data:
                # Suggest similar region names
                similar_regions = {r["region"] for r in region_exists.data}
                suggestion = f" Did you mean: {', '.join(similar_regions)}?"
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No players found in region '{region_upper}'.{suggestion}"
            )
        
        # Build the main query
        query = (
            client.table("players")
            .select(
                "id, gamertag, avatar_url, player_rp, player_rank_score, "
                "wins, losses, win_rate, tier, region, created_at"
            )
            .eq("region", region_upper)
            .order(sort_by, desc=True)
            .range(offset, offset + limit - 1)
        )
        
        # Apply min_tier filter if provided
        if min_tier is not None:
            query = query.gte("tier", min_tier.value)
        
        # Execute the query
        result = query.execute()
        players = result.data if hasattr(result, 'data') else []
        
        # Add rank based on the current sort order within the region
        for i, player in enumerate(players, start=1):
            player["rank"] = offset + i
        
        logger.info(f"Retrieved {len(players)} players from {region_upper} region leaderboard")
        return players
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving leaderboard for region {region}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the {region} region leaderboard"
        )
