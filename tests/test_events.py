"""
Tests for event schemas and models
"""

import pytest
from datetime import date
from uuid import uuid4
from app.schemas.event import EventCreate, EventInDB, EventUpdate, EventTier, EventType, EventStatus

def test_event_create():
    """Test creating a new event"""
    event_data = {
        "name": "Test Event",
        "type": EventType.LEAGUE,
        "description": "Test description",
        "is_global": False,
        "start_date": date(2025, 8, 1),
        "end_date": date(2025, 8, 31),
        "tier": EventTier.T1,
        "season_number": 1,
        "prize_pool": 10000
    }
    
    event = EventCreate(**event_data)
    
    assert event.name == "Test Event"
    assert event.type == EventType.LEAGUE
    assert event.tier == EventTier.T1
    assert event.season_number == 1

def test_event_in_db():
    """Test creating an event in the database"""
    event_data = {
        "id": uuid4(),
        "name": "DB Event",
        "type": EventType.TOURNAMENT,
        "status": EventStatus.UPCOMING,
        "created_at": "2025-07-30T14:00:00Z",
        "tier": EventTier.T2
    }
    
    event = EventInDB(**event_data)
    
    assert event.id is not None
    assert event.status == EventStatus.UPCOMING
    assert event.processed is False

def test_event_update():
    """Test updating an event"""
    update_data = {
        "name": "Updated Event Name",
        "status": EventStatus.IN_PROGRESS,
        "prize_pool": 15000
    }
    
    update = EventUpdate(**update_data)
    
    assert update.name == "Updated Event Name"
    assert update.status == EventStatus.IN_PROGRESS
    assert update.prize_pool == 15000
