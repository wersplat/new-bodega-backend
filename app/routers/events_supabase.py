"""
Events Router for Supabase Backend

This module provides API endpoints for managing events in the Bodega backend.
It handles event creation, retrieval, updating, and deletion, along with
related operations like event registration and participant management.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from pydantic import BaseModel, Field

from app.core.auth import get_current_user, get_current_admin_user
from app.core.supabase import supabase
from app.schemas.events import EventCreate, EventSchema, EventStatus, EventType, EventTier
from app.core.config import settings
from app.core.rate_limiter import limiter

import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/events", tags=["events"])

# Constants for API documentation
REGION_ID_EXAMPLE = "123e4567-e89b-12d3-a456-426614174000"
REGION_ID_REGEX = "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"

# Helper function to get event by ID
async def get_event_by_id(event_id: str) -> Dict[str, Any]:
    """
    Helper function to retrieve an event by ID with proper error handling.
    
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
        if not re.match(REGION_ID_REGEX, event_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID format"
            )
            
        # Fetch the event
        event = supabase.get_by_id("events", event_id)
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
            
        return event
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving event {event_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the event"
        )

@router.post(
    "/",
    response_model=EventSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Event created successfully"},
        400: {"description": "Invalid event data or validation error"},
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
    Create a new event (admin only).
    
    This endpoint allows administrators to create new events with the provided details.
    The event will be created with a default status of 'UPCOMING' and the current
    admin user will be recorded as the creator.
    
    Args:
        request: The incoming request object (for rate limiting)
        event: The event data to create
        current_user: The authenticated admin user creating the event
        
    Returns:
        Dict[str, Any]: The created event data
        
    Raises:
        HTTPException: If there's an error creating the event or if the user is not authorized
    """
    try:
        logger.info(f"Creating new event: {event.name}")
        
        # Prepare event data
        event_data = event.dict()
        event_data["created_by"] = str(current_user.id)
        event_data["created_at"] = datetime.utcnow().isoformat()
        event_data["status"] = EventStatus.UPCOMING.value  # Default status
        
        # Check for duplicate events (same name and start date)
        existing_events = supabase.get_client().table("events") \
            .select("id") \
            .eq("name", event.name) \
            .eq("start_date", event.start_date.isoformat()) \
            .execute()
            
        if hasattr(existing_events, 'data') and existing_events.data:
            logger.warning(f"Event with name '{event.name}' on {event.start_date} already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An event with this name and start date already exists"
            )
        
        # Create the event
        created_event = supabase.insert("events", event_data)
        
        if not created_event:
            logger.error("Failed to create event in database")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create event"
            )
            
        logger.info(f"Successfully created event: {created_event.get('id')}")
        return created_event
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error creating event: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the event"
        )

@router.get(
    "/",
    response_model=List[EventSchema],
    responses={
        200: {"description": "List of events matching the specified filters"},
        400: {"description": "Invalid query parameters"},
        404: {"description": "No events found matching the criteria"},
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
        examples={
            "upcoming": {"value": "upcoming"},
            "in_progress": {"value": "in_progress"},
            "completed": {"value": "completed"},
            "cancelled": {"value": "cancelled"}
        },
        openapi_examples={
            "upcoming": {"summary": "Upcoming events", "value": "upcoming"},
            "in_progress": {"summary": "Events in progress", "value": "in_progress"},
            "completed": {"summary": "Completed events", "value": "completed"},
            "cancelled": {"summary": "Cancelled events", "value": "cancelled"}
        }
    ),
    event_type: Optional[EventType] = Query(
        None,
        description="Filter events by type",
        examples={"league": {"value": "League"}, "tournament": {"value": "Tournament"}},
        openapi_examples={
            "league": {"summary": "League events", "value": "League"},
            "tournament": {"summary": "Tournament events", "value": "Tournament"}
        }
    ),
    tier: Optional[EventTier] = Query(
        None,
        description="Filter events by competitive tier (T1-T4)",
        examples={"t1": {"value": "T1"}, "t2": {"value": "T2"}},
        openapi_examples={
            "t1": {"summary": "Tier 1 events", "value": "T1"},
            "t2": {"summary": "Tier 2 events", "value": "T2"},
            "t3": {"summary": "Tier 3 events", "value": "T3"},
            "t4": {"summary": "Tier 4 events", "value": "T4"}
        }
    ),
    season_number: Optional[int] = Query(
        None,
        description="Filter events by season number (1-based index)",
        ge=1,
        example=1,
        openapi_examples={
            "season1": {"summary": "Season 1", "value": 1},
            "season2": {"summary": "Season 2", "value": 2}
        }
    ),
    is_global: Optional[bool] = Query(
        None,
        description="Filter for global events only. If not specified, returns both global and regional events.",
        example=True,
        openapi_examples={
            "global": {"summary": "Global events only", "value": True},
            "regional": {"summary": "Regional events only", "value": False}
        }
    ),
    region_id: Optional[str] = Query(
        None,
        description=f"Filter events by specific region UUID. Takes precedence over is_global.",
        example=REGION_ID_EXAMPLE,
        pattern=REGION_ID_REGEX,
        openapi_examples={
            "na": {"summary": "North America region", "value": REGION_ID_EXAMPLE},
            "eu": {"summary": "Europe region", "value": "87654321-4321-8765-4321-876543210987"}
        }
    ),
    start_date: Optional[datetime] = Query(
        None,
        description="Filter events starting on or after this date (ISO 8601 format)",
        example="2023-01-01T00:00:00Z"
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="Filter events starting on or before this date (ISO 8601 format)",
        example="2023-12-31T23:59:59Z"
    ),
    limit: int = Query(
        50,
        description="Maximum number of events to return (1-1000)",
        ge=1,
        le=1000
    ),
    offset: int = Query(
        0,
        description="Number of events to skip for pagination",
        ge=0
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
) -> List[Dict[str, Any]]:
    """
    List events with optional filtering and pagination.
    
    This endpoint returns a paginated list of events that match the specified filters.
    It supports filtering by status, type, tier, season, region, and date ranges.
    
    Args:
        request: The incoming request object (for rate limiting)
        status: Filter events by status (upcoming, in_progress, completed, cancelled)
        event_type: Filter events by type (League, Tournament)
        tier: Filter events by competitive tier (T1-T4)
        season_number: Filter events by season number
        is_global: Filter for global events only
        region_id: Filter events by specific region UUID (takes precedence over is_global)
        start_date: Filter events starting on or after this date
        end_date: Filter events starting on or before this date
        limit: Maximum number of events to return (1-1000)
        offset: Number of events to skip for pagination
        sort_by: Field to sort results by
        sort_order: Sort order (asc or desc)
        
    Returns:
        List[Dict[str, Any]]: List of event objects matching the criteria
        
    Raises:
        HTTPException: If there's an error retrieving events or invalid parameters
    """
    try:
        logger.info(
            f"Listing events with filters: status={status}, type={event_type}, "
            f"tier={tier}, season={season_number}, is_global={is_global}, "
            f"region_id={region_id}"
        )
        
        # Build the base query
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
        query = query.range(offset, offset + limit - 1)
        
        # Execute the query
        result = query.execute()
        events = result.data if hasattr(result, 'data') else []
        
        if not events:
            logger.info("No events found matching the criteria")
            
        logger.info(f"Found {len(events)} events matching the criteria")
        return events
        
    except Exception as e:
        logger.error(
            f"Error listing events: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving events"
        )

@router.get(
    "/{event_id}",
    response_model=EventSchema,
    responses={
        200: {"description": "Event details retrieved successfully"},
        400: {"description": "Invalid event ID format"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Event not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_event(
    request: Request,
    event_id: str = Query(
        ...,
        description="The UUID of the event to retrieve",
        example=REGION_ID_EXAMPLE,
        pattern=REGION_ID_REGEX,
        openapi_examples={
            "example1": {"summary": "Sample event ID 1", "value": "123e4567-e89b-12d3-a456-426614174000"},
            "example2": {"summary": "Sample event ID 2", "value": "87654321-4321-8765-4321-876543210987"}
        }
    ),
    include_participants: bool = Query(
        False,
        description="Whether to include participant details in the response"
    ),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get event details by ID.
    
    This endpoint retrieves detailed information about a specific event, including
    its status, schedule, and other metadata. Optionally, it can also include
    information about event participants.
    
    Args:
        request: The incoming request object (for rate limiting)
        event_id: The UUID of the event to retrieve
        include_participants: Whether to include participant details
        current_user: The currently authenticated user
        
    Returns:
        Dict[str, Any]: The event details, optionally including participants
        
    Raises:
        HTTPException: If the event is not found or an error occurs
    """
    try:
        logger.info(f"Retrieving event with ID: {event_id}")
        
        # Get the event
        event = await get_event_by_id(event_id)
        
        if not event:
            logger.warning(f"Event not found: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
            
        # If participants are requested, fetch them
        if include_participants:
            logger.debug(f"Fetching participants for event: {event_id}")
            try:
                participants = supabase.get_client().table("event_participants") \
                    .select("*, user_profiles!inner(*)") \
                    .eq("event_id", event_id) \
                    .execute()
                
                if hasattr(participants, 'data'):
                    event["participants"] = participants.data
                else:
                    event["participants"] = []
                    
            except Exception as e:
                logger.error(
                    f"Error fetching participants for event {event_id}: {str(e)}",
                    exc_info=True
                )
                event["participants"] = []
                
        logger.info(f"Successfully retrieved event: {event_id}")
        return event
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving event {event_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the event"
        )

@router.put(
    "/{event_id}",
    response_model=EventSchema,
    responses={
        200: {"description": "Event updated successfully"},
        400: {"description": "Invalid event data or validation error"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Event not found"},
        409: {"description": "Event with similar details already exists"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def update_event(
    request: Request,
    event_id: str,
    event_update: EventCreate,
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    Update an existing event (admin only).
    
    This endpoint allows administrators to update an existing event with new information.
    Only the fields provided in the request body will be updated; all other fields
    will remain unchanged.
    
    Args:
        request: The incoming request object (for rate limiting)
        event_id: The UUID of the event to update
        event_update: The updated event data
        current_user: The authenticated admin user making the update
        
    Returns:
        Dict[str, Any]: The updated event data
        
    Raises:
        HTTPException: If the event is not found, the user is not authorized,
                      or an error occurs during the update
    """
    try:
        logger.info(f"Updating event with ID: {event_id}")
        
        # Check if the event exists
        existing_event = await get_event_by_id(event_id)
        if not existing_event:
            logger.warning(f"Event not found for update: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
            
        # Check for duplicate events (same name and start date)
        if event_update.name != existing_event.get('name') or \
           event_update.start_date.isoformat() != existing_event.get('start_date'):
            existing_events = supabase.get_client().table("events") \
                .select("id") \
                .eq("name", event_update.name) \
                .eq("start_date", event_update.start_date.isoformat()) \
                .neq("id", event_id) \
                .execute()
                
            if hasattr(existing_events, 'data') and existing_events.data:
                logger.warning(
                    f"Event with name '{event_update.name}' on {event_update.start_date} "
                    f"already exists (conflict with update for {event_id})"
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An event with this name and start date already exists"
                )
        
        # Prepare update data
        update_data = event_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow().isoformat()
        update_data["updated_by"] = str(current_user.id)
        
        # Update the event
        updated_event = supabase.update("events", event_id, update_data)
        
        if not updated_event:
            logger.error(f"Failed to update event in database: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update event"
            )
            
        logger.info(f"Successfully updated event: {event_id}")
        return updated_event
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error updating event {event_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the event"
        )

@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Event deleted successfully"},
        400: {"description": "Invalid event ID format"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Event not found"},
        409: {"description": "Event cannot be deleted (e.g., has active participants)"},
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
        description="Force deletion even if the event has participants (use with caution)"
    ),
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
) -> None:
    """
    Delete an event (admin only).
    
    This endpoint allows administrators to delete an event. By default, events with
    active participants cannot be deleted unless the force parameter is set to True.
    
    Args:
        request: The incoming request object (for rate limiting)
        event_id: The UUID of the event to delete
        force: If True, will delete the event even if it has participants
        current_user: The authenticated admin user performing the deletion
        
    Raises:
        HTTPException: If the event is not found, has participants (and force=False),
                      or an error occurs during deletion
    """
    try:
        logger.info(f"Deleting event with ID: {event_id} (force={force})")
        
        # Check if the event exists
        event = await get_event_by_id(event_id)
        if not event:
            logger.warning(f"Event not found for deletion: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
            
        # Check if the event has participants (unless force is True)
        if not force:
            participants = supabase.get_client().table("event_participants") \
                .select("id") \
                .eq("event_id", event_id) \
                .limit(1) \
                .execute()
                
            if hasattr(participants, 'data') and participants.data:
                logger.warning(
                    f"Cannot delete event {event_id}: Event has active participants "
                    f"(count: {len(participants.data)}). Use force=true to override."
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
            logger.error(f"Failed to delete event from database: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete event"
            )
            
        logger.info(f"Successfully deleted event: {event_id}")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error deleting event {event_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the event"
        )

# Add more endpoints here following the same pattern as above
