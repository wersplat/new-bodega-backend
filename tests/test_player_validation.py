"""
Tests for player model validation and edge cases.
"""

import pytest
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError
from app.schemas.player import (
    PlayerCreate,
    PlayerUpdate,
    PlayerInDB,
    LeaderboardTier
)

# Test data
TEST_USER_ID = 100

# Helper function to create a base player
def create_base_player():
    return {
        "gamertag": "TestPlayer123",
        "region": "NA",
        "team_name": "Test Team",
        "user_id": TEST_USER_ID
    }

def test_gamertag_validation():
    """Test validation of gamertag field."""
    # Test minimum length
    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        PlayerCreate(gamertag="", region="NA", user_id=TEST_USER_ID)
    
    # Test maximum length
    long_gamertag = "A" * 101  # 101 characters (max is 100)
    with pytest.raises(ValidationError, match="String should have at most 100 characters"):
        PlayerCreate(gamertag=long_gamertag, region="NA", user_id=TEST_USER_ID)
    
    # Test valid gamertag
    valid_gamertag = "ValidPlayer_123"
    player = PlayerCreate(gamertag=valid_gamertag, region="NA", user_id=TEST_USER_ID)
    assert player.gamertag == valid_gamertag

def test_region_validation():
    """Test validation of region field."""
    # Test optional region
    player = PlayerCreate(gamertag="TestPlayer", region=None, user_id=TEST_USER_ID)
    assert player.region is None
    
    # Test region length
    long_region = "A" * 51  # 51 characters (max is 50)
    with pytest.raises(ValidationError, match="String should have at most 50 characters"):
        PlayerCreate(gamertag="TestPlayer", region=long_region, user_id=TEST_USER_ID)

def test_team_name_validation():
    """Test validation of team_name field."""
    # Test optional team_name
    player = PlayerCreate(gamertag="TestPlayer", region="NA", user_id=TEST_USER_ID, team_name=None)
    assert player.team_name is None
    
    # Test team_name length
    long_team = "A" * 101  # 101 characters (max is 100)
    with pytest.raises(ValidationError, match="String should have at most 100 characters"):
        PlayerCreate(gamertag="TestPlayer", region="NA", user_id=TEST_USER_ID, team_name=long_team)

def test_user_id_validation():
    """Test validation of user_id field."""
    # Test invalid user_id (must be positive)
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        PlayerCreate(gamertag="TestPlayer", region="NA", user_id=0)
    
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        PlayerCreate(gamertag="TestPlayer", region="NA", user_id=-1)
    
    # Test valid user_id
    player = PlayerCreate(gamertag="TestPlayer", region="NA", user_id=1)
    assert player.user_id == 1

def test_player_update_validation():
    """Test validation of player updates."""
    # Test empty update (should be valid)
    update = PlayerUpdate()
    assert update.gamertag is None
    assert update.region is None
    assert update.team_name is None
    
    # Test partial update with gamertag
    update = PlayerUpdate(gamertag="NewGamertag")
    assert update.gamertag == "NewGamertag"
    assert update.region is None
    assert update.team_name is None
    
    # Test partial update with team_name
    update = PlayerUpdate(team_name="New Team")
    assert update.gamertag is None
    assert update.region is None
    assert update.team_name == "New Team"
    
    # Test that a long gamertag is accepted (no length validation in PlayerUpdate)
    long_gamertag = "A" * 150
    update = PlayerUpdate(gamertag=long_gamertag)
    assert update.gamertag == long_gamertag
    
    # Test that unknown fields are allowed (Pydantic allows extra fields by default)
    update = PlayerUpdate(unknown_field="test")
    assert update.gamertag is None
    assert update.region is None
    assert update.team_name is None

def test_player_in_db_validation():
    """Test validation of PlayerInDB model."""
    now = datetime.now(timezone.utc)
    
    # Test required fields
    with pytest.raises(ValidationError):
        PlayerInDB(id=1, gamertag="TestPlayer")
    
    # Test RP validation
    with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
        PlayerInDB(
            id=1, 
            gamertag="TestPlayer", 
            player_rp=-1.0,
            player_rank_score=100.0,
            created_at=now
        )
    
    # Test valid player
    player = PlayerInDB(
        id=1,
        gamertag="TestPlayer",
        player_rp=1000.0,
        player_rank_score=1100.0,
        created_at=now
    )
    assert player.id == 1
    assert player.gamertag == "TestPlayer"
    assert player.player_rp == 1000.0
    assert player.player_rank_score == 1100.0
    assert player.created_at == now

def test_leaderboard_tier_enum_values():
    """Test that all leaderboard tier enum values are valid."""
    # Test all enum values
    tiers = [tier.value for tier in LeaderboardTier]
    assert set(tiers) == {
        "bronze", "silver", "gold", "platinum", 
        "diamond", "pink_diamond", "galaxy_opal"
    }
    
    # Test case sensitivity
    with pytest.raises(ValueError):
        LeaderboardTier("BRONZE")  # Should be lowercase
