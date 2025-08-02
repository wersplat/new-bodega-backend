"""
Matches router for match management and lookups
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from app.core.supabase import supabase
from app.core.auth import get_current_active_user
from app.schemas.match import MatchCreate, Match as MatchSchema, MatchUpdate, MatchWithDetails
from app.schemas.player_stats import PlayerStats as PlayerStatsSchema

router = APIRouter(prefix="/matches", tags=["matches"])

async def get_match_by_id(match_id: str) -> Optional[Dict[str, Any]]:
    """Helper function to get a match by ID from Supabase"""
    result = supabase.fetch_by_id("matches", match_id)
    return result

@router.post("/", response_model=MatchSchema, status_code=status.HTTP_201_CREATED)
async def create_match(
    match: MatchCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Create a new match
    """
    # Validate that teams exist and are different
    if match.team_a_id == match.team_b_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team A and Team B must be different"
        )
    
    # Validate teams exist
    client = supabase.get_client()
    team_a = client.table("teams").select("name").eq("id", str(match.team_a_id)).execute()
    team_b = client.table("teams").select("name").eq("id", str(match.team_b_id)).execute()
    
    if not team_a.data or not team_b.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both teams not found"
        )
    
    # Validate event exists if provided
    if match.event_id:
        event = client.table("events").select("id").eq("id", str(match.event_id)).execute()
        if not event.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {match.event_id} not found"
            )
    
    # Set default values
    match_data = match.model_dump()
    match_data["team_a_name"] = team_a.data[0]["name"]
    match_data["team_b_name"] = team_b.data[0]["name"]
    
    # Set winner based on scores if not provided
    if match.winner_id is None:
        if match.score_a > match.score_b:
            match_data["winner_id"] = match.team_a_id
            match_data["winner_name"] = team_a.data[0]["name"]
        elif match.score_b > match.score_a:
            match_data["winner_id"] = match.team_b_id
            match_data["winner_name"] = team_b.data[0]["name"]
        # If scores are equal, winner remains None (tie)
    else:
        # Set winner name if winner_id is provided
        winner = team_a if match.winner_id == match.team_a_id else team_b
        match_data["winner_name"] = winner.data[0]["name"]
    
    # Set played_at to now if not provided
    if not match.played_at:
        match_data["played_at"] = datetime.now(timezone.utc).isoformat()
    
    try:
        created_match = supabase.insert("matches", match_data)
        return created_match
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create match: {str(e)}"
        )

@router.get("/{match_id}", response_model=MatchWithDetails)
async def get_match(match_id: str):
    """
    Get match details by ID
    """
    match = await get_match_by_id(match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Get player stats for this match
    client = supabase.get_client()
    stats_result = client.table("player_stats").select("*").eq("match_id", match_id).execute()
    
    match_with_details = dict(match)
    match_with_details["player_stats"] = stats_result.data if hasattr(stats_result, 'data') else []
    
    return match_with_details

@router.get("/", response_model=List[MatchSchema])
async def list_matches(
    skip: int = 0,
    limit: int = 100,
    team_id: Optional[UUID] = None,
    event_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """
    List matches with optional filtering
    """
    client = supabase.get_client()
    query = client.table("matches").select("*")
    
    if team_id:
        query = query.or_(f"team_a_id.eq.{team_id},team_b_id.eq.{team_id}")
    if event_id:
        query = query.eq("event_id", str(event_id))
    if start_date:
        query = query.gte("played_at", start_date.isoformat())
    if end_date:
        query = query.lte("played_at", end_date.isoformat())
    
    # Order by most recent first
    query = query.order("played_at", desc=True)
    
    result = query.range(skip, skip + limit - 1).execute()
    return result.data if hasattr(result, 'data') else []

@router.put("/{match_id}", response_model=MatchSchema)
async def update_match(
    match_id: str,
    match_update: MatchUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Update match information
    """
    # Check if match exists
    match = await get_match_by_id(match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Check if user has permission to update the match
    # Note: Add your permission logic here
    
    # Validate teams if being updated
    update_data = match_update.model_dump(exclude_unset=True)
    
    if "team_a_id" in update_data or "team_b_id" in update_data:
        team_a_id = update_data.get("team_a_id", match["team_a_id"])
        team_b_id = update_data.get("team_b_id", match["team_b_id"])
        
        if team_a_id == team_b_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team A and Team B must be different"
            )
        
        # Get team names if teams are being updated
        client = supabase.get_client()
        if "team_a_id" in update_data:
            team_a = client.table("teams").select("name").eq("id", str(team_a_id)).execute()
            if not team_a.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Team A with ID {team_a_id} not found"
                )
            update_data["team_a_name"] = team_a.data[0]["name"]
        
        if "team_b_id" in update_data:
            team_b = client.table("teams").select("name").eq("id", str(team_b_id)).execute()
            if not team_b.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Team B with ID {team_b_id} not found"
                )
            update_data["team_b_name"] = team_b.data[0]["name"]
    
    # Update winner if scores are updated
    if "score_a" in update_data or "score_b" in update_data:
        score_a = update_data.get("score_a", match["score_a"])
        score_b = update_data.get("score_b", match["score_b"])
        
        if score_a > score_b:
            update_data["winner_id"] = match["team_a_id"]
            update_data["winner_name"] = match["team_a_name"]
        elif score_b > score_a:
            update_data["winner_id"] = match["team_b_id"]
            update_data["winner_name"] = match["team_b_name"]
        else:
            # Tie
            update_data["winner_id"] = None
            update_data["winner_name"] = None
    
    try:
        updated_match = supabase.update("matches", match_id, update_data)
        return updated_match
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update match: {str(e)}"
        )

@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_match(
    match_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Delete a match
    """
    # Check if match exists
    match = await get_match_by_id(match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Check if user has permission to delete the match
    # Note: Add your permission logic here
    
    try:
        # First, delete all player stats for this match
        client = supabase.get_client()
        client.table("player_stats").delete().eq("match_id", match_id).execute()
        
        # Then delete the match
        supabase.delete("matches", match_id)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete match: {str(e)}"
        )

@router.get("/team/{team_id}", response_model=List[MatchSchema])
async def get_team_matches(
    team_id: str,
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """
    Get all matches for a specific team
    """
    client = supabase.get_client()
    result = client.table("matches")\
        .select("*")\
        .or_(f"team_a_id.eq.{team_id},team_b_id.eq.{team_id}")\
        .order("played_at", desc=True)\
        .range(skip, skip + limit - 1)\
        .execute()
    
    return result.data if hasattr(result, 'data') else []

@router.get("/event/{event_id}", response_model=List[MatchSchema])
async def get_event_matches(
    event_id: str,
    stage: Optional[str] = None,
    limit: int = Query(100, ge=1, le=200),
    skip: int = Query(0, ge=0)
):
    """
    Get all matches for a specific event, optionally filtered by stage
    """
    client = supabase.get_client()
    query = client.table("matches")\
        .select("*")\
        .eq("event_id", event_id)
    
    if stage:
        query = query.eq("stage", stage)
    
    result = query.order("played_at", desc=True)\
                 .range(skip, skip + limit - 1)\
                 .execute()
    
    return result.data if hasattr(result, 'data') else []
