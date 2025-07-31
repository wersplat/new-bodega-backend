"""
Leaderboard router for global and event rankings using Supabase
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from enum import Enum

from app.core.supabase import supabase
from app.schemas.player import PlayerProfile, PlayerTier

router = APIRouter()

class LeaderboardSortBy(str, Enum):
    CURRENT_RP = "current_rp"
    PEAK_RP = "peak_rp"
    WINS = "wins"
    WIN_RATE = "win_rate"

@router.get("/global", response_model=List[PlayerProfile])
async def get_global_leaderboard(
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
    
    # Apply sorting
    sort_order = "desc" if descending else "asc"
    query = query.order(sort_by.value, desc=descending)
    
    # Apply pagination
    query = query.range(offset, offset + limit - 1)
    
    try:
        result = query.execute()
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch leaderboard: {str(e)}"
        )

@router.get("/global/top", response_model=List[PlayerProfile])
async def get_top_players(
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get top players globally by current RP
    """
    client = supabase.get_client()
    
    try:
        result = client.table("players") \
            .select("*") \
            .order("current_rp", desc=True) \
            .limit(limit) \
            .execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch top players: {str(e)}"
        )

@router.get("/tier/{tier}", response_model=List[PlayerProfile])
async def get_tier_leaderboard(
    tier: PlayerTier,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Get leaderboard for a specific tier
    """
    client = supabase.get_client()
    
    try:
        result = client.table("players") \
            .select("*") \
            .eq("tier", tier.value) \
            .order("current_rp", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch {tier.value} leaderboard: {str(e)}"
        )

@router.get("/event/{event_id}", response_model=List[dict])
async def get_event_leaderboard(event_id: str):
    """
    Get leaderboard for a specific event
    """
    client = supabase.get_client()
    
    try:
        # First, verify the event exists
        event = supabase.fetch_by_id("events", event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        # Get event results with player details
        result = client.rpc('get_event_leaderboard', {'event_id': event_id}).execute()
        
        if hasattr(result, 'data') and result.data:
            return result.data
        else:
            # Fallback to simpler query if the RPC function doesn't exist
            result = client.table("event_results") \
                .select("*, players(*)") \
                .eq("event_id", event_id) \
                .order("position", desc=False) \
                .execute()
            
            return result.data if hasattr(result, 'data') else []
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch event leaderboard: {str(e)}"
        )

@router.get("/peak-rp", response_model=List[PlayerProfile])
async def get_peak_rp_leaderboard(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Get leaderboard by peak RP
    """
    client = supabase.get_client()
    
    try:
        result = client.table("players") \
            .select("*") \
            .order("peak_rp", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch peak RP leaderboard: {str(e)}"
        )

@router.get("/platform/{platform}", response_model=List[PlayerProfile])
async def get_platform_leaderboard(
    platform: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Get leaderboard for a specific platform
    """
    client = supabase.get_client()
    
    try:
        result = client.table("players") \
            .select("*") \
            .eq("platform", platform.lower()) \
            .order("current_rp", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch {platform} leaderboard: {str(e)}"
        )

@router.get("/region/{region}", response_model=List[PlayerProfile])
async def get_region_leaderboard(
    region: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Get leaderboard for a specific region
    """
    client = supabase.get_client()
    
    try:
        result = client.table("players") \
            .select("*") \
            .eq("region", region.upper()) \
            .order("current_rp", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch {region} leaderboard: {str(e)}"
        )
