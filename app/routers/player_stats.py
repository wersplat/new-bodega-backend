"""
Player statistics router for handling player stats related operations
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union, cast
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from pydantic import BaseModel, Field, validator

from app.core.config import settings
from app.core.supabase import supabase
from app.core.rate_limiter import limiter
from app.schemas.player_stats import (
    PlayerStats as PlayerStatsSchema,
    PlayerStatsCreate,
    PlayerStatsUpdate,
    PlayerStatsWithDetails
)
from app.core.auth import get_current_active_user, RoleChecker

# Initialize router with rate limiting
router = APIRouter(prefix="/player-stats", tags=["Player Statistics"])

def calculate_game_score(stats: Dict[str, Any]) -> float:
    """
    Calculate a game score for a player's performance in a game.
    
    Game Score formula:
    Points + (0.4 * Field Goals) - (0.7 * Field Goal Attempts) - (0.4 * (Free Throw Attempts - Free Throws)) +
    (0.7 * Offensive Rebounds) + (0.3 * Defensive Rebounds) + Steals + (0.7 * Assists) + (0.7 * Blocks) -
    (0.4 * Personal Fouls) - Turnovers
    
    Args:
        stats: Dictionary containing player statistics for a game
        
    Returns:
        float: The calculated game score
    """
    fg = stats.get("field_goals_made", stats.get("fgm", 0))
    fga = stats.get("field_goals_attempted", stats.get("fga", 0))
    ft = stats.get("free_throws_made", stats.get("ftm", 0))
    fta = stats.get("free_throws_attempted", stats.get("fta", 0))
    orb = stats.get("offensive_rebounds", 0)
    drb = stats.get("defensive_rebounds", 0)
    stl = stats.get("steals", 0)
    ast = stats.get("assists", 0)
    blk = stats.get("blocks", 0)
    pf = stats.get("fouls", 0)
    tov = stats.get("turnovers", 0)
    pts = stats.get("points", 0)
    
    game_score = (
        pts +
        (0.4 * fg) -
        (0.7 * fga) -
        (0.4 * (fta - ft)) +
        (0.7 * orb) +
        (0.3 * drb) +
        stl +
        (0.7 * ast) +
        (0.7 * blk) -
        (0.4 * pf) -
        tov
    )
    
    return round(game_score, 1)

def calculate_efficiency(stats: Dict[str, Any]) -> float:
    """
    Calculate efficiency for a player's performance in a game.
    
    Efficiency formula:
    (Points + Rebounds + Assists + Steals + Blocks - 
     ((Field Goals Attempted - Field Goals Made) + 
      (Free Throws Attempted - Free Throws Made) + 
      Turnovers))
    
    Args:
        stats: Dictionary containing player statistics for a game
        
    Returns:
        float: The calculated efficiency rating
    """
    fg = stats.get("field_goals_made", stats.get("fgm", 0))
    fga = stats.get("field_goals_attempted", stats.get("fga", 0))
    ft = stats.get("free_throws_made", stats.get("ftm", 0))
    fta = stats.get("free_throws_attempted", stats.get("fta", 0))
    reb = stats.get("rebounds", 0) or (stats.get("offensive_rebounds", 0) + stats.get("defensive_rebounds", 0))
    stl = stats.get("steals", 0)
    ast = stats.get("assists", 0)
    blk = stats.get("blocks", 0)
    tov = stats.get("turnovers", 0)
    pts = stats.get("points", 0)
    
    efficiency = (
        pts +
        reb +
        ast +
        stl +
        blk -
        ((fga - fg) + (fta - ft) + tov)
    )
    
    return round(efficiency, 1)

# Configure logging
logger = logging.getLogger(__name__)

# Role-based access control
admin_role = RoleChecker(["admin", "moderator"])

def calculate_performance_score(stats: PlayerStatsCreate) -> float:
    """
    Calculate a performance score based on player statistics.
    
    Args:
        stats: Player statistics data
        
    Returns:
        float: Calculated performance score
    """
    # This is a weighted formula that values different stats differently
    ps = (
        (stats.points * 1.0) + 
        (stats.assists * 0.5) + 
        (stats.rebounds * 0.3) +
        (stats.steals * 1.5) + 
        (stats.blocks * 1.5) - 
        (stats.turnovers * 0.5) +
        (stats.three_pointers_made * 0.5) +
        (stats.offensive_rebounds * 0.2) +
        (stats.defensive_rebounds * 0.1)
    )
    
    # Add bonus for double-doubles and triple-doubles
    categories = 0
    if stats.points >= 10: categories += 1
    if stats.assists >= 10: categories += 1
    if stats.rebounds >= 10: categories += 1
    if stats.steals >= 10: categories += 1
    if stats.blocks >= 10: categories += 1
    
    if categories >= 3:  # Triple-double or better
        ps += 10.0
    elif categories == 2:  # Double-double
        ps += 5.0
    
    # Ensure PS is not negative
    return max(0.0, round(ps, 2))

async def update_player_career_totals(player_id: str, client=None) -> None:
    """
    Update a player's career totals based on all their game stats.
    
    Args:
        player_id: The UUID of the player
        client: Optional Supabase client (for transactions)
        
    Raises:
        Exception: If there's an error updating the career totals
    """
    try:
        client = client or supabase.get_client()
        
        # Get all stats for the player
        result = client.table("player_stats")\
            .select("*")\
            .eq("player_id", str(player_id))\
            .execute()
        
        if not result.data:
            return
            
        # Calculate career totals
        totals = {
            "games_played": len(result.data),
            "points": 0,
            "assists": 0,
            "rebounds": 0,
            "steals": 0,
            "blocks": 0,
            "turnovers": 0,
            "field_goals_made": 0,
            "field_goals_attempted": 0,
            "three_pointers_made": 0,
            "three_pointers_attempted": 0,
            "free_throws_made": 0,
            "free_throws_attempted": 0,
            "offensive_rebounds": 0,
            "defensive_rebounds": 0,
            "fouls": 0,
            "plus_minus": 0,
            "minutes_played": 0,
            "double_doubles": 0,
            "triple_doubles": 0,
            "quadruple_doubles": 0,
            "quintuple_doubles": 0,
            "highest_points": 0,
            "highest_assists": 0,
            "highest_rebounds": 0,
            "highest_steals": 0,
            "highest_blocks": 0,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        # Process each game
        for game in result.data:
            # Update totals
            for stat in ["points", "assists", "rebounds", "steals", "blocks", 
                        "turnovers", "field_goals_made", "field_goals_attempted",
                        "three_pointers_made", "three_pointers_attempted",
                        "free_throws_made", "free_throws_attempted",
                        "offensive_rebounds", "defensive_rebounds",
                        "fouls", "plus_minus", "minutes_played"]:
                if game.get(stat) is not None:
                    totals[stat] += float(game[stat] or 0)
            
            # Check for double-doubles, triple-doubles, etc.
            categories = 0
            if game.get("points", 0) >= 10: categories += 1
            if game.get("assists", 0) >= 10: categories += 1
            if game.get("rebounds", 0) >= 10: categories += 1
            if game.get("steals", 0) >= 10: categories += 1
            if game.get("blocks", 0) >= 10: categories += 1
            
            if categories >= 5:
                totals["quintuple_doubles"] += 1
            elif categories >= 4:
                totals["quadruple_doubles"] += 1
            elif categories >= 3:
                totals["triple_doubles"] += 1
            elif categories >= 2:
                totals["double_doubles"] += 1
            
            # Update career highs
            for stat in ["points", "assists", "rebounds", "steals", "blocks"]:
                if game.get(stat, 0) > totals[f"highest_{stat}"]:
                    totals[f"highest_{stat}"] = game[stat]
        
        # Calculate percentages
        totals["field_goal_percentage"] = (
            (totals["field_goals_made"] / totals["field_goals_attempted"] * 100) 
            if totals["field_goals_attempted"] > 0 else 0
        )
        
        totals["three_point_percentage"] = (
            (totals["three_pointers_made"] / totals["three_pointers_attempted"] * 100) 
            if totals["three_pointers_attempted"] > 0 else 0
        )
        
        totals["free_throw_percentage"] = (
            (totals["free_throws_made"] / totals["free_throws_attempted"] * 100) 
            if totals["free_throws_attempted"] > 0 else 0
        )
        
        # Calculate per-game averages
        for stat in ["points", "assists", "rebounds", "steals", "blocks", 
                    "turnovers", "offensive_rebounds", "defensive_rebounds",
                    "minutes_played"]:
            totals[f"{stat}_per_game"] = (
                totals[stat] / totals["games_played"] 
                if totals["games_played"] > 0 else 0
            )
        
        # Update player record
        client.table("players")\
            .update(totals)\
            .eq("id", str(player_id))\
            .execute()
            
        logger.info(f"Updated career totals for player {player_id}")
        
    except Exception as e:
        logger.error(f"Error updating career totals for player {player_id}: {str(e)}", exc_info=True)
        raise

async def get_player_stats_by_id(stats_id: str) -> Optional[Dict[str, Any]]:
    """
    Helper function to get player stats by ID from Supabase.
    
    Args:
        stats_id: The UUID of the player stats record
        
    Returns:
        Optional[Dict[str, Any]]: The player stats record if found, None otherwise
        
    Raises:
        HTTPException: If there's an error fetching the stats
    """
    try:
        result = supabase.fetch_by_id("player_stats", stats_id)
        return result
    except Exception as e:
        logger.error(f"Error fetching player stats {stats_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch player statistics"
        )

@router.post(
    "/",
    response_model=PlayerStatsSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_role)],
    responses={
        201: {"description": "Player statistics created successfully"},
        400: {"description": "Invalid input data or duplicate entry"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Player, match, or team not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def create_player_stats(
    request: Request,
    stats: PlayerStatsCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Create new player statistics for a match.
    
    This endpoint allows administrators to record statistics for a player's performance
    in a specific match. The statistics include points, rebounds, assists, and other
    relevant metrics.
    
    Args:
        request: The FastAPI request object (used for rate limiting)
        stats: The player statistics data to create
        current_user: The authenticated user (from JWT token)
        
    Returns:
        Dict[str, Any]: The created player statistics record
        
    Raises:
        HTTPException: If validation fails or an error occurs
    """
    logger.info(f"Creating player stats for player {stats.player_id} in match {stats.match_id}")
    
    # Use a transaction to ensure data consistency
    with supabase.transaction() as transaction:
        try:
            client = transaction or supabase.get_client()
            
            # Check player exists
            player = client.table("players")\
                .select("gamertag,team_id")\
                .eq("id", str(stats.player_id))\
                .execute()
                
            if not player.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Player with ID {stats.player_id} not found"
                )
            
            # Check match exists and is completed
            match = client.table("matches")\
                .select("status,start_time")\
                .eq("id", str(stats.match_id))\
                .execute()
                
            if not match.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Match with ID {stats.match_id} not found"
                )
                
            if match.data[0].get("status") != "completed":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot add stats to a match that is not completed"
                )
            
            # Check team exists and player belongs to team
            team = client.table("teams")\
                .select("name")\
                .eq("id", str(stats.team_id))\
                .execute()
                
            if not team.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Team with ID {stats.team_id} not found"
                )
                
            if player.data[0].get("team_id") != str(stats.team_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Player {stats.player_id} is not on team {stats.team_id}"
                )
            
            # Check for duplicate stats
            existing_stats = client.table("player_stats")\
                .select("id")\
                .eq("player_id", str(stats.player_id))\
                .eq("match_id", str(stats.match_id))\
                .execute()
            
            if existing_stats.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Statistics already exist for this player in the specified match"
                )
            
            # Prepare data for insertion
            stats_data = stats.model_dump(exclude_unset=True)
            stats_data.update({
                "player_name": player.data[0]["gamertag"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "created_by": current_user.get("id"),
                "team_name": team.data[0]["name"],
                "match_date": match.data[0].get("start_time")
            })
            
            # Calculate performance score (PS) if not provided
            if "ps" not in stats_data or stats_data["ps"] is None:
                stats_data["ps"] = calculate_performance_score(stats)
            
            # Insert the stats
            created_stats = supabase.insert("player_stats", stats_data, client=transaction)
            
            # Update player's career totals asynchronously
            await update_player_career_totals(stats.player_id, transaction)
            
            logger.info(f"Successfully created player stats: {created_stats.get('id')}")
            return created_stats
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating player stats: {str(e)}", exc_info=True)
            if transaction:
                transaction.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create player statistics"
            )

