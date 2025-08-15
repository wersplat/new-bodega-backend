"""
Tournaments Router (Refactored)

This module provides a RESTful API for managing tournaments with improved
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
    tags=["Tournaments"],
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

class TournamentStatus(StringEnum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in progress"
    COMPLETED = "completed"
    UNDER_REVIEW = "under review"
    REVIEWED = "reviewed"
    APPROVED = "approved"

class EventTier(StringEnum):
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"

# Models
class TournamentBase(BaseModel):
    """Base tournament model with common fields."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Summer Championship 2023",
                "description": "Annual summer gaming championship",
                "tier": "T1",
                "start_date": "2023-07-15T15:00:00Z",
                "end_date": "2023-07-18T22:00:00Z",
                "status": "scheduled"
            }
        }
    )
    
    # Custom JSON serialization for enums
    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        # Convert enums to their values for JSON serialization
        for field, value in data.items():
            if isinstance(value, (TournamentStatus, EventTier)):
                data[field] = value.value
        return data
    
    name: str = Field(..., min_length=3, max_length=200, description="Tournament name")
    description: Optional[str] = Field(None, description="Tournament description")
    tier: EventTier = Field(..., description="Competitive tier of the tournament")
    start_date: datetime = Field(..., description="When the tournament starts")
    end_date: datetime = Field(..., description="When the tournament ends")
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
        description="Whether this is a global tournament (not region-specific)"
    )
    regions_id: Optional[str] = Field(
        None,
        description="Region ID for regional tournaments",
        pattern=UUID_PATTERN,
        examples=[UUID_EXAMPLE]
    )
    season_number: int = Field(1, ge=1, description="Season number for the tournament")
    status: TournamentStatus = Field(TournamentStatus.SCHEDULED, description="Current tournament status")
    rules_url: Optional[HttpUrl] = Field(None, description="URL to tournament rules")
    banner_url: Optional[HttpUrl] = Field(None, description="URL to tournament banner image")
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

class TournamentCreate(TournamentBase):
    """Model for creating a new tournament."""
    pass

class TournamentUpdate(BaseModel):
    """Model for updating an existing tournament."""
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    tier: Optional[EventTier] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None
    max_participants: Optional[int] = Field(None, ge=2)
    is_global: Optional[bool] = None
    regions_id: Optional[str] = Field(None, pattern=UUID_PATTERN, examples=[UUID_EXAMPLE])
    season_number: Optional[int] = Field(None, ge=1)
    status: Optional[TournamentStatus] = None
    rules_url: Optional[HttpUrl] = None
    banner_url: Optional[HttpUrl] = None
    prize_pool: Optional[float] = Field(None, ge=0)
    registration_fee: Optional[float] = Field(None, ge=0)

class TournamentResponse(TournamentBase):
    """Complete tournament model for API responses."""
    id: str = Field(..., description="Unique identifier for the tournament")
    created_at: datetime = Field(..., description="When the tournament was created")
    updated_at: datetime = Field(..., description="When the tournament was last updated")
    created_by: Optional[str] = Field(None, description="ID of the user who created the tournament")
    
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

class TournamentListResponse(BaseModel):
    """Paginated list of tournaments with metadata."""
    items: List[TournamentResponse] = Field(..., description="List of tournaments")
    total: int = Field(..., description="Total number of tournaments matching the query")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    has_more: bool = Field(..., description="Whether there are more items available")

# Helper Functions
async def get_tournament_by_id(tournament_id: str) -> Optional[Dict[str, Any]]:
    """
    Helper function to get a tournament by ID with proper error handling.
    
    Args:
        tournament_id: The UUID of the tournament to retrieve
        
    Returns:
        Optional[Dict[str, Any]]: The tournament data if found, None otherwise
        
    Raises:
        HTTPException: If there's an error retrieving the tournament
    """
    try:
        if not tournament_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tournament ID is required"
            )
            
        result = supabase.get_by_id("tournaments", tournament_id)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving tournament {tournament_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the tournament"
        )

