"""
Events router for tournament and event management using Supabase
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.core.supabase import supabase
from app.core.auth import get_current_active_user, get_current_admin_user
from app.schemas.event import (
    EventCreate, Event as EventSchema, EventUpdate, 
    EventWithRegistrations, EventRegistration, EventStatus, EventType, EventTier
)
from app.schemas.player import Player as PlayerSchema

router = APIRouter()

def get_event_by_id(event_id: str) -> Optional[Dict[str, Any]]:
    """Helper function to get an event by ID from Supabase using optimized primary key lookup"""
    return supabase.fetch_by_id("events", event_id)

@router.post("/", response_model=EventSchema)
def create_event(
    event: EventCreate,
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
):
    """
    Create a new event (admin only)
    """
    event_data = event.model_dump()
    event_data["created_by"] = str(current_user.id)
    event_data["status"] = EventStatus.UPCOMING  # Default status
    
    created_event = supabase.insert("events", event_data)
    if not created_event:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create event"
        )
    return created_event

@router.get("/", response_model=List[EventSchema])
def list_events(
    status: Optional[EventStatus] = Query(
        None,
        description="Filter events by status",
        examples=["upcoming", "in_progress", "completed", "cancelled"]
    ),
    event_type: Optional[EventType] = Query(
        None,
        description="Filter events by type",
        examples=["League", "Tournament"]
    ),
    tier: Optional[EventTier] = Query(
        None,
        description="Filter events by tier",
        examples=["T1", "T2", "T3", "T4"]
    ),
    season_number: Optional[int] = Query(
        None,
        description="Filter events by season number",
        ge=1,
        example=1
    ),
    is_global: Optional[bool] = Query(
        None,
        description="Filter global events only"
    ),
    region_id: Optional[str] = Query(
        None,
        description="Filter events by region ID",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
):
    """
    List all events with optional filtering.
    
    Parameters:
    - **status**: Filter by event status (upcoming, in_progress, completed, cancelled)
    - **event_type**: Filter by event type (League, Tournament)
    - **tier**: Filter by event tier (T1, T2, T3, T4)
    - **season_number**: Filter by season number (1-based)
    - **is_global**: Filter global events only
    - **region_id**: Filter events by region UUID
    
    Returns:
        List of events matching the specified filters
    """
    client = supabase.get_client()
    query = client.table("events").select("*")
    
    if status:
        query = query.eq("status", status)
    if event_type:
        query = query.eq("event_type", event_type)
    if tier:
        query = query.eq("tier", tier)
    if season_number is not None:
        query = query.eq("season_number", season_number)
    if is_global is not None:
        query = query.eq("is_global", is_global)
    if region_id:
        query = query.eq("region_id", region_id)
        
    result = query.order("start_time", desc=True).execute()
    return result.data if hasattr(result, 'data') else []

@router.get(
    "/open", 
    response_model=List[EventSchema],
    summary="List open events",
    description="""
    List all open events (upcoming and in-progress) with optional filtering.
    
    This endpoint returns events that are either upcoming or in-progress.
    """
)
def list_open_events(
    event_type: Optional[EventType] = Query(
        None,
        description="Filter events by type",
        examples=["League", "Tournament"]
    ),
    tier: Optional[EventTier] = Query(
        None,
        description="Filter events by tier",
        examples=["T1", "T2", "T3", "T4"]
    )
):
    """
    List all open events (upcoming and in-progress) with optional filtering.
    
    Parameters:
    - **event_type**: Filter by event type (League, Tournament)
    - **tier**: Filter by event tier (T1, T2, T3, T4)
    
    Returns:
        List of open events matching the specified filters
    """
    client = supabase.get_client()
    query = client.table("events")\
        .select("*")\
        .in_("status", [EventStatus.UPCOMING, EventStatus.IN_PROGRESS])
        
    if event_type:
        query = query.eq("event_type", event_type)
    if tier:
        query = query.eq("tier", tier)
        
    result = query.order("start_time", desc=True).execute()
    return result.data if hasattr(result, 'data') else []

@router.get("/{event_id}", response_model=EventWithRegistrations)
def get_event(event_id: str):
    """
    Get event details with registrations using optimized primary key lookup
    """
    # Get event using optimized primary key lookup
    event = get_event_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Get registrations with player details in a single query
    client = supabase.get_client()
    registrations_result = client.table("event_registrations")\
        .select("*, player:players(*)")\
        .eq("event_id", event_id)\
        .execute()
    
    registrations = []
    if hasattr(registrations_result, 'data') and registrations_result.data:
        registrations = [
            EventRegistration(
                player=PlayerSchema(**reg["player"]),
                registered_at=reg["registered_at"]
            )
            for reg in registrations_result.data
        ]
    
    return EventWithRegistrations(
        **event,
        registrations=registrations
    )

@router.put("/{event_id}", response_model=EventSchema)
def update_event(
    event_id: str,
    event_update: EventUpdate,
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
):
    """
    Update event details (admin only)
    """
    # Check if event exists
    existing_event = get_event_by_id(event_id)
    if not existing_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Update event
    update_data = event_update.model_dump(exclude_unset=True)
    updated_event = supabase.update("events", event_id, update_data)
    
    if not updated_event:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update event"
        )
    return updated_event

@router.post("/{event_id}/register")
async def register_for_event(
    request: Request,
    event_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Register current user for an event
    """
    # Check if event exists and is open for registration
    event = get_event_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if event["status"] != EventStatus.UPCOMING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is not open for registration"
        )
    
    # Check if user already registered
    client = supabase.get_client()
    existing_registration = client.table("event_registrations")\
        .select("*")\
        .eq("event_id", event_id)\
        .eq("player_id", current_user.id)\
        .execute()
    
    if hasattr(existing_registration, 'data') and existing_registration.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already registered for this event"
        )
    
    # Create registration
    registration_data = {
        "event_id": event_id,
        "player_id": str(current_user.id),
        "registered_at": "now()"
    }
    
    result = client.table("event_registrations").insert(registration_data).execute()
    if not (hasattr(result, 'data') and result.data):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register for event"
        )
    
    # Get player details for response
    player = client.table("players").select("*").eq("user_id", str(current_user.id)).execute()
    player_data = player.data[0] if hasattr(player, 'data') and player.data else {}
    
    return {
        "event_id": event_id,
        "player": player_data,
        "registered_at": registration_data["registered_at"]
    }

@router.delete("/{event_id}/unregister", status_code=status.HTTP_204_NO_CONTENT)
def unregister_from_event(
    event_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Unregister current user from an event
    """
    client = supabase.get_client()
    
    # Find the registration
    result = client.table("event_registrations") \
        .select("id") \
        .eq("event_id", event_id) \
        .eq("player_id", str(current_user.id)) \
        .execute()
    
    if not hasattr(result, 'data') or not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )
    
    registration_id = result.data[0]['id']
    
    # Delete the registration
    try:
        supabase.delete("event_registrations", registration_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unregister from event: {str(e)}"
        )
