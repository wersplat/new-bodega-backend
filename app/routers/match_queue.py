"""
Match Queue Router

This module provides API endpoints for managing match queue sessions and slots.
Supports both individual player queues and team queues.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from pydantic import BaseModel, ConfigDict, Field

from app.core.supabase import supabase
from app.core.auth_supabase import require_admin_api_token, supabase_user_from_bearer
from app.core.rate_limiter import limiter
from app.core.config import settings

# Initialize router
router = APIRouter(
    prefix="/v1/match-queue",
    tags=["Match Queue"],
    responses={404: {"description": "Not found"}},
)

# Configure logging
logger = logging.getLogger(__name__)

# Pydantic Models

class MatchQueueSessionBase(BaseModel):
    """Base match queue session model"""
    guild_id: str = Field(..., description="Discord guild ID")
    channel_id: str = Field(..., description="Discord channel ID")
    message_id: Optional[str] = None
    required_positions: List[str] = Field(
        default=["Point Guard", "Shooting Guard", "Lock", "Power Forward", "Center"],
        description="Required positions for the match"
    )
    skill_range: Optional[float] = Field(None, ge=0, description="Allowed skill range")

class MatchQueueSessionCreate(MatchQueueSessionBase):
    """Create match queue session request"""
    pass

class MatchQueueSession(MatchQueueSessionBase):
    """Match queue session response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    status: str
    team_a_strength: Optional[float] = None
    team_b_strength: Optional[float] = None
    matched_at: Optional[str] = None
    cancelled_at: Optional[str] = None
    cancelled_by: Optional[str] = None
    created_at: str

class MatchQueueSlotBase(BaseModel):
    """Base match queue slot model"""
    discord_id: str = Field(..., description="Discord user ID")
    position: str = Field(..., description="Player position")
    player_id: Optional[str] = None

class MatchQueueSlotCreate(MatchQueueSlotBase):
    """Create match queue slot request"""
    pass

class MatchQueueSlot(MatchQueueSlotBase):
    """Match queue slot response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    session_id: str
    status: str
    assigned_team: Optional[str] = None
    joined_at: str
    left_at: Optional[str] = None

class TeamQueueSlotBase(BaseModel):
    """Base team queue slot model"""
    team_id: str = Field(..., description="Team UUID")
    captain_discord_id: str = Field(..., description="Captain's Discord ID")
    captain_player_id: Optional[str] = None
    selected_league_id: Optional[str] = None
    selected_season_id: Optional[str] = None
    roster_source: Optional[str] = Field(None, description="league or current")

class TeamQueueSlotCreate(TeamQueueSlotBase):
    """Create team queue slot request"""
    pass

class TeamQueueSlot(TeamQueueSlotBase):
    """Team queue slot response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    session_id: str
    status: str
    elo_snapshot: Optional[float] = None
    rp_snapshot: Optional[float] = None
    ready_at: Optional[str] = None
    left_at: Optional[str] = None
    created_at: str

# Player Match Queue Endpoints

