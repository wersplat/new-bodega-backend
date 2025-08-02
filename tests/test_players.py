"""
Tests for player schemas and models
"""

import pytest
from datetime import datetime, timezone
from uuid import UUID
from pydantic import ValidationError
from app.schemas.player import (
    PlayerBase,
    PlayerCreate,
    PlayerUpdate,
    PlayerInDB,
    PlayerProfile,
    PlayerWithHistory,
    RPHistory,
    PlayerTier
)

# Test data
TEST_PLAYER_ID = 1
TEST_USER_ID = 100
TEST_TEAM_ID = 10
TEST_REGION_ID = 5

# Helper function to create a base player
def create_base_player():
    return {
        "gamertag": "TestPlayer",
        "platform": "PS5",
        "team_name": "Test Team",
        "region": "NA",
        "bio": "Test bio"
    }

def test_player_base():
    """Test creating a base player"""
    player_data = create_base_player()
    player = PlayerBase(**player_data)
    
    assert player.gamertag == "TestPlayer"
    assert player.platform == "PS5"
    assert player.team_name == "Test Team"
    assert player.region == "NA"
    assert player.bio == "Test bio"

def test_player_create():
    """Test creating a new player with required fields"""
    player_data = create_base_player()
    player_data["user_id"] = TEST_USER_ID
    
    player = PlayerCreate(**player_data)
    
    assert player.gamertag == "TestPlayer"
    assert player.user_id == TEST_USER_ID
    assert player.team_name == "Test Team"

def test_player_create_validation():
    """Test validation of player creation"""
    # Test missing required fields
    with pytest.raises(ValidationError):
        PlayerCreate(gamertag="", platform="PS5", user_id=TEST_USER_ID)
    
    # Test invalid user_id
    with pytest.raises(ValidationError):
        PlayerCreate(gamertag="Test", platform="PS5", user_id=-1)

def test_player_update():
    """Test updating a player with partial data"""
    update_data = {
        "gamertag": "UpdatedGamertag",
        "bio": "Updated bio"
    }
    
    update = PlayerUpdate(**update_data)
    
    assert update.gamertag == "UpdatedGamertag"
    assert update.bio == "Updated bio"
    assert update.team_name is None  # Not updated
    assert update.region is None     # Not updated

def test_player_in_db():
    """Test creating a player in the database"""
    created_at = datetime.now(timezone.utc)
    updated_at = datetime.now(timezone.utc)
    
    player_data = {
        "id": TEST_PLAYER_ID,
        "gamertag": "DBPlayer",
        "platform": "Xbox",
        "position": "PG",
        "region_id": TEST_REGION_ID,
        "current_team_id": TEST_TEAM_ID,
        "performance_score": 85.5,
        "player_rp": 2500.0,
        "player_rank_score": 2600.0,
        "salary_tier": 5,
        "monthly_value": 10000.0,
        "is_rookie": False,
        "discord_id": "player123",
        "twitter_id": "@player123",
        "alternate_gamertag": "AltPlayer123",
        "created_at": created_at,
        "updated_at": updated_at,
        "team_name": "DB Team",
        "region": "EU",
        "bio": "Database player bio"
    }
    
    player = PlayerInDB(**player_data)
    
    # Test required fields
    assert player.id == TEST_PLAYER_ID
    assert player.gamertag == "DBPlayer"
    assert player.platform == "Xbox"
    
    # Test optional fields
    assert player.position == "PG"
    assert player.region_id == TEST_REGION_ID
    assert player.current_team_id == TEST_TEAM_ID
    assert player.performance_score == 85.5
    assert player.player_rp == 2500.0
    assert player.player_rank_score == 2600.0
    assert player.salary_tier == 5
    assert player.monthly_value == 10000.0
    assert player.is_rookie is False
    assert player.discord_id == "player123"
    assert player.twitter_id == "@player123"
    assert player.alternate_gamertag == "AltPlayer123"
    assert player.created_at == created_at
    assert player.updated_at == updated_at

def test_player_profile():
    """Test creating a player profile with extended information"""
    created_at = datetime.now(timezone.utc)
    
    profile_data = {
        "id": TEST_PLAYER_ID,
        "gamertag": "ProfilePlayer",
        "platform": "PC",
        "username": "profileuser",
        "full_name": "Test User",
        "position": "SG",
        "region_id": TEST_REGION_ID,
        "current_team_id": TEST_TEAM_ID,
        "performance_score": 90.0,
        "player_rp": 2700.0,
        "player_rank_score": 2800.0,
        "salary_tier": 6,
        "monthly_value": 12000.0,
        "is_rookie": True,
        "discord_id": "profile123",
        "twitter_id": "@profile123",
        "alternate_gamertag": "ProfileAlt",
        "created_at": created_at,
        "team_name": "Profile Team",
        "region": "NA",
        "bio": "Player profile bio"
    }
    
    profile = PlayerProfile(**profile_data)
    
    # Test extended fields
    assert profile.username == "profileuser"
    assert profile.full_name == "Test User"
    
    # Test inherited fields
    assert profile.gamertag == "ProfilePlayer"
    assert profile.position == "SG"
    assert profile.is_rookie is True

def test_rp_history():
    """Test RP history model"""
    now = datetime.now(timezone.utc)
    
    history_data = {
        "id": 1,
        "player_id": TEST_PLAYER_ID,
        "old_rp": 1000.0,
        "new_rp": 1100.0,
        "change_reason": "Tournament win",
        "event_id": 5,
        "created_at": now
    }
    
    history = RPHistory(**history_data)
    
    assert history.id == 1
    assert history.player_id == TEST_PLAYER_ID
    assert history.old_rp == 1000.0
    assert history.new_rp == 1100.0
    assert history.change_reason == "Tournament win"
    assert history.event_id == 5
    assert history.created_at == now

def test_player_with_history():
    """Test player with RP history"""
    now = datetime.now(timezone.utc)
    
    player_data = {
        "id": TEST_PLAYER_ID,
        "gamertag": "HistoryPlayer",
        "platform": "Xbox",
        "created_at": now,
        "player_rp": 2500.0,
        "player_rank_score": 2600.0,
        "team_name": "History Team",
        "region": "NA"
    }
    
    history_data = [
        {
            "id": 1,
            "player_id": TEST_PLAYER_ID,
            "old_rp": 1000.0,
            "new_rp": 1100.0,
            "change_reason": "Tournament win",
            "created_at": now
        },
        {
            "id": 2,
            "player_id": TEST_PLAYER_ID,
            "old_rp": 1100.0,
            "new_rp": 1200.0,
            "change_reason": "Weekly bonus",
            "created_at": now
        }
    ]
    
    history = [RPHistory(**item) for item in history_data]
    player = PlayerWithHistory(**player_data, rp_history=history)
    
    assert player.gamertag == "HistoryPlayer"
    assert len(player.rp_history) == 2
    assert player.rp_history[0].change_reason == "Tournament win"
    assert player.rp_history[1].change_reason == "Weekly bonus"

def test_player_tier_enum():
    """Test player tier enum values"""
    assert PlayerTier.BRONZE == "bronze"
    assert PlayerTier.SILVER == "silver"
    assert PlayerTier.GOLD == "gold"
    assert PlayerTier.PLATINUM == "platinum"
    assert PlayerTier.DIAMOND == "diamond"
    assert PlayerTier.PINK_DIAMOND == "pink_diamond"
    assert PlayerTier.GALAXY_OPAL == "galaxy_opal"
    
    # Test enum iteration
    tiers = list(PlayerTier)
    assert len(tiers) == 7
    assert PlayerTier.BRONZE in tiers