@router.get(
    "/{stats_id}",
    response_model=PlayerStatsWithDetails,
    responses={
        200: {"description": "Player statistics retrieved successfully"},
        404: {"description": "Player statistics not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_player_stats(
    request: Request,
    stats_id: str
) -> Dict[str, Any]:
    """
    Get detailed player statistics by ID.
    
    This endpoint retrieves comprehensive player statistics for a specific game,
    including related player, match, and team information.
    
    Args:
        request: The FastAPI request object (used for rate limiting)
        stats_id: The UUID of the player statistics record
        
    Returns:
        Dict[str, Any]: Detailed player statistics with related information
        
    Raises:
        HTTPException: If the statistics record is not found or an error occurs
    """
    try:
        logger.info(f"Fetching player stats with ID: {stats_id}")
        
        # Get the base stats
        stats = await get_player_stats_by_id(stats_id)
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Player statistics with ID {stats_id} not found"
            )
        
        # Get related data in parallel for better performance
        client = supabase.get_client()
        
        # Get player details
        player_future = client.table("players").select("*")\
            .eq("id", stats["player_id"])\
            .single()\
            .execute()
        
        # Get match details
        match_future = client.table("matches").select("*")\
            .eq("id", stats["match_id"])\
            .single()\
            .execute()
        
        # Get team details
        team_future = client.table("teams").select("*")\
            .eq("id", stats["team_id"])\
            .single()\
            .execute()
        
        # Wait for all queries to complete
        player = player_future
        match = match_future
        team = team_future
        
        # Check for errors in any of the queries
        if not player.data:
            logger.warning(f"Player not found for stats ID {stats_id}")
        if not match.data:
            logger.warning(f"Match not found for stats ID {stats_id}")
        if not team.data:
            logger.warning(f"Team not found for stats ID {stats_id}")
        
        # Calculate additional derived stats if not present
        if "game_score" not in stats:
            stats["game_score"] = calculate_game_score(stats)
            
        if "efficiency" not in stats:
            stats["efficiency"] = calculate_efficiency(stats)
        
        return {
            **stats,
            "player": player.data or {},
            "match": match.data or {},
            "team": team.data or {}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching player stats {stats_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve player statistics"
        )

@router.get(
    "/",
    response_model=List[PlayerStatsSchema],
    responses={
        200: {"description": "List of player statistics retrieved successfully"},
        400: {"description": "Invalid query parameters"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_player_stats(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    player_id: Optional[UUID] = Query(None, description="Filter by player ID"),
    match_id: Optional[UUID] = Query(None, description="Filter by match ID"),
    team_id: Optional[UUID] = Query(None, description="Filter by team ID"),
    min_points: Optional[int] = Query(None, ge=0, description="Minimum points scored"),
    max_points: Optional[int] = Query(None, ge=0, description="Maximum points scored"),
    min_assists: Optional[int] = Query(None, ge=0, description="Minimum assists"),
    min_rebounds: Optional[int] = Query(None, ge=0, description="Minimum rebounds"),
    min_steals: Optional[int] = Query(None, ge=0, description="Minimum steals"),
    min_blocks: Optional[int] = Query(None, ge=0, description="Minimum blocks"),
    min_three_pointers: Optional[int] = Query(None, ge=0, description="Minimum three-pointers made"),
    sort_by: str = Query("created_at", description="Field to sort by (e.g., 'points', 'assists', 'created_at')"),
    sort_order: str = Query("desc", description="Sort order ('asc' or 'desc')", pattern="^(asc|desc)$"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date")
) -> List[Dict[str, Any]]:
    """
    List and filter player statistics with pagination and sorting.
    
    This endpoint allows querying player statistics with various filters and sorting options.
    Results are paginated and can be sorted by any stat field.
    
    Args:
        request: The FastAPI request object (used for rate limiting)
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return (max 1000)
        player_id: Filter by player UUID
        match_id: Filter by match UUID
        team_id: Filter by team UUID
        min_points: Filter by minimum points scored
        max_points: Filter by maximum points scored
        min_assists: Filter by minimum assists
        min_rebounds: Filter by minimum rebounds
        min_steals: Filter by minimum steals
        min_blocks: Filter by minimum blocks
        min_three_pointers: Filter by minimum three-pointers made
        sort_by: Field to sort results by
        sort_order: Sort order ('asc' or 'desc')
        start_date: Filter by start date (inclusive)
        end_date: Filter by end date (inclusive)
        
    Returns:
        List[Dict[str, Any]]: List of player statistics matching the criteria
        
    Raises:
        HTTPException: If there's an error executing the query
    """
    try:
        logger.info(f"Listing player stats with filters: {locals()}")
        
        # Input validation
        if start_date and end_date and start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date cannot be after end date"
            )
            
        if min_points is not None and max_points is not None and min_points > max_points:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum points cannot be greater than maximum points"
            )
        
        # Build the query
        query = supabase.get_client().table("player_stats").select("*")
        
        # Apply filters
        if player_id:
            query = query.eq("player_id", str(player_id))
        if match_id:
            query = query.eq("match_id", str(match_id))
        if team_id:
            query = query.eq("team_id", str(team_id))
        if min_points is not None:
            query = query.gte("points", min_points)
        if max_points is not None:
            query = query.lte("points", max_points)
        if min_assists is not None:
            query = query.gte("assists", min_assists)
        if min_rebounds is not None:
            query = query.gte("rebounds", min_rebounds)
        if min_steals is not None:
            query = query.gte("steals", min_steals)
        if min_blocks is not None:
            query = query.gte("blocks", min_blocks)
        if min_three_pointers is not None:
            query = query.gte("three_pointers_made", min_three_pointers)
        if start_date:
            query = query.gte("created_at", start_date.isoformat())
        if end_date:
            # Include the entire end date
            end_of_day = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.lte("created_at", end_of_day.isoformat())
        
        # Apply sorting
        if sort_order.lower() == "asc":
            query = query.order(sort_by, desc=False)
        else:
            query = query.order(sort_by, desc=True)
        
        # Apply pagination
        query = query.range(skip, skip + limit - 1)
        
        # Execute the query
        result = query.execute()
        
        # Calculate derived stats if not present
        stats_list = result.data if hasattr(result, 'data') else []
        for stat in stats_list:
            if "game_score" not in stat:
                stat["game_score"] = calculate_game_score(stat)
            if "efficiency" not in stat:
                stat["efficiency"] = calculate_efficiency(stat)
        
        return stats_list
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing player stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve player statistics"
        )
    
    result = query.range(skip, skip + limit - 1).execute()
    
    # If we joined with matches, we need to extract just the player_stats data
    if start_date or end_date:
        return [item for item in result.data if item]
    return result.data if hasattr(result, 'data') else []

@router.put("/{stats_id}", response_model=PlayerStatsSchema)
async def update_player_stats(
    stats_id: str,
    stats_update: PlayerStatsUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Update player statistics
    """
    # Check if stats exist
    stats = await get_player_stats_by_id(stats_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player statistics not found"
        )
    
    # Check if user has permission to update the stats
    # Note: Add your permission logic here
    
    # Prepare update data
    update_data = stats_update.model_dump(exclude_unset=True)
    
    # Recalculate performance score if relevant fields are being updated
    if any(field in update_data for field in ["points", "assists", "rebounds", "steals", "blocks", "turnovers"]):
        points = update_data.get("points", stats["points"])
        assists = update_data.get("assists", stats["assists"])
        rebounds = update_data.get("rebounds", stats["rebounds"])
        steals = update_data.get("steals", stats["steals"])
        blocks = update_data.get("blocks", stats["blocks"])
        turnovers = update_data.get("turnovers", stats["turnovers"])
        
        # Recalculate performance score
        ps = (points * 1.0) + (assists * 0.5) + (rebounds * 0.3) + \
             (steals * 1.5) + (blocks * 1.5) - (turnovers * 0.5)
        update_data["ps"] = max(0, ps)  # Ensure PS is not negative
    
    try:
        updated_stats = supabase.update("player_stats", stats_id, update_data)
        return updated_stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update player stats: {str(e)}"
        )

@router.delete("/{stats_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player_stats(
    stats_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Delete player statistics
    """
    # Check if stats exist
    stats = await get_player_stats_by_id(stats_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player statistics not found"
        )
    
    # Check if user has permission to delete the stats
    # Note: Add your permission logic here
    
    try:
        supabase.delete("player_stats", stats_id)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete player stats: {str(e)}"
        )

@router.get("/player/{player_id}/history", response_model=List[PlayerStatsWithDetails])
async def get_player_stats_history(
    player_id: str,
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """
    Get match history for a specific player with detailed statistics
    """
    client = supabase.get_client()
    
    # Get player stats with match details
    result = client.table("player_stats")\
        .select("*, matches(*)")\
        .eq("player_id", player_id)\
        .order("matches.played_at", desc=True)\
        .range(skip, skip + limit - 1)\
        .execute()
    
    if not result.data:
        return []
    
    # Get player and team details
    player = client.table("players").select("*").eq("id", player_id).execute()
    
    # Format the response
    stats_list = []
    for stat in result.data:
        if not stat:
            continue
            
        # Get team details
        team = client.table("teams").select("*").eq("id", stat["team_id"]).execute()
        
        # Create the stats with details
        stats_with_details = dict(stat)
        stats_with_details["player"] = player.data[0] if player.data else None
        stats_with_details["match"] = stat.get("matches")
        stats_with_details["team"] = team.data[0] if team.data else None
        
        # Remove the nested matches data to avoid duplication
        if "matches" in stats_with_details:
            del stats_with_details["matches"]
            
        stats_list.append(stats_with_details)
    
    return stats_list

@router.get("/match/{match_id}/team/{team_id}", response_model=List[PlayerStatsWithDetails])
async def get_team_stats_for_match(
    match_id: str,
    team_id: str,
    min_minutes: Optional[int] = None
):
    """
    Get all player statistics for a specific team in a specific match
    """
    client = supabase.get_client()
    
    # Build the query
    query = client.table("player_stats")\
        .select("*, players(*)")\
        .eq("match_id", match_id)\
        .eq("team_id", team_id)
    
    if min_minutes is not None:
        # Assuming we have a minutes_played column
        query = query.gte("minutes_played", min_minutes)
    
    result = query.execute()
    
    if not result.data:
        return []
    
    # Get team and match details
    team = client.table("teams").select("*").eq("id", team_id).execute()
    match = client.table("matches").select("*").eq("id", match_id).execute()
    
    # Format the response
    stats_list = []
    for stat in result.data:
        if not stat:
            continue
            
        stats_with_details = dict(stat)
        stats_with_details["player"] = stat.get("players")
        stats_with_details["match"] = match.data[0] if match.data else None
        stats_with_details["team"] = team.data[0] if team.data else None
        
        # Remove the nested players data to avoid duplication
        if "players" in stats_with_details:
            del stats_with_details["players"]
            
        stats_list.append(stats_with_details)
    
    return stats_list
