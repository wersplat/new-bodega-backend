"""
Leaderboard router for global and event rankings using Supabase
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, List, Optional
from enum import Enum

from app.core.supabase import supabase
from app.schemas.player import PlayerProfile, PlayerTier

router = APIRouter()

class LeaderboardSortBy(str, Enum):
    # Using player_rp instead of current_rp to match Supabase schema
    CURRENT_RP = "player_rp"
    PEAK_RP = "player_rank_score"  # Using player_rank_score as peak RP
    WINS = "wins"
    WIN_RATE = "win_rate"
    RANK = "rank"  # Fallback column if others don't exist

@router.get("/global", response_model=List[PlayerProfile])
def get_global_leaderboard(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    tier: Optional[PlayerTier] = None,
    sort_by: LeaderboardSortBy = LeaderboardSortBy.CURRENT_RP,
    descending: bool = True
):
    """
    Get global leaderboard with various sorting options
    """
    client = supabase.get_client()
    
    # Build the query
    query = client.table("players").select("*")
    
    # Apply filters
    if tier:
        query = query.eq("tier", tier.value)
    
    # Apply sorting with fallback if column doesn't exist
    sort_order = "desc" if descending else "asc"
    try:
        # First try the requested sort column
        query = query.order(sort_by.value, desc=descending)
    except Exception as e:
        if "column" in str(e) and "does not exist" in str(e):
            # If the column doesn't exist, try fallback columns
            fallback_columns = ["rank", "id", "created_at"]
            for col in fallback_columns:
                try:
                    query = query.order(col, desc=descending)
                    break
                except:
                    continue
        else:
            # Re-raise if it's a different error
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort column: {sort_by.value}"
            )
    
    # Apply pagination
    query = query.range(offset, offset + limit - 1)
    
    result = query.execute()
    return result.data if hasattr(result, 'data') else []

@router.get("/global/top", response_model=List[PlayerProfile])
def get_top_players(
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get top players globally by player RP
    """
    client = supabase.get_client()
    result = client.table("players") \
        .select("*") \
        .order("player_rp", desc=True) \
        .limit(limit) \
        .execute()
    
    return result.data if hasattr(result, 'data') else []

@router.get("/tier/{tier}", response_model=List[PlayerProfile])
def get_tier_leaderboard(
    tier: PlayerTier,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Get leaderboard for a specific tier
    """
    client = supabase.get_client()
    result = client.table("players") \
        .select("*") \
        .eq("tier", tier.value) \
        .order("player_rp", desc=True) \
        .range(offset, offset + limit - 1) \
        .execute()
    
    return result.data if hasattr(result, 'data') else []

@router.get("/event/{event_id}", response_model=List[Dict])
def get_event_leaderboard(event_id: str):
    """
    Get leaderboard for a specific event with optimized queries
    """
    # First verify the event exists using optimized primary key lookup
    event = supabase.fetch_by_id("events", event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Get event registrations with player details in a single optimized query
    client = supabase.get_client()
    result = client.table("event_registrations") \
        .select("*, player:players(*)") \
        .eq("event_id", event_id) \
        .order("final_rank", desc=False) \
        .execute()
    
    return result.data if hasattr(result, 'data') else []

@router.get("/peak-rp", response_model=List[PlayerProfile])
def get_peak_rp_leaderboard(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Get leaderboard by peak RP
    """
    client = supabase.get_client()
    result = client.table("players") \
        .select("*") \
        .order("player_rank_score", desc=True) \
        .range(offset, offset + limit - 1) \
        .execute()
    
    return result.data if hasattr(result, 'data') else []

@router.get("/region/{region}", response_model=List[PlayerProfile])
def get_region_leaderboard(
    region: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Get leaderboard for a specific region
    """
    client = supabase.get_client()
    result = client.table("players") \
        .select("*") \
        .eq("region", region.upper()) \
        .order("player_rp", desc=True) \
        .range(offset, offset + limit - 1) \
        .execute()
    
    return result.data if hasattr(result, 'data') else []
