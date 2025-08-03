"""Tests for badge schemas and models."""

import pytest
from datetime import datetime, timezone
from uuid import UUID
from pydantic import ValidationError
from app.schemas.badge import (
    BadgeBase,
    BadgeCreate,
    BadgeUpdate,
    BadgeInDB,
    Badge,
    PlayerBadgeBase,
    PlayerBadgeCreate,
    PlayerBadgeInDB,
    PlayerBadge,
    PlayerBadgeWithDetails
)

# Test data
TEST_BADGE_ID = 1
TEST_PLAYER_ID = 100
TEST_ADMIN_ID = 1

# Helper function to create a base badge
def create_base_badge():
    return {
        "name": "Test Badge",
        "description": "A test badge for testing purposes",
        "icon_url": "https://example.com/badge.png",
        "rarity": "rare"
    }

def test_badge_base():
    """Test creating a base badge."""
    badge_data = create_base_badge()
    badge = BadgeBase(**badge_data)
    
    assert badge.name == "Test Badge"
    assert badge.description == "A test badge for testing purposes"
    assert badge.icon_url == "https://example.com/badge.png"
    assert badge.rarity == "rare"
    # is_active is not part of BadgeBase, only in BadgeInDB

def test_badge_create():
    """Test creating a new badge with required fields."""
    badge_data = create_base_badge()
    badge = BadgeCreate(**badge_data)
    
    assert badge.name == "Test Badge"
    assert badge.rarity == "rare"


def test_badge_update():
    """Test updating a badge with partial data"""
    update_data = {
        "name": "Updated Badge Name",
        "description": "Updated description"
    }
    badge = BadgeUpdate(**update_data)
    
    assert badge.name == "Updated Badge Name"
    assert badge.description == "Updated description"
    assert badge.rarity is None  # Not updated


def test_badge_rarity_validation():
    """Test that rarity can be any string and is not validated in the base model."""
    # Test various rarities - the base model doesn't validate the rarity
    test_rarities = ["common", "uncommon", "rare", "epic", "legendary", "invalid_rarity"]
    for rarity in test_rarities:
        badge_data = create_base_badge()
        badge_data["rarity"] = rarity
        badge = BadgeBase(**badge_data)
        assert badge.rarity == rarity  # Should accept any string value


def test_player_badge_create():
    """Test creating a player badge association"""
    player_badge_data = {
        "player_id": TEST_PLAYER_ID,
        "badge_id": TEST_BADGE_ID,
        "awarded_by": TEST_ADMIN_ID,
        "is_equipped": True
    }
    
    player_badge = PlayerBadgeCreate(**player_badge_data)
    
    assert player_badge.player_id == TEST_PLAYER_ID
    assert player_badge.badge_id == TEST_BADGE_ID
    assert player_badge.awarded_by == TEST_ADMIN_ID
    assert player_badge.is_equipped is True


def test_player_badge_with_details():
    """Test the PlayerBadgeWithDetails schema"""
    # Create a badge
    badge_data = {
        "id": 1,
        "name": "Test Badge",
        "description": "Test description",
        "rarity": "rare",
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }
    badge = Badge(**badge_data)
    
    # Create player badge with details
    player_badge_data = {
        "id": 1,
        "player_id": 100,
        "badge_id": 1,
        "is_equipped": True,
        "awarded_by": 1,
        "awarded_at": datetime.now(timezone.utc),
        "badge": badge
    }
    
    player_badge = PlayerBadgeWithDetails(**player_badge_data)
    
    assert player_badge.id == 1
    assert player_badge.player_id == 100
    assert player_badge.badge_id == 1
    assert player_badge.is_equipped is True
    assert player_badge.awarded_by == 1
    assert isinstance(player_badge.awarded_at, datetime)
    assert isinstance(player_badge.badge, Badge)
    assert player_badge.badge.name == "Test Badge"