# API Endpoints
@router.post(
    "/",
    response_model=TournamentResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Tournament created successfully"},
        400: {"description": "Invalid input data or validation error"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        409: {"description": "Tournament with similar details already exists"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def create_tournament(
    request: Request,
    tournament: TournamentCreate,
    _: None = Depends(require_admin_api_token)
) -> Dict[str, Any]:
    """
    Create a new tournament (Admin only).
    
    This endpoint allows administrators to create new tournaments with all necessary details.
    """
    try:
        # Check for existing tournament with same name and dates
        client = supabase.get_client()
        existing_tournament = client.table("tournaments")\
            .select("*")\
            .ilike("name", tournament.name)\
            .eq("start_date", tournament.start_date.isoformat())\
            .execute()
        
        if existing_tournament and hasattr(existing_tournament, 'data') and existing_tournament.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A tournament with this name and start date already exists"
            )
        
        # Prepare tournament data
        tournament_data = tournament.dict(exclude_unset=True)
        tournament_data["created_by"] = "admin_api"
        
        # Create tournament
        created_tournament = supabase.insert("tournaments", tournament_data)
        
        return created_tournament
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tournament: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the tournament"
        )

@router.get(
    "/{tournament_id}",
    response_model=TournamentResponse,
    responses={
        200: {"description": "Tournament details retrieved successfully"},
        404: {"description": "Tournament not found"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_tournament(
    request: Request,
    tournament_id: str = Path(..., 
                        description="The UUID of the tournament to retrieve",
                        examples=[UUID_EXAMPLE], 
                        pattern=UUID_PATTERN),
) -> Dict[str, Any]:
    """
    Get tournament details by ID.
    
    This endpoint retrieves detailed information about a specific tournament.
    """
    try:
        tournament = await get_tournament_by_id(tournament_id)
        if not tournament:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tournament with ID {tournament_id} not found"
            )
        return tournament
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving tournament {tournament_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the tournament"
        )

@router.get(
    "/",
    response_model=TournamentListResponse,
    responses={
        200: {"description": "List of tournaments retrieved successfully"},
        400: {"description": "Invalid query parameters"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_tournaments(
    request: Request,
    name: Optional[str] = Query(
        None,
        description="Filter tournaments by name (case-insensitive contains)",
        min_length=1,
        max_length=100
    ),
    tier: Optional[EventTier] = Query(
        None,
        description="Filter tournaments by competitive tier"
    ),
    status: Optional[TournamentStatus] = Query(
        None,
        description="Filter tournaments by status"
    ),
    is_global: Optional[bool] = Query(
        None,
        description="Filter for global/regional tournaments"
    ),
    regions_id: Optional[str] = Query(
        None,
        description="Filter tournaments by region ID",
        pattern=UUID_PATTERN,
        examples=[UUID_EXAMPLE]
    ),
    season_number: Optional[int] = Query(
        None,
        ge=1,
        description="Filter tournaments by season number"
    ),
    start_date_after: Optional[datetime] = Query(
        None,
        description="Filter tournaments starting on or after this date"
    ),
    start_date_before: Optional[datetime] = Query(
        None,
        description="Filter tournaments starting on or before this date"
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
    List tournaments with optional filtering and pagination.
    
    This endpoint returns a paginated list of tournaments that match the specified filters.
    """
    try:
        offset = (page - 1) * size
        limit = size
        
        # Build query
        client = supabase.get_client()
        query = client.table("tournaments").select("*", count="exact")
        
        # Apply filters
        if name:
            query = query.ilike("name", f"%{name}%")
        if tier:
            query = query.eq("tier", tier)
        if status:
            query = query.eq("status", status)
        if is_global is not None:
            query = query.eq("is_global", is_global)
        if regions_id:
            query = query.eq("regions_id", regions_id)
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
        logger.error(f"Error listing tournaments: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving tournaments"
        )

@router.put(
    "/{tournament_id}",
    response_model=TournamentResponse,
    responses={
        200: {"description": "Tournament updated successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Tournament not found"},
        409: {"description": "Tournament with similar details already exists"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def update_tournament(
    request: Request,
    tournament_id: str = Path(..., 
                        description="The UUID of the tournament to update",
                        examples=[UUID_EXAMPLE], 
                        pattern=UUID_PATTERN),
    tournament_update: TournamentUpdate = Body(..., description="Tournament data to update"),
    _: None = Depends(require_admin_api_token)
) -> Dict[str, Any]:
    """
    Update an existing tournament (Admin only).
    
    This endpoint allows administrators to update tournament details.
    Only the fields provided in the request will be updated.
    """
    try:
        # Check if tournament exists
        existing_tournament = await get_tournament_by_id(tournament_id)
        if not existing_tournament:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tournament with ID {tournament_id} not found"
            )
        
        # Check for name/date conflict if name or dates are being updated
        if tournament_update.name or tournament_update.start_date:
            client = supabase.get_client()
            query = client.table("tournaments")\
                .select("*")\
                .neq("id", tournament_id)
                
            if tournament_update.name:
                query = query.ilike("name", tournament_update.name)
            else:
                query = query.ilike("name", existing_tournament["name"])
                
            if tournament_update.start_date:
                query = query.eq("start_date", tournament_update.start_date.isoformat())
            else:
                query = query.eq("start_date", existing_tournament["start_date"])
            
            conflict_check = query.execute()
            
            if conflict_check and hasattr(conflict_check, 'data') and conflict_check.data:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A tournament with this name and start date already exists"
                )
        
        # Prepare update data
        update_data = tournament_update.dict(exclude_unset=True)
        
        # Only update if there are changes
        if not update_data:
            return existing_tournament
        
        # Update tournament
        updated_tournament = supabase.update("tournaments", tournament_id, update_data)
        
        return updated_tournament
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tournament {tournament_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the tournament"
        )

@router.delete(
    "/{tournament_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Tournament deleted successfully"},
        400: {"description": "Cannot delete tournament with participants"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Tournament not found"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def delete_tournament(
    request: Request,
    tournament_id: str = Path(..., 
                        description="The UUID of the tournament to delete",
                        examples=[UUID_EXAMPLE], 
                        pattern=UUID_PATTERN),
    force: bool = Query(
        False,
        description="Force deletion even if the tournament has participants (use with caution)"
    ),
    _: None = Depends(require_admin_api_token)
) -> None:
    """
    Delete a tournament (Admin only).
    
    This endpoint allows administrators to delete a tournament.
    By default, tournaments with participants cannot be deleted unless force=True.
    """
    try:
        # Check if tournament exists
        tournament = await get_tournament_by_id(tournament_id)
        if not tournament:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tournament with ID {tournament_id} not found"
            )
        
        # Delete tournament
        supabase.delete("tournaments", tournament_id)
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tournament {tournament_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the tournament"
        )
