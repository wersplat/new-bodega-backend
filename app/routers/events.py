"""
Events Router (Refactored)

This module provides a RESTful API for managing events with improved
performance, better error handling, and comprehensive documentation.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Request, status
from pydantic import BaseModel, Field, HttpUrl, model_validator

from app.core.auth_supabase import require_admin_api_token
from app.core.config import settings
from app.core.rate_limiter import limiter
from app.core.supabase import supabase

# Initialize router with rate limiting and explicit prefix
router = APIRouter(
    prefix="/v1/events",
    tags=["Events"],
    responses={404: {"description": "Not found"}},
)

# Configure logging
logger = logging.getLogger(__name__)

# Constants
UUID_PATTERN = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
UUID_EXAMPLE = "123e4567-e89b-12d3-a456-426614174000"

from enum import Enum
from pydantic import ConfigDict

# Enums (moved from schemas for better cohesion)
class StringEnum(str, Enum):
    """Base class for string enums that works with Python 3.9+"""
    def __str__(self) -> str:
        return str(self.value)
    
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)

class EventStatus(StringEnum):
    UPCOMING = "upcoming"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class EventType(StringEnum):
    LEAGUE = "League"
    TOURNAMENT = "Tournament"

class EventTier(StringEnum):
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"

# Models
class EventBase(BaseModel):
    """Base event model with common fields."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Summer Championship 2023",
                "description": "Annual summer gaming championship",
                "event_type": "TOURNAMENT",
                "tier": "T1",
                "start_date": "2023-07-15T15:00:00Z",
                "end_date": "2023-07-18T22:00:00Z",
                "status": "UPCOMING"
            }
        }
    )
    
    # Custom JSON serialization for enums
    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        # Convert enums to their values for JSON serialization
        for field, value in data.items():
            if isinstance(value, (EventStatus, EventType, EventTier)):
                data[field] = value.value
        return data
    
    name: str = Field(..., min_length=3, max_length=200, description="Event name")
    description: Optional[str] = Field(None, description="Event description")
    event_type: EventType = Field(..., description="Type of event (League/Tournament)")
    tier: EventTier = Field(..., description="Competitive tier of the event")
    start_date: datetime = Field(..., description="When the event starts")
    end_date: datetime = Field(..., description="When the event ends")
    registration_deadline: Optional[datetime] = Field(
        None, 
        description="Deadline for registration"
    )
    max_participants: Optional[int] = Field(
        None, 
        ge=2, 
        description="Maximum number of participants (if applicable)"
    )
    is_global: bool = Field(
        False, 
        description="Whether this is a global event (not region-specific)"
    )
    region_id: Optional[str] = Field(
        None,
        description="Region ID for regional events",
        pattern=UUID_PATTERN,
        examples=[UUID_EXAMPLE]
    )
    season_number: int = Field(1, ge=1, description="Season number for the event")
    status: EventStatus = Field(EventStatus.UPCOMING, description="Current event status")
    rules_url: Optional[HttpUrl] = Field(None, description="URL to event rules")
    banner_url: Optional[HttpUrl] = Field(None, description="URL to event banner image")
    prize_pool: Optional[float] = Field(None, ge=0, description="Total prize pool in USD")
    registration_fee: Optional[float] = Field(None, ge=0, description="Registration fee in USD")

    @model_validator(mode='after')
    def validate_dates(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValueError('end_date must be after start_date')
        return self

    @model_validator(mode='after')
    def validate_registration_deadline(self):
        if self.registration_deadline and self.start_date and self.registration_deadline > self.start_date:
            raise ValueError('registration_deadline must be before start_date')
        return self

class EventCreate(EventBase):
    """Model for creating a new event."""
    pass

class EventUpdate(BaseModel):
    """Model for updating an existing event."""
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    event_type: Optional[EventType] = None
    tier: Optional[EventTier] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None
    max_participants: Optional[int] = Field(None, ge=2)
    is_global: Optional[bool] = None
    region_id: Optional[str] = Field(None, pattern=UUID_PATTERN, examples=[UUID_EXAMPLE])
    season_number: Optional[int] = Field(None, ge=1)
    status: Optional[EventStatus] = None
    rules_url: Optional[HttpUrl] = None
    banner_url: Optional[HttpUrl] = None
    prize_pool: Optional[float] = Field(None, ge=0)
    registration_fee: Optional[float] = Field(None, ge=0)

class EventResponse(EventBase):
    """Complete event model for API responses."""
    id: str = Field(..., description="Unique identifier for the event")
    created_at: datetime = Field(..., description="When the event was created")
    updated_at: datetime = Field(..., description="When the event was last updated")
    created_by: Optional[str] = Field(None, description="ID of the user who created the event")
    
    model_config = ConfigDict(
        from_attributes=True,  # Replaces orm_mode=True
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Summer Championship 2023",
                "created_at": "2023-06-01T10:00:00Z",
                "updated_at": "2023-06-01T10:00:00Z",
                "created_by": "110e8400-e29b-41d4-a716-446655440000"
            }
        }
    )
    
    # Custom JSON serialization for datetime fields
    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        # Convert datetime fields to ISO format
        for field in ["created_at", "updated_at"]:
            if field in data and data[field] is not None:
                data[field] = data[field].isoformat()
        return data

