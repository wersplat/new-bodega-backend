"""
Events router for tournament and event management using Supabase
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.core.supabase import supabase
from app.core.auth import get_current_active_user, get_current_admin_user
from app.schemas.event import (
    EventCreate, Event as EventSchema, EventUpdate, 
    EventWithRegistrations, EventRegistration, EventStatus, EventType, EventTier
)

router = APIRouter()

async def get_event_by_id(event_id: str) -> Optional[Dict[str, Any]]:
    """Helper function to get an event by ID from Supabase"""
    return supabase.fetch_by_id("events", event_id)

@router.post("/", response_model=EventSchema)
async def create_event(
    event: EventCreate,
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
):
    """
    Create a new event (admin only)
    """
    event_data = event.model_dump()
    event_data["created_by"] = str(current_user.id)
    event_data["status"] = EventStatus.UPCOMING  # Default status
    
    try:
        created_event = supabase.insert("events", event_data)
        return created_event
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create event: {str(e)}"
        )

@router.get("/", response_model=List[EventSchema])
async def list_events(
    status: Optional[EventStatus] = None,
    event_type: Optional[EventType] = None
):
    """
    List all events with optional filtering
    """
    client = supabase.get_client()
    query = client.table("events").select("*")
    
    if status:
        query = query.eq("status", status.value)
    if event_type:
        query = query.eq("type", event_type.value)
    
    result = query.execute()
    return result.data if hasattr(result, 'data') else []

@router.get("/open", response_model=List[EventSchema])
async def list_open_events():
    """
    List all open events (upcoming and in-progress)
    """
    client = supabase.get_client()
    result = client.table("events") \
        .select("*") \
        .in_("status", [EventStatus.UPCOMING, EventStatus.IN_PROGRESS]) \
        .execute()
    
    return result.data if hasattr(result, 'data') else []

@router.get("/{event_id}", response_model=EventWithRegistrations)
async def get_event(event_id: str):
    """
    Get event details with registrations
    """
    client = supabase.get_client()
    
    # Get event
    event = await get_event_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Get registrations for this event
    try:
        result = client.table("event_registrations") \
            .select("*") \
            .eq("event_id", event_id) \
            .execute()
        registrations = result.data if hasattr(result, 'data') else []
    except Exception as e:
        # If the table doesn't exist or there's an error, return empty registrations
        registrations = []
    
    return EventWithRegistrations(**event, registrations=registrations)

@router.put("/{event_id}", response_model=EventSchema)
async def update_event(
    event_id: str,
    event_update: EventUpdate,
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
):
    """
    Update event details (admin only)
    """
    # Check if event exists
    event = await get_event_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Update only the fields that were provided
    update_data = event_update.model_dump(exclude_unset=True)
    
    try:
        updated_event = supabase.update("events", event_id, update_data)
        return updated_event
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update event: {str(e)}"
        )

@router.post("/{event_id}/register", response_model=EventRegistration)
async def register_for_event(
    event_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Register current user for an event
    """
    client = supabase.get_client()
    
    # Check if event exists and is open for registration
    event = await get_event_by_id(event_id)
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
    result = client.table("event_registrations") \
        .select("*") \
        .eq("event_id", event_id) \
        .eq("player_id", str(current_user.id)) \
        .execute()
    
    if hasattr(result, 'data') and result.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already registered for this event"
        )
    
    # Create registration
    registration_data = {
        "event_id": event_id,
        "player_id": str(current_user.id),
        "registration_date": "now()",  # Let the database set the current timestamp
        "payment_status": "pending",
        "is_confirmed": False
    }
    
    try:
        created_registration = supabase.insert("event_registrations", registration_data)
        return created_registration
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register for event: {str(e)}"
        )

@router.delete("/{event_id}/unregister", status_code=status.HTTP_204_NO_CONTENT)
async def unregister_from_event(
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
