"""
Leaderboard Router

This module provides a unified API endpoint for retrieving player rankings and leaderboards
with support for filtering, sorting, and pagination.

Endpoint:
- GET /: Get leaderboard with comprehensive filtering options
  - Filter by: tier, region, event, min_games
  - Sort by: RP, peak RP, wins, win rate
  - Pagination support
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Any, Union

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Path

from app.core.supabase import supabase
from app.core.rate_limiter import limiter
from app.core.config import settings
from app.schemas.player import PlayerProfile, PlayerTier

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
    tier: Optional[PlayerTier] = Query(None, description="Filter by player tier"),
    region: Optional[str] = Query(None, description="Filter by region code (e.g., 'NA', 'EU')"),
    event_id: Optional[str] = Query(None, description="Filter by specific event ID"),
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
    - Filtering by tier, region, event, and minimum games played
    - Sorting by RP, peak RP, wins, or win rate
    - Pagination and top-N shortcuts
    
    Args:
        request: The FastAPI request object (used for rate limiting)
        limit: Maximum number of entries to return (1-1000)
        offset: Pagination offset
        tier: Filter by player tier
        region: Filter by region code
        event_id: Filter by specific event
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
            f"event_id: {event_id}, min_games: {min_games}, "
            f"limit: {limit}, offset: {offset}"
        )
        
        client = supabase.get_client()
        
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
            
        # Handle event-specific leaderboard
        if event_id:
            # This would join with event_participants table in a real implementation
            # For now, we'll just filter by event_id if present
            query = query.eq("last_event_id", event_id)  # Assuming this field exists
            
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
    tier: PlayerTier = Path(..., description="Tier to get leaderboard for"),
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
            valid_tiers = [t.value for t in PlayerTier]
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
    "/event/{event_id}",
    response_model=List[Dict],
    responses={
        200: {"description": "Event leaderboard retrieved successfully"},
        400: {"description": "Invalid event ID"},
        404: {"description": "Event not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_event_leaderboard(
    request: Request,
    event_id: str = Path(..., description="ID of the event to get leaderboard for"),
    include_stats: bool = Query(False, description="Include detailed player statistics")
) -> List[Dict[str, Any]]:
    """
    Get leaderboard for a specific event.
    
    This endpoint retrieves the leaderboard for a specific event, showing player rankings
    and statistics for that event. It uses an optimized database function to efficiently
    calculate and return the results.
    
    Args:
        request: The FastAPI request object (used for rate limiting)
        event_id: The unique identifier of the event
        include_stats: Whether to include detailed player statistics
        
    Returns:
        List[Dict[str, Any]]: List of player entries in the event leaderboard
        
    Raises:
        HTTPException: If the event is not found or there's an error retrieving the leaderboard
    """
    try:
        logger.info(f"Fetching leaderboard for event {event_id}")
        
        # Validate event_id format
        try:
            # This will raise a ValueError if the event_id is not a valid UUID
            uuid.UUID(event_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID format. Must be a valid UUID."
            )
        
        client = supabase.get_client()
        
        # First get the event to verify it exists and get basic info
        event_result = (
            client.table("events")
            .select("id, name, start_date, end_date, status")
            .eq("id", event_id)
            .single()
            .execute()
        )
        
        if not hasattr(event_result, 'data') or not event_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        event = event_result.data
        logger.debug(f"Found event: {event.get('name')} (ID: {event_id})")
        
        # Determine which fields to select based on include_stats
        select_fields = [
            "player_id", "gamertag", "avatar_url", "total_points", "rank",
            "matches_played", "wins", "losses", "win_rate"
        ]
        
        if include_stats:
            select_fields.extend([
                "kills", "deaths", "assists", "kd_ratio", "damage_dealt",
                "damage_taken", "healing_done", "objectives_completed"
            ])
        
        # Get event standings with player details using the RPC function
        result = client.rpc(
            'get_event_standings',
            {
                'p_event_id': event_id,
                'p_include_stats': include_stats
            }
        ).execute()
        
        leaderboard = result.data if hasattr(result, 'data') else []
        
        # Add event information to each entry
        for entry in leaderboard:
            entry["event_id"] = event_id
            entry["event_name"] = event.get("name")
            
            # Calculate rank percentage if we have enough data
            if "rank" in entry and "total_players" in event:
                total_players = event["total_players"] or 1  # Avoid division by zero
                entry["rank_percentile"] = min(100, round((entry["rank"] / total_players) * 100, 2))
        
        logger.info(f"Retrieved leaderboard for event {event_id} with {len(leaderboard)} entries")
        return leaderboard
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving leaderboard for event {event_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the event leaderboard"
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
    min_tier: Optional[PlayerTier] = Query(None, description="Minimum player tier to include"),
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
