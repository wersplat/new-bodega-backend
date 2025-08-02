"""
Tests for event schemas and models
"""

import pytest
from datetime import date, datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
from pydantic import ValidationError
from app.schemas.event import (
    EventCreate, 
    EventInDB, 
    EventUpdate, 
    EventTier, 
    EventType, 
    EventStatus,
    EventRegistration,
    EventResult
)

# Test data
TEST_EVENT_ID = uuid4()
TEST_PLAYER_ID = uuid4()
TEST_TEAM_ID = uuid4()

def test_event_create():
    """Test creating a new event with all required and optional fields"""
    # Test with all fields
    event_data = {
        "name": "Test Event",
        "type": EventType.LEAGUE,
        "description": "Test description",
        "is_global": False,
        "region_id": str(uuid4()),
        "start_date": date(2025, 8, 1),
        "end_date": date(2025, 8, 31),
        "max_rp": 1000,
        "decay_days": 7,
        "tier": EventTier.T1,
        "season_number": 1,
        "prize_pool": 10000,
        "banner_url": "https://example.com/banner.jpg",
        "rules_url": "https://example.com/rules.pdf"
    }
    
    event = EventCreate(**event_data)
    
    # Test required fields
    assert event.name == "Test Event"
    assert event.type == EventType.LEAGUE
    assert event.is_global is False
    
    # Test optional fields
    assert event.description == "Test description"
    assert event.region_id == UUID(event_data["region_id"])
    assert event.start_date == date(2025, 8, 1)
    assert event.end_date == date(2025, 8, 31)
    assert event.max_rp == 1000
    assert event.decay_days == 7
    assert event.tier == EventTier.T1
    assert event.season_number == 1
    assert event.prize_pool == 10000
    assert str(event.banner_url) == "https://example.com/banner.jpg"
    assert str(event.rules_url) == "https://example.com/rules.pdf"

def test_event_create_required_fields_only():
    """Test creating an event with only required fields"""
    event_data = {
        "name": "Required Fields Only",
        "type": EventType.TOURNAMENT,
    }
    
    event = EventCreate(**event_data)
    
    assert event.name == "Required Fields Only"
    assert event.type == EventType.TOURNAMENT
    assert event.is_global is False  # Default value
    assert event.description is None
    assert event.region_id is None
    assert event.start_date is None
    assert event.end_date is None
    assert event.max_rp is None
    assert event.decay_days is None
    assert event.tier is None
    assert event.season_number is None
    assert event.prize_pool is None
    assert event.banner_url is None
    assert event.rules_url is None

def test_event_create_validation():
    """Test validation of event creation"""
    # Test invalid name (empty)
    with pytest.raises(ValidationError):
        EventCreate(name="", type=EventType.LEAGUE)
    
    # Test invalid prize pool (negative)
    with pytest.raises(ValidationError):
        EventCreate(name="Invalid Prize", type=EventType.LEAGUE, prize_pool=-100)
    
    # Test invalid season number (less than 1)
    with pytest.raises(ValidationError):
        EventCreate(name="Invalid Season", type=EventType.LEAGUE, season_number=0)

def test_event_in_db():
    """Test creating an event in the database"""
    created_at = datetime.now(timezone.utc)
    updated_at = datetime.now(timezone.utc)
    processed_at = datetime.now(timezone.utc)
    
    event_data = {
        "id": TEST_EVENT_ID,
        "name": "DB Event",
        "type": EventType.TOURNAMENT,
        "status": EventStatus.UPCOMING,
        "is_global": True,
        "created_at": created_at,
        "updated_at": updated_at,
        "processed_at": processed_at,
        "tier": EventTier.T2,
        "processed": False,
        "description": "Database event description",
        "region_id": str(uuid4()),
        "start_date": date(2025, 9, 1),
        "end_date": date(2025, 9, 30),
        "max_rp": 2000,
        "decay_days": 14,
        "season_number": 2,
        "prize_pool": 20000,
        "banner_url": "https://example.com/banner2.jpg",
        "rules_url": "https://example.com/rules2.pdf"
    }
    
    event = EventInDB(**event_data)
    
    # Test required fields
    assert event.id == TEST_EVENT_ID
    assert event.name == "DB Event"
    assert event.type == EventType.TOURNAMENT
    assert event.status == EventStatus.UPCOMING
    assert event.processed is False
    assert event.created_at == created_at
    
    # Test optional fields
    assert event.updated_at == updated_at
    assert event.processed_at == processed_at
    assert event.tier == EventTier.T2
    assert event.is_global is True
    assert event.description == "Database event description"
    assert event.region_id == UUID(event_data["region_id"])
    assert event.start_date == date(2025, 9, 1)
    assert event.end_date == date(2025, 9, 30)
    assert event.max_rp == 2000
    assert event.decay_days == 14
    assert event.season_number == 2
    assert event.prize_pool == 20000
    assert str(event.banner_url) == "https://example.com/banner2.jpg"
    assert str(event.rules_url) == "https://example.com/rules2.pdf"

