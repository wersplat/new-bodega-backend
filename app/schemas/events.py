"""
Event Schema Definitions

This module defines Pydantic models for event-related data validation and serialization.
These schemas are used for request/response validation and OpenAPI documentation.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class EventStatus(str, Enum):
    """Enumeration of possible event statuses."""
    DRAFT = "draft"
    UPCOMING = "upcoming"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


class EventType(str, Enum):
    """Enumeration of possible event types."""
    LEAGUE = "League"
    TOURNAMENT = "Tournament"
    SHOWMATCH = "Showmatch"
    SCRIM = "Scrim"
    OTHER = "Other"


class EventTier(str, Enum):
    """Enumeration of event tiers for competitive events."""
    T1 = "T1"  # Professional/Elite
    T2 = "T2"  # Semi-Professional
    T3 = "T3"  # Amateur/Community
    T4 = "T4"  # Casual/Open


class EventBase(BaseModel):
    """Base schema with common event fields."""
    name: str = Field(..., min_length=3, max_length=100, description="Name of the event")
    description: Optional[str] = Field(
        None, 
        max_length=2000, 
        description="Detailed description of the event"
    )
    event_type: EventType = Field(..., description="Type of the event")
    status: EventStatus = Field(default=EventStatus.DRAFT, description="Current status of the event")
    tier: EventTier = Field(..., description="Competitive tier of the event")
    
    # Timing information
    start_date: datetime = Field(..., description="Scheduled start date and time of the event")
    end_date: Optional[datetime] = Field(
        None, 
        description="Scheduled end date and time of the event (if known)"
    )
    registration_deadline: Optional[datetime] = Field(
        None, 
        description="Deadline for event registration"
    )
    
    # Location information
    is_online: bool = Field(True, description="Whether the event is held online")
    location: Optional[str] = Field(
        None, 
        max_length=200, 
        description="Physical location (for offline events) or online platform details"
    )
    
    # Game/Competition details
    game_id: str = Field(..., description="ID of the game this event is for")
    season_number: Optional[int] = Field(
        None, 
        ge=1, 
        description="Season number if this is part of a seasonal competition"
    )
    
    # Region information
    is_global: bool = Field(False, description="Whether this is a global event")
    region_id: Optional[str] = Field(
        None, 
        description="ID of the region this event belongs to (if not global)",
        pattern=r"^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
    )
    
    # Media and assets
    banner_url: Optional[str] = Field(
        None, 
        description="URL to the event banner image"
    )
    thumbnail_url: Optional[str] = Field(
        None, 
        description="URL to the event thumbnail image"
    )
    
    # Rules and requirements
    rules: Optional[Dict[str, Any]] = Field(
        None, 
        description="Custom rules and requirements for the event"
    )
    
    # Prizing information
    prize_pool: Optional[float] = Field(
        None, 
        ge=0, 
        description="Total prize pool amount (if any)"
    )
    prize_distribution: Optional[Dict[str, Any]] = Field(
        None, 
        description="Detailed prize distribution structure"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Summer Championship 2023",
                "description": "Annual summer gaming championship featuring top teams",
                "event_type": "Tournament",
                "status": "upcoming",
                "tier": "T1",
                "start_date": "2023-07-15T15:00:00Z",
                "end_date": "2023-07-18T22:00:00Z",
                "registration_deadline": "2023-07-10T23:59:59Z",
                "is_online": False,
                "location": "Los Angeles Convention Center, CA",
                "game_id": "550e8400-e29b-41d4-a716-446655440000",
                "season_number": 5,
                "is_global": True,
                "banner_url": "https://example.com/banners/summer-champ-2023.jpg",
                "thumbnail_url": "https://example.com/thumbnails/summer-champ-2023.jpg",
                "prize_pool": 100000.0,
                "prize_distribution": {
                    "1st": 50000,
                    "2nd": 30000,
                    "3rd-4th": 10000
                }
            }
        }
    )
    
    @model_validator(mode='after')
    def validate_dates(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValueError('End date must be after start date')
        return self
    
    @model_validator(mode='after')
    def validate_registration_deadline(self):
        if self.registration_deadline and self.start_date and self.registration_deadline > self.start_date:
            raise ValueError('Registration deadline must be before the event start time')
        return self
    
    @model_validator(mode='after')
    def validate_region_id(self):
        if not self.is_global and not self.region_id:
            raise ValueError('Region ID is required for non-global events')
        return self


class EventCreate(EventBase):
    """Schema for creating a new event."""
    pass


class EventUpdate(BaseModel):
    """Schema for updating an existing event."""
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="Updated name of the event")
    description: Optional[str] = Field(None, max_length=2000, description="Updated description")
    event_type: Optional[EventType] = Field(None, description="Updated event type")
    status: Optional[EventStatus] = Field(None, description="Updated status")
    tier: Optional[EventTier] = Field(None, description="Updated tier")
    start_date: Optional[datetime] = Field(None, description="Updated start date and time")
    end_date: Optional[datetime] = Field(None, description="Updated end date and time")
    registration_deadline: Optional[datetime] = Field(None, description="Updated registration deadline")
    is_online: Optional[bool] = Field(None, description="Updated online status")
    location: Optional[str] = Field(None, max_length=200, description="Updated location")
    game_id: Optional[str] = Field(None, description="Updated game ID")
    season_number: Optional[int] = Field(None, ge=1, description="Updated season number")
    is_global: Optional[bool] = Field(None, description="Updated global status")
    region_id: Optional[str] = Field(
            None, 
            description="Updated region ID (if not global)"
        )
    
    @field_validator('region_id')
    @classmethod
    def validate_region_id(cls, v: Optional[str], info):
        if v is not None and not info.data.get('is_global', False):
            # Validate UUID format if region_id is provided and event is not global
            import re
            if not re.match(r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$', v):
                raise ValueError('Invalid UUID format for region_id')
        return v
    
    banner_url: Optional[str] = Field(None, description="Updated banner URL")
    thumbnail_url: Optional[str] = Field(None, description="Updated thumbnail URL")
    rules: Optional[Dict[str, Any]] = Field(None, description="Updated rules")
    prize_pool: Optional[float] = Field(None, ge=0, description="Updated prize pool")
    prize_distribution: Optional[Dict[str, Any]] = Field(None, description="Updated prize distribution")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Summer Championship 2023 - Updated",
                "status": "in_progress",
                "prize_pool": 120000.0,
                "prize_distribution": {
                    "1st": 60000,
                    "2nd": 35000,
                    "3rd-4th": 12500
                }
            }
        }
    )


class EventSchema(EventBase):
    """Complete event schema including read-only fields."""
    id: str = Field(..., description="Unique identifier for the event")
    created_at: datetime = Field(..., description="When the event was created")
    updated_at: Optional[datetime] = Field(None, description="When the event was last updated")
    created_by: str = Field(..., description="ID of the user who created the event")
    updated_by: Optional[str] = Field(None, description="ID of the user who last updated the event")
    participant_count: int = Field(0, description="Number of participants registered for the event")
    
    model_config = ConfigDict(
        json_schema_extra={
            **EventBase.model_config["json_schema_extra"]["example"],
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "created_at": "2023-01-15T10:30:00Z",
            "updated_at": "2023-01-20T14:45:00Z",
            "created_by": "550e8400-e29b-41d4-a716-446655440000",
            "updated_by": "550e8400-e29b-41d4-a716-446655440001",
            "participant_count": 42
        }
    )