class EventListResponse(BaseModel):
    """Paginated list of events with metadata."""
    items: List[EventResponse] = Field(..., description="List of events")
    total: int = Field(..., description="Total number of events matching the query")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    has_more: bool = Field(..., description="Whether there are more items available")

# Helper Functions
async def get_event_by_id(event_id: str) -> Optional[Dict[str, Any]]:
    """
    Helper function to get an event by ID with proper error handling.
    
    Args:
        event_id: The UUID of the event to retrieve
        
    Returns:
        Optional[Dict[str, Any]]: The event data if found, None otherwise
        
    Raises:
        HTTPException: If there's an error retrieving the event
    """
    try:
        if not event_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event ID is required"
            )
            
        result = supabase.get_by_id("events", event_id)
        return result
        
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
        400: {"description": "Invalid input data or validation error"},
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
    _: None = Depends(require_admin_api_token)
) -> Dict[str, Any]:
    """
    Create a new event (Admin only).
    
    This endpoint allows administrators to create new events with all necessary details.
    """
    try:
        # Check for existing event with same name and dates
        client = supabase.get_client()
        existing_event = client.table("events")\
            .select("*")\
            .ilike("name", event.name)\
            .eq("start_date", event.start_date.isoformat())\
            .execute()
        
        if existing_event and hasattr(existing_event, 'data') and existing_event.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An event with this name and start date already exists"
            )
        
        # Prepare event data
        event_data = event.dict(exclude_unset=True)
        event_data["created_by"] = "admin_api"
        
        # Create event
        created_event = supabase.insert("events", event_data)
        
        return created_event
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating event: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the event"
        )

