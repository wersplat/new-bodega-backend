"""
Events router for tournament and event management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.auth import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.event import Event, EventRegistration, EventStatus, EventType
from app.models.player import Player
from app.schemas.event import EventCreate, Event as EventSchema, EventUpdate, EventWithRegistrations

router = APIRouter()

@router.post("/", response_model=EventSchema)
async def create_event(
    event: EventCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a new event (admin only)
    """
    db_event = Event(
        name=event.name,
        description=event.description,
        event_type=event.event_type,
        entry_fee=event.entry_fee,
        max_participants=event.max_participants,
        start_date=event.start_date,
        end_date=event.end_date,
        created_by=current_user.id
    )
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    return db_event

@router.get("/", response_model=List[EventSchema])
async def list_events(
    status: EventStatus = None,
    event_type: EventType = None,
    db: Session = Depends(get_db)
):
    """
    List all events with optional filtering
    """
    query = db.query(Event)
    
    if status:
        query = query.filter(Event.status == status)
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    events = query.order_by(Event.created_at.desc()).all()
    return events

@router.get("/open", response_model=List[EventSchema])
async def list_open_events(db: Session = Depends(get_db)):
    """
    List all open events (draft + BYOT)
    """
    events = db.query(Event).filter(
        Event.status == EventStatus.OPEN
    ).order_by(Event.start_date.asc()).all()
    return events

@router.get("/{event_id}", response_model=EventWithRegistrations)
async def get_event(
    event_id: int = Path(..., description="ID of the event to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Get event details with registrations
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return event

@router.put("/{event_id}", response_model=EventSchema)
async def update_event(
    event_id: int = Path(..., description="ID of the event to update"),
    event_update: EventUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update event details (admin only)
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Update fields
    update_data = event_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    
    return event

@router.post("/{event_id}/register")
async def register_for_event(
    event_id: int = Path(..., description="ID of the event to register for"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Register current user for an event
    """
    # Check if event exists and is open
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if event.status != EventStatus.OPEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is not open for registration"
        )
    
    # Check if user has a player profile
    player = db.query(Player).filter(Player.user_id == current_user.id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player profile required to register for events"
        )
    
    # Check if already registered
    existing_registration = db.query(EventRegistration).filter(
        EventRegistration.event_id == event_id,
        EventRegistration.player_id == player.id
    ).first()
    
    if existing_registration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already registered for this event"
        )
    
    # Check if event is full
    if event.max_participants and event.current_participants >= event.max_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is full"
        )
    
    # Create registration
    registration = EventRegistration(
        event_id=event_id,
        player_id=player.id
    )
    
    db.add(registration)
    
    # Update participant count
    event.current_participants += 1
    
    db.commit()
    
    return {"message": "Successfully registered for event"}

@router.delete("/{event_id}/register")
async def unregister_from_event(
    event_id: int = Path(..., description="ID of the event to unregister from"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Unregister current user from an event
    """
    # Get player profile
    player = db.query(Player).filter(Player.user_id == current_user.id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player profile not found"
        )
    
    # Find registration
    registration = db.query(EventRegistration).filter(
        EventRegistration.event_id == event_id,
        EventRegistration.player_id == player.id
    ).first()
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not registered for this event"
        )
    
    # Remove registration
    db.delete(registration)
    
    # Update participant count
    event = db.query(Event).filter(Event.id == event_id).first()
    if event:
        event.current_participants = max(0, event.current_participants - 1)
    
    db.commit()
    
    return {"message": "Successfully unregistered from event"} 