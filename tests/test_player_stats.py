"""
Tests for player statistics schemas and models
"""

import pytest
from datetime import datetime, timezone
from uuid import UUID, uuid4
from pydantic import ValidationError
from app.schemas.player_stats import (
    PlayerStatsBase,
    PlayerStatsCreate,
    PlayerStatsUpdate,
    PlayerStatsInDB,
    PlayerGameAverages,
    PlayerSeasonStats,
    PlayerGameLog
)

# Test data
TEST_PLAYER_ID = uuid4()
TEST_MATCH_ID = uuid4()
TEST_TEAM_ID = uuid4()

def test_player_stats_base():
    """Test creating base player statistics"""
    stats_data = {
        "player_id": str(TEST_PLAYER_ID),
        "match_id": str(TEST_MATCH_ID),
        "team_id": str(TEST_TEAM_ID),
        "points": 25,
        "assists": 8,
        "rebounds": 7,
        "steals": 2,
        "blocks": 1,
        "turnovers": 3,
        "fouls": 2,
        "fgm": 10,
        "fga": 18,
        "three_points_made": 3,
        "three_points_attempted": 7,
        "ftm": 2,
        "fta": 2,
        "plus_minus": 12,
        "minutes_played": 36,
        "ps": 32.5
    }
    
    stats = PlayerStatsBase(**stats_data)
    
    # Test required fields
    assert stats.player_id == TEST_PLAYER_ID
    assert stats.match_id == TEST_MATCH_ID
    assert stats.team_id == TEST_TEAM_ID
    
    # Test statistics
    assert stats.points == 25
    assert stats.assists == 8
    assert stats.rebounds == 7
    assert stats.steals == 2
    assert stats.blocks == 1
    assert stats.turnovers == 3
    assert stats.fouls == 2
    assert stats.fgm == 10
    assert stats.fga == 18
    assert stats.three_points_made == 3
    assert stats.three_points_attempted == 7
    assert stats.ftm == 2
    assert stats.fta == 2
    assert stats.plus_minus == 12
    assert stats.minutes_played == 36
    assert stats.ps == 32.5

def test_player_stats_validation():
    """Test validation of player statistics"""
    # Test field goals made > attempted
    with pytest.raises(ValueError, match="Field goals attempted must be >= field goals made"):
        PlayerStatsBase(
            player_id=TEST_PLAYER_ID,
            match_id=TEST_MATCH_ID,
            team_id=TEST_TEAM_ID,
            fgm=10,
            fga=8  # Less than fgm
        )
    
    # Test 3-pointers made > attempted
    with pytest.raises(ValueError, match="3-point attempts must be >= 3-pointers made"):
        PlayerStatsBase(
            player_id=TEST_PLAYER_ID,
            match_id=TEST_MATCH_ID,
            team_id=TEST_TEAM_ID,
            three_points_made=5,
            three_points_attempted=4  # Less than made
        )
    
    # Test free throws made > attempted
    with pytest.raises(ValueError, match="Free throw attempts must be >= free throws made"):
        PlayerStatsBase(
            player_id=TEST_PLAYER_ID,
            match_id=TEST_MATCH_ID,
            team_id=TEST_TEAM_ID,
            ftm=3,
            fta=2  # Less than made
        )
    
    # Test minutes played > 48
    with pytest.raises(ValueError, match="Input should be less than or equal to 48"):
        PlayerStatsBase(
            player_id=TEST_PLAYER_ID,
            match_id=TEST_MATCH_ID,
            team_id=TEST_TEAM_ID,
            minutes_played=49  # More than 48
        )

def test_player_stats_create():
    """Test creating player statistics with player name"""
    stats_data = {
        "player_id": str(TEST_PLAYER_ID),
        "match_id": str(TEST_MATCH_ID),
        "team_id": str(TEST_TEAM_ID),
        "points": 30,
        "player_name": "Test Player"
    }
    
    stats = PlayerStatsCreate(**stats_data)
    
    assert stats.player_id == TEST_PLAYER_ID
    assert stats.player_name == "Test Player"
    assert stats.points == 30

def test_player_stats_update():
    """Test updating player statistics with partial data"""
    update_data = {
        "points": 35,
        "assists": 10,
        "rebounds": 5,
        "minutes_played": 40
    }
    
    update = PlayerStatsUpdate(**update_data)
    
    assert update.points == 35
    assert update.assists == 10
    assert update.rebounds == 5
    assert update.minutes_played == 40
    assert update.steals is None  # Not updated

def test_player_stats_in_db():
    """Test player statistics as stored in the database"""
    created_at = datetime.now(timezone.utc)
    updated_at = datetime.now(timezone.utc)
    
    stats_data = {
        "id": 1,
        "player_id": str(TEST_PLAYER_ID),
        "match_id": str(TEST_MATCH_ID),
        "team_id": str(TEST_TEAM_ID),
        "points": 28,
        "assists": 7,
        "rebounds": 6,
        "steals": 3,
        "blocks": 2,
        "turnovers": 2,
        "fouls": 1,
        "fgm": 11,
        "fga": 19,
        "three_points_made": 4,
        "three_points_attempted": 8,
        "ftm": 2,
        "fta": 2,
        "plus_minus": 15,
        "minutes_played": 38,
        "ps": 35.2,
        "player_name": "DB Player",
        "created_at": created_at,
        "updated_at": updated_at
    }
    
    stats = PlayerStatsInDB(**stats_data)
    
    assert stats.id == 1
    assert stats.player_id == TEST_PLAYER_ID
    assert stats.match_id == TEST_MATCH_ID
    assert stats.team_id == TEST_TEAM_ID
    assert stats.points == 28
    assert stats.player_name == "DB Player"
    assert stats.created_at == created_at
    assert stats.updated_at == updated_at