@router.get(
    "/sessions/",
    response_model=List[MatchQueueSession],
    summary="List match queue sessions"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_queue_sessions(
    request: Request,
    guild_id: Optional[str] = Query(None, description="Filter by guild ID"),
    status_filter: Optional[str] = Query(None, description="Filter by status", alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    List match queue sessions with optional filtering.
    """
    try:
        query = supabase.get_client().table("match_queue_sessions").select("*")
        
        if guild_id:
            query = query.eq("guild_id", guild_id)
        if status_filter:
            query = query.eq("status", status_filter)
            
        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
        result = query.execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching queue sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch queue sessions"
        )

@router.get(
    "/sessions/{session_id}",
    response_model=MatchQueueSession,
    summary="Get queue session by ID"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_queue_session_by_id(
    request: Request,
    session_id: str
) -> Dict[str, Any]:
    """Get a specific queue session by ID."""
    try:
        result = supabase.get_by_id("match_queue_sessions", session_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Queue session not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching queue session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch queue session"
        )

@router.post(
    "/sessions/",
    response_model=MatchQueueSession,
    status_code=status.HTTP_201_CREATED,
    summary="Create queue session"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def create_queue_session(
    request: Request,
    session: MatchQueueSessionCreate
) -> Dict[str, Any]:
    """
    Create a new match queue session.
    
    This initiates a new matchmaking session in a Discord guild.
    """
    try:
        session_data = session.model_dump()
        session_data["id"] = str(uuid4())
        session_data["status"] = "active"
        session_data["created_at"] = datetime.utcnow().isoformat()
        
        result = supabase.insert("match_queue_sessions", session_data)
        return result
    except Exception as e:
        logger.error(f"Error creating queue session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create queue session"
        )

@router.post(
    "/sessions/{session_id}/cancel",
    dependencies=[Depends(require_admin_api_token)],
    summary="Cancel queue session"
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def cancel_queue_session(
    request: Request,
    session_id: str,
    current_user: Dict[str, Any] = Depends(supabase_user_from_bearer)
) -> Dict[str, Any]:
    """Cancel a queue session (admin only)."""
    try:
        user_id = current_user.get("sub") or current_user.get("user_id") or current_user.get("id")
        
        update_data = {
            "status": "cancelled",
            "cancelled_at": datetime.utcnow().isoformat(),
            "cancelled_by": str(user_id)
        }
        
        result = supabase.update("match_queue_sessions", session_id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Queue session not found"
            )
        
        return {"message": "Queue session cancelled", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling queue session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel queue session"
        )

# Queue Slots Endpoints

@router.get(
    "/sessions/{session_id}/slots",
    response_model=List[MatchQueueSlot],
    summary="List slots in session"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_session_slots(
    request: Request,
    session_id: str
) -> List[Dict[str, Any]]:
    """
    List all slots (players) in a queue session.
    """
    try:
        result = supabase.get_client().table("match_queue_slots") \
            .select("*") \
            .eq("session_id", session_id) \
            .order("joined_at") \
            .execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching session slots for {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch session slots"
        )

@router.post(
    "/sessions/{session_id}/join",
    response_model=MatchQueueSlot,
    status_code=status.HTTP_201_CREATED,
    summary="Join queue session"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def join_queue_session(
    request: Request,
    session_id: str,
    slot: MatchQueueSlotCreate
) -> Dict[str, Any]:
    """
    Join a queue session as a player.
    """
    try:
        # Verify session exists and is active
        session = supabase.get_by_id("match_queue_sessions", session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Queue session not found"
            )
        
        if session.get("status") != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Queue session is not active"
            )
        
        # Check if player already in session
        existing = supabase.get_client().table("match_queue_slots") \
            .select("id") \
            .eq("session_id", session_id) \
            .eq("discord_id", slot.discord_id) \
            .eq("status", "waiting") \
            .execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Player already in queue"
            )
        
        slot_data = slot.model_dump()
        slot_data["id"] = str(uuid4())
        slot_data["session_id"] = session_id
        slot_data["status"] = "waiting"
        slot_data["joined_at"] = datetime.utcnow().isoformat()
        
        result = supabase.insert("match_queue_slots", slot_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error joining queue session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join queue session"
        )

@router.post(
    "/sessions/{session_id}/leave",
    summary="Leave queue session"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def leave_queue_session(
    request: Request,
    session_id: str,
    discord_id: str = Query(..., description="Discord user ID")
) -> Dict[str, Any]:
    """
    Leave a queue session.
    """
    try:
        # Find the slot
        slot_result = supabase.get_client().table("match_queue_slots") \
            .select("*") \
            .eq("session_id", session_id) \
            .eq("discord_id", discord_id) \
            .eq("status", "waiting") \
            .execute()
        
        if not slot_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found in queue"
            )
        
        slot = slot_result.data[0]
        
        # Update slot status
        update_data = {
            "status": "left",
            "left_at": datetime.utcnow().isoformat()
        }
        
        supabase.update("match_queue_slots", slot["id"], update_data)
        
        return {"message": "Left queue successfully", "slot_id": slot["id"]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error leaving queue session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to leave queue session"
        )

# Team Queue Endpoints

@router.get(
    "/team/sessions/",
    response_model=List[Dict[str, Any]],
    summary="List team queue sessions"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_team_queue_sessions(
    request: Request,
    guild_id: Optional[str] = Query(None, description="Filter by guild ID"),
    status_filter: Optional[str] = Query(None, description="Filter by status", alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    List team queue sessions with optional filtering.
    """
    try:
        query = supabase.get_client().table("team_match_queue_sessions").select("*")
        
        if guild_id:
            query = query.eq("guild_id", guild_id)
        if status_filter:
            query = query.eq("status", status_filter)
            
        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
        result = query.execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching team queue sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch team queue sessions"
        )

@router.post(
    "/team/sessions/",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Create team queue session"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def create_team_queue_session(
    request: Request,
    guild_id: str = Query(..., description="Discord guild ID"),
    channel_id: str = Query(..., description="Discord channel ID")
) -> Dict[str, Any]:
    """
    Create a new team queue session.
    """
    try:
        session_data = {
            "id": str(uuid4()),
            "guild_id": guild_id,
            "channel_id": channel_id,
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.insert("team_match_queue_sessions", session_data)
        return result
    except Exception as e:
        logger.error(f"Error creating team queue session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create team queue session"
        )

@router.get(
    "/team/sessions/{session_id}/slots",
    response_model=List[TeamQueueSlot],
    summary="List team slots in session"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_team_session_slots(
    request: Request,
    session_id: str
) -> List[Dict[str, Any]]:
    """
    List all team slots in a queue session.
    """
    try:
        result = supabase.get_client().table("team_match_queue_slots") \
            .select("*") \
            .eq("session_id", session_id) \
            .order("created_at") \
            .execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching team session slots for {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch team session slots"
        )

@router.post(
    "/team/sessions/{session_id}/join",
    response_model=TeamQueueSlot,
    status_code=status.HTTP_201_CREATED,
    summary="Join team queue session"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def join_team_queue_session(
    request: Request,
    session_id: str,
    slot: TeamQueueSlotCreate
) -> Dict[str, Any]:
    """
    Join a team queue session.
    """
    try:
        # Verify session exists and is active
        session = supabase.get_by_id("team_match_queue_sessions", session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team queue session not found"
            )
        
        if session.get("status") != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team queue session is not active"
            )
        
        # Verify team exists
        team_result = supabase.get_client().table("teams").select("id, name, elo_rating, current_rp").eq("id", slot.team_id).execute()
        if not team_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        team = team_result.data[0]
        
        # Check if team already in session
        existing = supabase.get_client().table("team_match_queue_slots") \
            .select("id") \
            .eq("session_id", session_id) \
            .eq("team_id", slot.team_id) \
            .in_("status", ["waiting", "pending_lineup", "ready"]) \
            .execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team already in queue"
            )
        
        slot_data = slot.model_dump()
        slot_data["id"] = str(uuid4())
        slot_data["session_id"] = session_id
        slot_data["status"] = "waiting"
        slot_data["elo_snapshot"] = team.get("elo_rating")
        slot_data["rp_snapshot"] = team.get("current_rp")
        slot_data["created_at"] = datetime.utcnow().isoformat()
        
        result = supabase.insert("team_match_queue_slots", slot_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error joining team queue session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join team queue session"
        )

@router.get(
    "/team/sessions/{session_id}/slots/{slot_id}/lineup",
    response_model=List[Dict[str, Any]],
    summary="Get team lineup for queue slot"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_team_queue_lineup(
    request: Request,
    session_id: str,
    slot_id: str
) -> List[Dict[str, Any]]:
    """
    Get the lineup for a team queue slot.
    """
    try:
        result = supabase.get_client().table("team_match_queue_lineup_players") \
            .select("*") \
            .eq("slot_id", slot_id) \
            .execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching team lineup for slot {slot_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch team lineup"
        )

@router.get(
    "/active/",
    summary="Get active queues"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_active_queues(
    request: Request,
    guild_id: Optional[str] = Query(None, description="Filter by guild ID")
) -> Dict[str, Any]:
    """
    Get active player and team queues.
    """
    try:
        # Get active player queue sessions
        player_query = supabase.get_client().table("match_queue_sessions").select("*").eq("status", "active")
        if guild_id:
            player_query = player_query.eq("guild_id", guild_id)
        player_result = player_query.execute()
        
        # Get active team queue sessions
        team_query = supabase.get_client().table("team_match_queue_sessions").select("*").eq("status", "active")
        if guild_id:
            team_query = team_query.eq("guild_id", guild_id)
        team_result = team_query.execute()
        
        return {
            "player_queues": player_result.data if hasattr(player_result, 'data') else [],
            "team_queues": team_result.data if hasattr(team_result, 'data') else [],
            "total_active_sessions": (
                len(player_result.data if hasattr(player_result, 'data') else []) +
                len(team_result.data if hasattr(team_result, 'data') else [])
            )
        }
    except Exception as e:
        logger.error(f"Error fetching active queues: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch active queues"
        )

