"""
Player Stats router for managing and querying player statistics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from app.core.supabase import supabase
from app.core.auth import get_current_active_user
from app.schemas.player_stats import PlayerStats as PlayerStatsSchema, PlayerStatsCreate, PlayerStatsUpdate, PlayerStatsWithDetails

router = APIRouter(prefix="/player-stats", tags=["player-stats"])

async def get_player_stats_by_id(stats_id: str) -> Optional[Dict[str, Any]]:
    """Helper function to get player stats by ID from Supabase"""
    result = supabase.fetch_by_id("player_stats", stats_id)
    return result

@router.post("/", response_model=PlayerStatsSchema, status_code=status.HTTP_201_CREATED)
async def create_player_stats(
    stats: PlayerStatsCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Create new player statistics for a match
    """
    # Validate that player, match, and team exist
    client = supabase.get_client()
    
    # Check player exists
    player = client.table("players").select("gamertag").eq("id", str(stats.player_id)).execute()
    if not player.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {stats.player_id} not found"
        )
    
    # Check match exists
    match = client.table("matches").select("*").eq("id", str(stats.match_id)).execute()
    if not match.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {stats.match_id} not found"
        )
    
    # Check team exists
    team = client.table("teams").select("name").eq("id", str(stats.team_id)).execute()
    if not team.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {stats.team_id} not found"
        )
    
    # Check if stats already exist for this player in this match
    existing_stats = client.table("player_stats")\
        .select("*")\
        .eq("player_id", str(stats.player_id))\
        .eq("match_id", str(stats.match_id))\
        .execute()
    
    if existing_stats.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Statistics already exist for this player in the specified match"
        )
    
    # Prepare data for insertion
    stats_data = stats.model_dump()
    stats_data["player_name"] = player.data[0]["gamertag"]
    stats_data["created_at"] = datetime.now(timezone.utc).isoformat()
    
    # Calculate performance score (ps) if not provided
    if "ps" not in stats_data or stats_data["ps"] is None:
        # This is a simplified calculation - adjust based on your actual formula
        ps = (stats.points * 1.0) + (stats.assists * 0.5) + (stats.rebounds * 0.3) + \
             (stats.steals * 1.5) + (stats.blocks * 1.5) - (stats.turnovers * 0.5)
        stats_data["ps"] = max(0, ps)  # Ensure PS is not negative
    
    try:
        created_stats = supabase.insert("player_stats", stats_data)
        return created_stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create player stats: {str(e)}"
        )

@router.get("/{stats_id}", response_model=PlayerStatsWithDetails)
async def get_player_stats(stats_id: str):
    """
    Get player statistics by ID
    """
    stats = await get_player_stats_by_id(stats_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player statistics not found"
        )
    
    # Get additional details
    client = supabase.get_client()
    
    # Get player details
    player = client.table("players").select("*").eq("id", stats["player_id"]).execute()
    
    # Get match details
    match = client.table("matches").select("*").eq("id", stats["match_id"]).execute()
    
    # Get team details
    team = client.table("teams").select("*").eq("id", stats["team_id"]).execute()
    
    # Combine all data
    stats_with_details = dict(stats)
    stats_with_details["player"] = player.data[0] if player.data else None
    stats_with_details["match"] = match.data[0] if match.data else None
    stats_with_details["team"] = team.data[0] if team.data else None
    
    return stats_with_details

@router.get("/", response_model=List[PlayerStatsSchema])
async def list_player_stats(
    skip: int = 0,
    limit: int = 100,
    player_id: Optional[UUID] = None,
    match_id: Optional[UUID] = None,
    team_id: Optional[UUID] = None,
    min_points: Optional[int] = None,
    min_assists: Optional[int] = None,
    min_rebounds: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """
    List player statistics with optional filtering
    """
    client = supabase.get_client()
    query = client.table("player_stats").select("*")
    
    if player_id:
        query = query.eq("player_id", str(player_id))
    if match_id:
        query = query.eq("match_id", str(match_id))
    if team_id:
        query = query.eq("team_id", str(team_id))
    if min_points is not None:
        query = query.gte("points", min_points)
    if min_assists is not None:
        query = query.gte("assists", min_assists)
    if min_rebounds is not None:
        query = query.gte("rebounds", min_rebounds)
    if start_date or end_date:
        # Join with matches table to filter by date
        query = query.select("*, matches(*)")
        if start_date:
            query = query.gte("matches.played_at", start_date.isoformat())
        if end_date:
            query = query.lte("matches.played_at", end_date.isoformat())
    
    # Order by most recent first (requires join with matches)
    if start_date or end_date:
        query = query.order("matches.played_at", desc=True)
    
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
