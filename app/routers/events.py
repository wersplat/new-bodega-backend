"""
Events Router

This module provides API endpoints for managing events, event results, and event tiers.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from pydantic import BaseModel, ConfigDict, Field

from app.core.supabase import supabase
from app.core.auth_supabase import require_admin_api_token
from app.core.rate_limiter import limiter
from app.core.config import settings
from app.schemas.enums import EventTier as EventTierEnum, EventType as EventTypeEnum

# Initialize router
router = APIRouter(
    prefix="/v1/events",
    tags=["Events"],
    responses={404: {"description": "Not found"}},
)

# Configure logging
logger = logging.getLogger(__name__)

# Pydantic Models

class EventResultBase(BaseModel):
    """Base event result model"""
    team_id: str = Field(..., description="Team UUID")
    placement: Optional[int] = Field(None, ge=1, description="Final placement")
    rp_awarded: Optional[int] = Field(None, ge=0, description="RP awarded")
    bonus_rp: Optional[int] = Field(0, ge=0, description="Bonus RP")
    prize_amount: Optional[int] = Field(None, ge=0, description="Prize money won")
    league_id: Optional[str] = None
    tournament_id: Optional[str] = None
    season_id: Optional[str] = None
    rp_decay_start_days: Optional[int] = Field(None, ge=0, description="Days before decay starts")
    winner_banner_url: Optional[str] = None

class EventResultCreate(EventResultBase):
    """Create event result request"""
    pass

class EventResultUpdate(BaseModel):
    """Update event result request"""
    placement: Optional[int] = Field(None, ge=1)
    rp_awarded: Optional[int] = Field(None, ge=0)
    bonus_rp: Optional[int] = Field(None, ge=0)
    prize_amount: Optional[int] = Field(None, ge=0)
    remaining_rp: Optional[int] = Field(None, ge=0)
    last_decay_date: Optional[str] = None
    winner_banner_url: Optional[str] = None

class EventResult(EventResultBase):
    """Event result response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    total_rp: Optional[int] = None
    remaining_rp: Optional[int] = None
    last_decay_date: Optional[str] = None
    awarded_at: Optional[str] = None

class EventTierBase(BaseModel):
    """Base event tier model"""
    event_tier: Optional[EventTierEnum] = Field(None, description="Tier code (T1-T5)")
    tier_name: Optional[str] = Field(None, description="Tier display name")
    event_type: Optional[EventTypeEnum] = Field(None, description="Event type")
    is_tournament: Optional[bool] = None
    max_rp: Optional[int] = Field(None, ge=0, description="Maximum RP for this tier")
    player_rp_bonus: Optional[int] = Field(None, ge=0, description="Bonus RP for players")

class EventTierCreate(EventTierBase):
    """Create event tier request"""
    pass

class EventTierUpdate(BaseModel):
    """Update event tier request"""
    tier_name: Optional[str] = None
    event_type: Optional[EventTypeEnum] = None
    is_tournament: Optional[bool] = None
    max_rp: Optional[int] = Field(None, ge=0)
    player_rp_bonus: Optional[int] = Field(None, ge=0)

class EventTier(EventTierBase):
    """Event tier response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    created_at: str

class EventQueueItem(BaseModel):
    """Event queue item response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    player_stats_id: str
    status: str
    attempts: int
    last_error: Optional[str] = None
    visible_at: str
    created_at: str
    updated_at: str

# Event Results Endpoints