@router.get(
    "/{event_id}",
    response_model=EventResponse,
    responses={
        200: {"description": "Event details retrieved successfully"},
        404: {"description": "Event not found"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_event(
    request: Request,
    event_id: str = Path(..., 
                        description="The UUID of the event to retrieve",
                        examples=[UUID_EXAMPLE], 
                        pattern=UUID_PATTERN),
    include_participants: bool = Query(
        False,
        description="Whether to include participant details in the response"
    )
) -> Dict[str, Any]:
    """
    Get event details by ID.
    
    This endpoint retrieves detailed information about a specific event,
    including its participants if requested.
    """
    try:
        event = await get_event_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        if include_participants:
            # Get event participants
            client = supabase.get_client()
            participants = client.table("event_participants")\
                .select("*, players(*)")\
                .eq("event_id", event_id)\
                .execute()
            
            event["participants"] = participants.data if hasattr(participants, 'data') else []
        
        return event
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving event {event_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the event"
        )

@router.get(
    "/",
    response_model=EventListResponse,
    responses={
        200: {"description": "List of events retrieved successfully"},
        400: {"description": "Invalid query parameters"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_events(
    request: Request,
    name: Optional[str] = Query(
        None,
        description="Filter events by name (case-insensitive contains)",
        min_length=1,
        max_length=100
    ),
    event_type: Optional[EventType] = Query(
        None,
        description="Filter events by type"
    ),
    tier: Optional[EventTier] = Query(
        None,
        description="Filter events by competitive tier"
    ),
    status: Optional[EventStatus] = Query(
        None,
        description="Filter events by status"
    ),
    is_global: Optional[bool] = Query(
        None,
        description="Filter for global/regional events"
    ),
    region_id: Optional[str] = Query(
        None,
        description="Filter events by region ID",
        pattern=UUID_PATTERN,
        examples=[UUID_EXAMPLE]
    ),
    season_number: Optional[int] = Query(
        None,
        ge=1,
        description="Filter events by season number"
    ),
    start_date_after: Optional[datetime] = Query(
        None,
        description="Filter events starting on or after this date"
    ),
    start_date_before: Optional[datetime] = Query(
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
    List events with optional filtering and pagination.
    
    This endpoint returns a paginated list of events that match the specified filters.
    """
    try:
        offset = (page - 1) * size
        limit = size
        
        # Build query
        client = supabase.get_client()
        query = client.table("events").select("*", count="exact")
        
        # Apply filters
        if name:
            query = query.ilike("name", f"%{name}%")
        if event_type:
            query = query.eq("event_type", event_type)
        if tier:
            query = query.eq("tier", tier)
        if status:
            query = query.eq("status", status)
        if is_global is not None:
            query = query.eq("is_global", is_global)
        if region_id:
            query = query.eq("region_id", region_id)
        if season_number:
            query = query.eq("season_number", season_number)
        if start_date_after:
            query = query.gte("start_date", start_date_after.isoformat())
        if start_date_before:
            query = query.lte("start_date", start_date_before.isoformat())
        
        # Apply sorting
        sort_field = sort_by if sort_by in ["start_date", "end_date", "name", "created_at", "updated_at"] else "start_date"
        sort_order_str = sort_order.lower() if sort_order.lower() in ["asc", "desc"] else "asc"
        
        # Get total count
        count_result = query.execute()
        total = count_result.count if hasattr(count_result, 'count') else 0
        
        # Apply pagination and sorting
        query = query.range(offset, offset + limit - 1)
        query = query.order(sort_field, desc=(sort_order_str == "desc"))
        
        # Execute query
        result = query.execute()
        items = result.data if hasattr(result, 'data') else []
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "has_more": (offset + len(items)) < total
        }
        
    except Exception as e:
        logger.error(f"Error listing events: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving events"
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
        409: {"description": "Event with similar details already exists"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def update_event(
    request: Request,
    event_id: str = Path(..., 
                        description="The UUID of the event to update",
                        examples=[UUID_EXAMPLE], 
                        pattern=UUID_PATTERN),
    event_update: EventUpdate = Body(..., description="Event data to update"),
    _: None = Depends(require_admin_api_token)
) -> Dict[str, Any]:
    """
    Update an existing event (Admin only).
    
    This endpoint allows administrators to update event details.
    Only the fields provided in the request will be updated.
    """
    try:
        # Check if event exists
        existing_event = await get_event_by_id(event_id)
        if not existing_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        # Check for name/date conflict if name or dates are being updated
        if event_update.name or event_update.start_date:
            client = supabase.get_client()
            query = client.table("events")\
                .select("*")\
                .neq("id", event_id)
                
            if event_update.name:
                query = query.ilike("name", event_update.name)
            else:
                query = query.ilike("name", existing_event["name"])
                
            if event_update.start_date:
                query = query.eq("start_date", event_update.start_date.isoformat())
            else:
                query = query.eq("start_date", existing_event["start_date"])
            
            conflict_check = query.execute()
            
            if conflict_check and hasattr(conflict_check, 'data') and conflict_check.data:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An event with this name and start date already exists"
                )
        
        # Prepare update data
        update_data = event_update.dict(exclude_unset=True)
        
        # Only update if there are changes
        if not update_data:
            return existing_event
        
        # Update event
        updated_event = supabase.update("events", event_id, update_data)
        
        return updated_event
        
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
        400: {"description": "Cannot delete event with participants"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Event not found"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def delete_event(
    request: Request,
    event_id: str = Path(..., 
                        description="The UUID of the event to delete",
                        examples=[UUID_EXAMPLE], 
                        pattern=UUID_PATTERN),
    force: bool = Query(
        False,
        description="Force deletion even if the event has participants (use with caution)"
    ),
    _: None = Depends(require_admin_api_token)
) -> None:
    """
    Delete an event (Admin only).
    
    This endpoint allows administrators to delete an event.
    By default, events with participants cannot be deleted unless force=True.
    """
    try:
        # Check if event exists
        event = await get_event_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        # Check for participants if not forcing deletion
        if not force:
            client = supabase.get_client()
            participants = client.table("event_participants")\
                .select("*", count="exact")\
                .eq("event_id", event_id)\
                .execute()
            
            participant_count = participants.count if hasattr(participants, 'count') else 0
            
            if participant_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Cannot delete event with {participant_count} participants. "
                        "Set force=true to delete anyway."
                    )
                )
        
        # Delete event
        supabase.delete("events", event_id)
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the event"
        )
