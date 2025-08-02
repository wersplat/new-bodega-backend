"""
Tests for team schemas and models
"""

import pytest
from datetime import datetime, timezone
from uuid import UUID, uuid4
from pydantic import ValidationError, HttpUrl
from app.schemas.team import (
    TeamBase,
    TeamCreate,
    TeamUpdate,
    TeamInDB,
    TeamWithPlayers,
    TeamWithStats,
    TeamStanding,
    TeamTier
)

# Test data
TEST_TEAM_ID = uuid4()
TEST_REGION_ID = uuid4()

def test_team_base():
    """Test creating a base team"""
    team_data = {
        "name": "Test Team",
        "logo_url": "https://example.com/logo.png",
        "region_id": str(TEST_REGION_ID)
    }
    
    team = TeamBase(**team_data)
    
    assert team.name == "Test Team"
    assert str(team.logo_url) == "https://example.com/logo.png"
    assert team.region_id == TEST_REGION_ID

def test_team_create():
    """Test creating a new team"""
    team_data = {
        "name": "New Team",
        "logo_url": "https://example.com/new_team.png",
        "region_id": str(TEST_REGION_ID)
    }
    
    team = TeamCreate(**team_data)
    
    assert team.name == "New Team"
    assert str(team.logo_url) == "https://example.com/new_team.png"
    assert team.region_id == TEST_REGION_ID

def test_team_create_validation():
    """Test validation of team creation"""
    # Test name validation
    with pytest.raises(ValidationError):
        TeamCreate(name="", logo_url="https://example.com/logo.png")
    
    # Test URL validation
    with pytest.raises(ValidationError):
        TeamCreate(name="Invalid URL", logo_url="not-a-url")

def test_team_update():
    """Test updating a team with partial data"""
    update_data = {
        "name": "Updated Team Name",
        "elo_rating": 1200.0,
        "money_won": 5000.0
    }
    
    update = TeamUpdate(**update_data)
    
    assert update.name == "Updated Team Name"
    assert update.elo_rating == 1200.0
    assert update.money_won == 5000.0
    assert update.logo_url is None  # Not updated
    assert update.region_id is None  # Not updated

def test_team_in_db():
    """Test creating a team in the database"""
    created_at = datetime.now(timezone.utc)
    
    team_data = {
        "id": TEST_TEAM_ID,
        "name": "DB Team",
        "logo_url": "https://example.com/db_team.png",
        "region_id": str(TEST_REGION_ID),
        "current_rp": 2500.0,
        "elo_rating": 1500.0,
        "global_rank": 5,
        "leaderboard_tier": TeamTier.PROFESSIONAL,
        "created_at": created_at,
        "player_rank_score": 2400.0,
        "money_won": 10000.0
    }
    
    team = TeamInDB(**team_data)
    
    # Test required fields
    assert team.id == TEST_TEAM_ID
    assert team.name == "DB Team"
    assert str(team.logo_url) == "https://example.com/db_team.png"
    assert team.region_id == TEST_REGION_ID
    
    # Test default and computed fields
    assert team.current_rp == 2500.0
    assert team.elo_rating == 1500.0
    assert team.global_rank == 5
    assert team.leaderboard_tier == TeamTier.PROFESSIONAL
    assert team.created_at == created_at
    assert team.player_rank_score == 2400.0
    assert team.money_won == 10000.0

def test_team_with_players():
    """Test team schema with player information"""
    team_data = {
        "id": TEST_TEAM_ID,
        "name": "Team With Players",
        "created_at": datetime.now(timezone.utc),
        "current_rp": 3000.0,
        "elo_rating": 1600.0,
        "leaderboard_tier": TeamTier.ELITE,
        "player_rank_score": 2900.0,
        "money_won": 15000.0,
        "players": [
            {"id": 1, "gamertag": "Player1", "position": "PG"},
            {"id": 2, "gamertag": "Player2", "position": "SG"},
            {"id": 3, "gamertag": "Player3", "position": "SF"}
        ]
    }
    
    team = TeamWithPlayers(**team_data)
    
    assert team.name == "Team With Players"
    assert len(team.players) == 3
    assert team.players[0]["gamertag"] == "Player1"
    assert team.players[1]["position"] == "SG"

def test_team_with_stats():
    """Test team schema with statistics"""
    team_data = {
        "id": TEST_TEAM_ID,
        "name": "Team With Stats",
        "created_at": datetime.now(timezone.utc),
        "current_rp": 2800.0,
        "elo_rating": 1700.0,
        "leaderboard_tier": TeamTier.CHAMPION,
        "player_rank_score": 3000.0,
        "money_won": 50000.0,
        "total_wins": 25,
        "total_losses": 5,
        "win_percentage": 83.33,
        "current_streak": 8
    }
    
    team = TeamWithStats(**team_data)
    
    assert team.name == "Team With Stats"
    assert team.total_wins == 25
    assert team.total_losses == 5
    assert team.total_games == 30  # 25 + 5
    assert team.win_percentage == 83.33
    assert team.current_streak == 8
    assert team.leaderboard_tier == TeamTier.CHAMPION

def test_team_standing():
    """Test team standings"""
    standing_data = {
        "id": TEST_TEAM_ID,
        "name": "Top Team",
        "created_at": datetime.now(timezone.utc),
        "current_rp": 3500.0,
        "elo_rating": 2000.0,
        "leaderboard_tier": TeamTier.CHAMPION,
        "player_rank_score": 3400.0,
        "money_won": 100000.0,
        "rank": 1,
        "previous_rank": 2,
        "rp_change": 150.0,
        "event_wins": 10,
        "event_top3": 15,
        "event_top5": 20
    }
    
    standing = TeamStanding(**standing_data)
    
    assert standing.rank == 1
    assert standing.previous_rank == 2
    assert standing.rp_change == 150.0
    assert standing.event_wins == 10
    assert standing.event_top3 == 15
    assert standing.event_top5 == 20
    assert standing.name == "Top Team"

def test_team_tier_enum():
    """Test team tier enum values"""
    assert TeamTier.AMATEUR == "amateur"
    assert TeamTier.SEMI_PRO == "semi_pro"
    assert TeamTier.PROFESSIONAL == "professional"
    assert TeamTier.ELITE == "elite"
    assert TeamTier.CHAMPION == "champion"
    
    # Test enum iteration
    tiers = list(TeamTier)
    assert len(tiers) == 5
    assert TeamTier.AMATEUR in tiers
    assert TeamTier.CHAMPION in tiers
