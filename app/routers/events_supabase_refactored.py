"""
Refactored Events Router for Supabase Backend

This module provides a clean, RESTful API for managing events with improved
performance, better error handling, and comprehensive documentation.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from fastapi import (
    APIRouter, Depends, HTTPException, status, 
    Query, Path, Body, Request
)
from pydantic import BaseModel, Field, validator

from app.core.supabase import supabase
from app.core.auth import get_current_user, get_current_admin_user, RoleChecker
from app.core.rate_limiter import limiter
from app.core.config import settings
from app.schemas.events import (
    EventStatus, EventType, EventTier,
    EventCreate, EventUpdate, EventSchema
)

import logging

# Initialize router with rate limiting
router = APIRouter(prefix="/events", tags=["Events"])

# Configure logging
logger = logging.getLogger(__name__)

# Constants
EVENT_ID_DESC = "The UUID of the event"
EVENT_ID_EXAMPLE = "123e4567-e89b-12d3-a456-426614174000"
UUID_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89abAB][0-9a-f]{3}-[0-9a-f]{12}$"

class EventResponse(EventSchema):
    """Extended event response with additional computed fields."""
    is_registration_open: bool = Field(
        False, 
        description="Whether registration is currently open for this event"
    )
    days_until_start: Optional[int] = Field(
        None,
        description="Number of days until the event starts (negative if in progress or completed)"
    )

class EventListResponse(BaseModel):
    """Paginated list of events with metadata."""
    items: List[EventResponse] = Field(..., description="List of events")
    total: int = Field(..., description="Total number of events matching the query")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    has_more: bool = Field(..., description="Whether there are more items available")

# Helper Functions

def get_event_by_id(event_id: str) -> Dict[str, Any]:
    """
    Retrieve an event by ID with proper error handling.
    
    Args:
        event_id: The UUID of the event to retrieve
        
    Returns:
        Dict[str, Any]: The event data
        
    Raises:
        HTTPException: If the event is not found or an error occurs
    """
    try:
        # Validate UUID format
        import re
        if not re.match(UUID_PATTERN, event_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID format"
            )
            
        # Fetch the event
        event = supabase.get_by_id("events", event_id)
        
        if not event:
            logger.warning(f"Event not found: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
            
        return event
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving event {event_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the event"
        )

# API Endpoints

@router.post(
    "/",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Event created successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        409: {"description": "Event with similar details already exists"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def create_event(
    request: Request,
    event: EventCreate,
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    Create a new event (Admin only).
    
    This endpoint allows administrators to create new events with the provided details.
    The event will be created with the current admin user as the creator.
    """
    try:
        logger.info(f"Creating new event: {event.name}")
        
        # Prepare event data
        event_data = event.dict()
        event_data["id"] = str(uuid4())
        event_data["created_by"] = current_user["id"]
        event_data["updated_by"] = current_user["id"]
        event_data["created_at"] = datetime.utcnow().isoformat()
        event_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Create the event
        result = supabase.insert("events", event_data)
        
        if not result:
            logger.error(f"Failed to create event: {event.name}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create event"
            )
            
        logger.info(f"Successfully created event: {result.get('id')}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating event: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the event"
        )