def test_event_update():
    """Test updating an event with partial data"""
    # Test with partial update
    update_data = {
        "name": "Updated Event Name",
        "status": EventStatus.IN_PROGRESS,
        "prize_pool": 15000,
        "description": "Updated description",
        "rules_url": "https://example.com/updated_rules.pdf"
    }
    
    update = EventUpdate(**update_data)
    
    # Test updated fields
    assert update.name == "Updated Event Name"
    assert update.status == EventStatus.IN_PROGRESS
    assert update.prize_pool == 15000
    assert update.description == "Updated description"
    assert str(update.rules_url) == "https://example.com/updated_rules.pdf"
    
    # Test that other fields are None (not updated)
    assert update.type is None
    assert update.is_global is None
    assert update.region_id is None
    assert update.start_date is None
    assert update.end_date is None

def test_event_registration():
    """Test event registration model"""
    registration_data = {
        "id": 1,
        "event_id": 1,
        "player_id": 1,
        "registration_date": datetime.now(timezone.utc),
        "payment_status": "paid",
        "is_confirmed": True
    }
    
    registration = EventRegistration(**registration_data)
    
    assert registration.id == 1
    assert registration.event_id == 1
    assert registration.player_id == 1
    assert registration.payment_status == "paid"
    assert registration.is_confirmed is True

def test_event_result():
    """Test event result model"""
    result_data = {
        "id": 1,
        "event_id": 1,
        "player_id": 1,
        "position": 1,
        "rp_earned": 100.5,
        "rp_before": 500.0,
        "rp_after": 600.5,
        "created_at": datetime.now(timezone.utc)
    }
    
    result = EventResult(**result_data)
    
    assert result.id == 1
    assert result.event_id == 1
    assert result.player_id == 1
    assert result.position == 1
    assert result.rp_earned == 100.5
    assert result.rp_before == 500.0
    assert result.rp_after == 600.5

def test_event_relationships():
    """Test event relationships with registrations and results"""
    from app.schemas.event import EventWithRegistrations, EventWithResults
    
    # Create test data
    event_data = {
        "id": TEST_EVENT_ID,
        "name": "Event with Relationships",
        "type": EventType.LEAGUE,
        "status": EventStatus.UPCOMING,
        "created_at": datetime.now(timezone.utc),
        "tier": EventTier.T1
    }
    
    registration = EventRegistration(
        id=1,
        event_id=1,
        player_id=1,
        registration_date=datetime.now(timezone.utc),
        payment_status="paid",
        is_confirmed=True
    )
    
    result = EventResult(
        id=1,
        event_id=1,
        player_id=1,
        position=1,
        rp_earned=100.0,
        rp_before=500.0,
        rp_after=600.0,
        created_at=datetime.now(timezone.utc)
    )
    
    # Test event with registrations
    event_with_registrations = EventWithRegistrations(
        **event_data,
        registrations=[registration]
    )
    assert len(event_with_registrations.registrations) == 1
    assert event_with_registrations.registrations[0].id == 1
    
    # Test event with results
    event_with_results = EventWithResults(
        **event_data,
        results=[result]
    )
    assert len(event_with_results.results) == 1
    assert event_with_results.results[0].id == 1