def test_player_game_averages():
    """Test player game averages calculation"""
    averages = PlayerGameAverages(
        games_played=10,
        points=22.5,
        assists=6.8,
        rebounds=5.5,
        steals=1.8,
        blocks=0.9,
        turnovers=2.5,
        field_goal_pct=48.7,
        three_point_pct=39.2,
        free_throw_pct=85.3,
        minutes_per_game=34.5,
        plus_minus=5.2,
        double_doubles=3,
        triple_doubles=1
    )
    
    assert averages.games_played == 10
    assert averages.points == 22.5
    assert averages.assists == 6.8
    assert averages.rebounds == 5.5
    assert averages.steals == 1.8
    assert averages.blocks == 0.9
    assert averages.turnovers == 2.5
    assert averages.field_goal_pct == 48.7
    assert averages.three_point_pct == 39.2
    assert averages.free_throw_pct == 85.3
    assert averages.minutes_per_game == 34.5
    assert averages.plus_minus == 5.2
    assert averages.double_doubles == 3
    assert averages.triple_doubles == 1

def test_player_season_stats():
    """Test player season statistics with calculated properties"""
    season_stats = PlayerSeasonStats(
        player_id=TEST_PLAYER_ID,
        player_name="Season Leader",
        team_id=TEST_TEAM_ID,
        team_name="Top Team",
        games_played=20,
        games_started=20,
        minutes_played=800,
        total_points=500,
        total_assists=150,
        total_rebounds=200,
        total_steals=40,
        total_blocks=30,
        total_turnovers=60,
        total_fgm=200,
        total_fga=400,
        total_3pm=50,
        total_3pa=150,
        total_ftm=50,
        total_fta=60,
        total_plus_minus=100,
        double_doubles=5,
        triple_doubles=1
    )
    
    # Test basic stats
    assert season_stats.player_name == "Season Leader"
    assert season_stats.team_name == "Top Team"
    assert season_stats.games_played == 20
    
    # Test computed per-game stats
    assert season_stats.points_per_game == 25.0  # 500 / 20
    assert season_stats.assists_per_game == 7.5  # 150 / 20
    assert season_stats.rebounds_per_game == 10.0  # 200 / 20
    assert season_stats.steals_per_game == 2.0  # 40 / 20
    assert season_stats.blocks_per_game == 1.5  # 30 / 20
    assert season_stats.turnovers_per_game == 3.0  # 60 / 20
    assert season_stats.minutes_per_game == 40.0  # 800 / 20
    assert season_stats.plus_minus_per_game == 5.0  # 100 / 20
    
    # Test computed percentages
    assert season_stats.field_goal_pct == 50.0  # (200/400)*100
    assert season_stats.three_point_pct == pytest.approx(33.33, 0.1)  # (50/150)*100
    assert season_stats.free_throw_pct == pytest.approx(83.33, 0.1)  # (50/60)*100
    
    # Test nested averages
    assert season_stats.averages.points == 25.0
    assert season_stats.averages.assists == 7.5
    assert season_stats.averages.rebounds == 10.0
    assert season_stats.averages.steals == 2.0
    assert season_stats.averages.blocks == 1.5
    assert season_stats.averages.turnovers == 3.0
    assert season_stats.averages.minutes_per_game == 40.0
    assert season_stats.averages.plus_minus == 5.0
    assert season_stats.averages.field_goal_pct == 50.0
    assert season_stats.averages.three_point_pct == pytest.approx(33.33, 0.1)
    assert season_stats.averages.free_throw_pct == pytest.approx(83.33, 0.1)
    assert season_stats.averages.double_doubles == 5
    assert season_stats.averages.triple_doubles == 1

def test_player_game_log():
    """Test player game log entry"""
    game_date = datetime.now(timezone.utc)
    opponent_team_id = uuid4()
    
    game_log = PlayerGameLog(
        match_id=TEST_MATCH_ID,
        match_date=game_date,
        opponent_team_id=opponent_team_id,
        opponent_team_name="Rival Team",
        is_home=True,
        minutes_played=42,
        points=32,
        rebounds=10,
        assists=8,
        steals=2,
        blocks=1,
        turnovers=3,
        fgm=12,
        fga=20,
        three_points_made=4,
        three_points_attempted=8,
        ftm=4,
        fta=5,
        plus_minus=15,
        result="W",
        score="115-100"
    )
    
    # Test basic fields
    assert game_log.match_id == TEST_MATCH_ID
    assert game_log.match_date == game_date
    assert game_log.opponent_team_id == opponent_team_id
    assert game_log.opponent_team_name == "Rival Team"
    assert game_log.is_home is True
    assert game_log.result == "W"
    assert game_log.score == "115-100"
    
    # Test statistics
    assert game_log.points == 32
    assert game_log.rebounds == 10
    assert game_log.assists == 8
    assert game_log.steals == 2
    assert game_log.blocks == 1
    assert game_log.turnovers == 3
    
    # Test calculated percentages
    assert game_log.field_goal_pct == 60.0  # (12/20)*100
    assert game_log.three_point_pct == 50.0  # (4/8)*100
    assert game_log.free_throw_pct == 80.0  # (4/5)*100
