"""
Pydantic schemas for events and tournaments
"""

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_serializer
from typing import Optional, List, Literal, ClassVar, Dict, Any
from datetime import date, datetime
from enum import Enum
from uuid import UUID

class EventTier(str, Enum):
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"

class EventType(str, Enum):
    LEAGUE = "League"
    TOURNAMENT = "Tournament"

class EventStatus(str, Enum):
    UPCOMING = "upcoming"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class EventBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str = Field(..., min_length=1)
    type: EventType
    description: Optional[str] = None
    is_global: bool = False
    region_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    max_rp: Optional[int] = Field(None, ge=0)
    decay_days: Optional[int] = Field(None, ge=0)
    tier: Optional[EventTier] = None
    season_number: Optional[int] = Field(None, ge=1)
    prize_pool: Optional[int] = Field(None, ge=0)
    banner_url: Optional[HttpUrl] = None
    rules_url: Optional[HttpUrl] = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    type: Optional[EventType] = None
    description: Optional[str] = None
    is_global: Optional[bool] = None
    region_id: Optional[UUID] = None
    status: Optional[EventStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    max_rp: Optional[int] = Field(None, ge=0)
    decay_days: Optional[int] = Field(None, ge=0)
    processed: Optional[bool] = None
    banner_url: Optional[HttpUrl] = None
    rules_url: Optional[HttpUrl] = None
    tier: Optional[EventTier] = None
    season_number: Optional[int] = Field(None, ge=1)
    prize_pool: Optional[int] = Field(None, ge=0)

class EventInDB(EventBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    status: EventStatus = EventStatus.UPCOMING
    processed: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    
    @field_serializer('id')
    def serialize_id(self, id: UUID, _info):
        return str(id)
        
    @field_serializer('banner_url', 'rules_url', check_fields=False)
    def serialize_url(self, url: Optional[HttpUrl], _info):
        return str(url) if url else None

class Event(EventInDB):
    """Public-facing event model"""
    pass

class EventRegistration(BaseModel):
    id: int
    event_id: int
    player_id: int
    registration_date: datetime
    payment_status: str
    is_confirmed: bool
    
    class Config:
        from_attributes = True

class EventResult(BaseModel):
    id: int
    event_id: int
    player_id: int
    position: Optional[int] = None
    rp_earned: float
    rp_before: float
    rp_after: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class EventWithRegistrations(Event):
    """Event with registration details"""
    registrations: List[EventRegistration] = []

class EventWithResults(Event):
    """Event with results"""
    results: List[EventResult] = [] 