@router.get(
    "/",
    response_model=EventListResponse,
    responses={
        200: {"description": "List of events matching the criteria"},
        400: {"description": "Invalid query parameters"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_events(
    request: Request,
    status: Optional[EventStatus] = Query(
        None, 
        description="Filter events by status",
        examples={"upcoming": {"value": "upcoming"}, "completed": {"value": "completed"}}
    ),
    event_type: Optional[EventType] = Query(
        None,
        description="Filter events by type"
    ),
    tier: Optional[EventTier] = Query(
        None,
        description="Filter events by competitive tier"
    ),
    season_number: Optional[int] = Query(
        None,
        ge=1,
        description="Filter events by season number"
    ),
    is_global: Optional[bool] = Query(
        None,
        description="Filter for global events only"
    ),
    region_id: Optional[str] = Query(
        None,
        description="Filter events by region ID (takes precedence over is_global)",
        pattern=UUID_PATTERN
    ),
    start_date: Optional[datetime] = Query(
        None,
        description="Filter events starting on or after this date"
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="Filter events starting on or before this date"
    ),
    page: int = Query(
        1,
        ge=1,
        description="Page number for pagination"
    ),
    size: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of items per page"
    ),
    sort_by: str = Query(
        "start_date",
        description="Field to sort results by",
        pattern="^(start_date|end_date|name|created_at|updated_at)$"
    ),
    sort_order: str = Query(
        "asc",
        description="Sort order (asc or desc)",
        pattern="^(asc|desc)$"
    )
) -> Dict[str, Any]:
    """
    List events with filtering, sorting, and pagination.
    
    Returns a paginated list of events that match the specified criteria.
    """
    try:
        logger.info("Listing events with filters")
        
        # Build the query
        query = supabase.get_client().table("events").select("*")
        
        # Apply filters
        if status:
            query = query.eq("status", status.value)
        if event_type:
            query = query.eq("event_type", event_type.value)
        if tier:
            query = query.eq("tier", tier.value)
        if season_number:
            query = query.eq("season_number", season_number)
        if region_id:
            query = query.eq("region_id", region_id)
        elif is_global is not None:
            query = query.eq("is_global", is_global)
        if start_date:
            query = query.gte("start_date", start_date.isoformat())
        if end_date:
            query = query.lte("start_date", end_date.isoformat())
            
        # Apply sorting
        query = query.order(sort_by, desc=(sort_order.lower() == "desc"))
        
        # Apply pagination
        offset = (page - 1) * size
        query = query.range(offset, offset + size - 1)
        
        # Execute the query
        result = query.execute()
        
        # Get total count for pagination
        count_query = supabase.get_client().table("events").select("id", count="exact")
        count_result = count_query.execute()
        total = count_result.count if hasattr(count_result, 'count') else 0
        
        # Format the response
        return {
            "items": result.data if hasattr(result, 'data') else [],
            "total": total,
            "page": page,
            "size": size,
            "has_more": (offset + len(result.data if hasattr(result, 'data') else [])) < total if total else False
        }
        
    except Exception as e:
        logger.error(f"Error listing events: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving events"
        )

@router.get(
    "/{event_id}",
    response_model=EventResponse,
    responses={
        200: {"description": "Event details"},
        404: {"description": "Event not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_event(
    request: Request,
    event_id: str = Path(..., description=EVENT_ID_DESC, example=EVENT_ID_EXAMPLE, pattern=UUID_PATTERN),
    include_participants: bool = Query(
        False,
        description="Whether to include participant details in the response"
    )
) -> Dict[str, Any]:
    """
    Get event details by ID.
    
    Returns detailed information about a specific event, optionally including
    participant information.
    """
    try:
        # Get the event
        event = get_event_by_id(event_id)
        
        # Include participants if requested
        if include_participants:
            participants = supabase.get_client().table("event_participants") \
                .select("*")\
                .eq("event_id", event_id) \
                .execute()
            event["participants"] = participants.data if hasattr(participants, 'data') else []
        
        # Add computed fields
        now = datetime.utcnow()
        event_start = datetime.fromisoformat(event["start_date"])
        event["is_registration_open"] = (
            event.get("registration_deadline") and 
            datetime.fromisoformat(event["registration_deadline"]) > now and
            event_start > now
        )
        event["days_until_start"] = (event_start - now).days
        
        return event
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving event {event_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the event"
        )

@router.put(
    "/{event_id}",
    response_model=EventResponse,
    responses={
        200: {"description": "Event updated successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Event not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def update_event(
    request: Request,
    event_id: str,
    event_update: EventUpdate,
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    Update an existing event (Admin only).
    
    This endpoint allows administrators to update an existing event with new information.
    Only the fields provided in the request body will be updated.
    """
    try:
        logger.info(f"Updating event: {event_id}")
        
        # Check if the event exists
        existing_event = get_event_by_id(event_id)
        
        # Prepare update data
        update_data = event_update.dict(exclude_unset=True)
        update_data["updated_by"] = current_user["id"]
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Update the event
        result = supabase.update("events", event_id, update_data)
        
        if not result:
            logger.error(f"Failed to update event: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update event"
            )
            
        logger.info(f"Successfully updated event: {event_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating event {event_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the event"
        )

@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Event deleted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Event not found"},
        409: {"description": "Cannot delete event with participants"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def delete_event(
    request: Request,
    event_id: str,
    force: bool = Query(
        False,
        description="Force deletion even if the event has participants"
    ),
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
) -> None:
    """
    Delete an event (Admin only).
    
    By default, events with active participants cannot be deleted unless the 
    force parameter is set to True.
    """
    try:
        logger.info(f"Deleting event: {event_id} (force={force})")
        
        # Check if the event exists
        event = get_event_by_id(event_id)
        
        # Check for participants (unless force is True)
        if not force:
            participants = supabase.get_client().table("event_participants") \
                .select("id") \
                .eq("event_id", event_id) \
                .limit(1) \
                .execute()
                
            if hasattr(participants, 'data') and participants.data:
                logger.warning(
                    f"Cannot delete event {event_id}: Has {len(participants.data)} participants"
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "Cannot delete event with active participants. "
                        "Set force=true to delete anyway."
                    )
                )
        
        # Delete the event
        result = supabase.delete("events", event_id)
        
        if not result:
            logger.error(f"Failed to delete event: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete event"
            )
            
        logger.info(f"Successfully deleted event: {event_id}")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the event"
        )
