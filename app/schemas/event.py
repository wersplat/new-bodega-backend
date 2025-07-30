"""
Pydantic schemas for events and tournaments
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    DRAFT = "draft"
    BYOT = "byot"
    TOURNAMENT = "tournament"
    LEAGUE = "league"

class EventStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    REGISTRATION_CLOSED = "registration_closed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    event_type: EventType
    entry_fee: float = 0.0
    max_participants: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[EventType] = None
    status: Optional[EventStatus] = None
    entry_fee: Optional[float] = None
    max_participants: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class EventInDB(EventBase):
    id: int
    status: EventStatus
    current_participants: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Event(EventInDB):
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