@router.get(
    "/results/",
    response_model=List[EventResult],
    summary="List event results"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_event_results(
    request: Request,
    team_id: Optional[str] = Query(None, description="Filter by team ID"),
    league_id: Optional[str] = Query(None, description="Filter by league ID"),
    tournament_id: Optional[str] = Query(None, description="Filter by tournament ID"),
    season_id: Optional[str] = Query(None, description="Filter by season ID"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    List event results with optional filtering.
    
    Returns placement and RP results for teams in events (tournaments/leagues).
    """
    try:
        query = supabase.get_client().table("event_results").select("*")
        
        if team_id:
            query = query.eq("team_id", team_id)
        if league_id:
            query = query.eq("league_id", league_id)
        if tournament_id:
            query = query.eq("tournament_id", tournament_id)
        if season_id:
            query = query.eq("season_id", season_id)
            
        query = query.order("awarded_at", desc=True).range(offset, offset + limit - 1)
        result = query.execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching event results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch event results"
        )

@router.get(
    "/results/{result_id}",
    response_model=EventResult,
    summary="Get event result by ID"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_event_result_by_id(
    request: Request,
    result_id: str
) -> Dict[str, Any]:
    """Get a specific event result by ID."""
    try:
        result = supabase.get_by_id("event_results", result_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event result not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching event result {result_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch event result"
        )

@router.post(
    "/results/",
    response_model=EventResult,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_api_token)],
    summary="Create event result"
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def create_event_result(
    request: Request,
    event_result: EventResultCreate
) -> Dict[str, Any]:
    """Create a new event result (admin only)."""
    try:
        # Verify team exists
        team_result = supabase.get_client().table("teams").select("id").eq("id", event_result.team_id).execute()
        if not team_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        result_data = event_result.model_dump()
        result_data["id"] = str(uuid4())
        result_data["awarded_at"] = datetime.utcnow().date().isoformat()
        
        # Calculate total_rp (rp_awarded + bonus_rp)
        result_data["total_rp"] = result_data.get("rp_awarded", 0) + result_data.get("bonus_rp", 0)
        result_data["remaining_rp"] = result_data["total_rp"]
        
        result = supabase.insert("event_results", result_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating event result: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create event result"
        )

@router.put(
    "/results/{result_id}",
    response_model=EventResult,
    dependencies=[Depends(require_admin_api_token)],
    summary="Update event result"
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def update_event_result(
    request: Request,
    result_id: str,
    result_update: EventResultUpdate
) -> Dict[str, Any]:
    """Update an event result (admin only)."""
    try:
        update_data = {k: v for k, v in result_update.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        result = supabase.update("event_results", result_id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event result not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating event result {result_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update event result"
        )

@router.delete(
    "/results/{result_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_api_token)],
    summary="Delete event result"
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def delete_event_result(
    request: Request,
    result_id: str
):
    """Delete an event result (admin only)."""
    try:
        result = supabase.delete("event_results", result_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event result not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting event result {result_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete event result"
        )

# Event Tiers Endpoints

@router.get(
    "/tiers/",
    response_model=List[EventTier],
    summary="List event tiers"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_event_tiers(
    request: Request,
    event_type: Optional[EventTypeEnum] = Query(None, description="Filter by event type"),
    is_tournament: Optional[bool] = Query(None, description="Filter tournament vs league"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    List all event tiers with optional filtering.
    
    Event tiers define the competitive level and reward structure for events.
    """
    try:
        query = supabase.get_client().table("event_tiers").select("*")
        
        if event_type:
            query = query.eq("event_type", event_type.value)
        if is_tournament is not None:
            query = query.eq("is_tournament", is_tournament)
            
        query = query.order("event_tier").range(offset, offset + limit - 1)
        result = query.execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching event tiers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch event tiers"
        )

@router.get(
    "/tiers/{tier_id}",
    response_model=EventTier,
    summary="Get event tier by ID"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_event_tier_by_id(
    request: Request,
    tier_id: str
) -> Dict[str, Any]:
    """Get a specific event tier by ID."""
    try:
        result = supabase.get_by_id("event_tiers", tier_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event tier not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching event tier {tier_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch event tier"
        )

@router.post(
    "/tiers/",
    response_model=EventTier,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_api_token)],
    summary="Create event tier"
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def create_event_tier(
    request: Request,
    tier: EventTierCreate
) -> Dict[str, Any]:
    """Create a new event tier (admin only)."""
    try:
        tier_data = tier.model_dump()
        tier_data["id"] = str(uuid4())
        tier_data["created_at"] = datetime.utcnow().isoformat()
        
        result = supabase.insert("event_tiers", tier_data)
        return result
    except Exception as e:
        logger.error(f"Error creating event tier: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create event tier"
        )

@router.put(
    "/tiers/{tier_id}",
    response_model=EventTier,
    dependencies=[Depends(require_admin_api_token)],
    summary="Update event tier"
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def update_event_tier(
    request: Request,
    tier_id: str,
    tier_update: EventTierUpdate
) -> Dict[str, Any]:
    """Update an event tier (admin only)."""
    try:
        update_data = {k: v for k, v in tier_update.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        result = supabase.update("event_tiers", tier_id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event tier not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating event tier {tier_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update event tier"
        )

# Event Queue Endpoints

@router.get(
    "/queue/",
    response_model=List[EventQueueItem],
    dependencies=[Depends(require_admin_api_token)],
    summary="List event queue items"
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def list_event_queue(
    request: Request,
    status_filter: Optional[str] = Query(None, description="Filter by status (queued, processing, done, error)", alias="status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    List event queue items (admin only).
    
    The event queue tracks player stats that need processing for achievements.
    """
    try:
        query = supabase.get_client().table("event_queue").select("*")
        
        if status_filter:
            query = query.eq("status", status_filter)
            
        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
        result = query.execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching event queue: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch event queue"
        )

@router.get(
    "/queue/{queue_id}",
    response_model=EventQueueItem,
    dependencies=[Depends(require_admin_api_token)],
    summary="Get event queue item by ID"
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def get_event_queue_item(
    request: Request,
    queue_id: int
) -> Dict[str, Any]:
    """Get a specific event queue item by ID (admin only)."""
    try:
        result = supabase.get_by_id("event_queue", queue_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event queue item not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching event queue item {queue_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch event queue item"
        )

@router.post(
    "/queue/{queue_id}/retry",
    dependencies=[Depends(require_admin_api_token)],
    summary="Retry failed queue item"
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def retry_event_queue_item(
    request: Request,
    queue_id: int
) -> Dict[str, Any]:
    """
    Retry a failed event queue item (admin only).
    
    Resets the status to 'queued' and clears the error message.
    """
    try:
        update_data = {
            "status": "queued",
            "last_error": None,
            "visible_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.update("event_queue", queue_id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event queue item not found"
            )
        
        return {"message": "Event queue item reset for retry", "queue_id": queue_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrying event queue item {queue_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retry event queue item"
        )

@router.get(
    "/team/{team_id}/results",
    response_model=List[EventResult],
    summary="Get team event results"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_team_event_results(
    request: Request,
    team_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get all event results for a specific team.
    
    Returns the team's placement and rewards from all events they've participated in.
    """
    try:
        query = supabase.get_client().table("event_results") \
            .select("*") \
            .eq("team_id", team_id) \
            .order("awarded_at", desc=True) \
            .range(offset, offset + limit - 1)
        
        result = query.execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching team event results for {team_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch team event results"
        )

