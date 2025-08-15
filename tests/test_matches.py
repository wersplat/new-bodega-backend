"""
Tests for match schemas and models
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4
from pydantic import ValidationError, HttpUrl
from app.schemas.match import (
    MatchBase,
    MatchCreate,
    MatchUpdate,
    MatchInDB,
    MatchWithTeams,
    MatchWithDetails,
    MatchResult,
    PlayerMatchStats,
    MatchStats,
    MatchStatus,
    MatchStage
)

# Test data
TEST_MATCH_ID = uuid4()
TEST_TOURNAMENT_ID = uuid4()
TEST_LEAGUE_ID = uuid4()
TEST_TEAM_A_ID = uuid4()
TEST_TEAM_B_ID = uuid4()
TEST_WINNER_ID = uuid4()
TEST_PLAYER_ID = uuid4()

def test_match_base():
    """Test creating a base match"""
    scheduled_time = datetime.now(timezone.utc) + timedelta(days=1)
    
    match_data = {
        "tournament_id": str(TEST_TOURNAMENT_ID),
        "league_id": str(TEST_LEAGUE_ID),
        "team_a_id": str(TEST_TEAM_A_ID),
        "team_b_id": str(TEST_TEAM_B_ID),
        "stage": MatchStage.QUARTERFINALS,
        "game_number": 3,
        "scheduled_at": scheduled_time.isoformat()
    }
    
    match = MatchBase(**match_data)
    
    assert match.tournament_id == TEST_TOURNAMENT_ID
    assert match.league_id == TEST_LEAGUE_ID
    assert match.team_a_id == TEST_TEAM_A_ID
    assert match.team_b_id == TEST_TEAM_B_ID
    assert match.stage == MatchStage.QUARTERFINALS
    assert match.game_number == 3
    assert match.scheduled_at == scheduled_time

def test_match_create():
    """Test creating a new match"""
    match_data = {
        "tournament_id": str(TEST_TOURNAMENT_ID),
        "league_id": str(TEST_LEAGUE_ID),
        "team_a_id": str(TEST_TEAM_A_ID),
        "team_b_id": str(TEST_TEAM_B_ID),
        "team_a_name": "Team Alpha",
        "team_b_name": "Team Beta",
        "stage": MatchStage.GROUP,
        "game_number": 1
    }
    
    match = MatchCreate(**match_data)
    
    assert match.team_a_name == "Team Alpha"
    assert match.team_b_name == "Team Beta"
    assert match.stage == MatchStage.GROUP
    assert match.game_number == 1

def test_match_create_validation():
    """Test validation of match creation"""
    # Test same team for both sides
    with pytest.raises(ValidationError):
        MatchCreate(
            tournament_id=str(TEST_TOURNAMENT_ID),
            league_id=str(TEST_LEAGUE_ID),
            team_a_id=str(TEST_TEAM_A_ID),
            team_b_id=str(TEST_TEAM_A_ID),  # Same as team_a_id
            team_a_name="Team A",
            team_b_name="Team A"
        )
    
    # Test invalid game number
    with pytest.raises(ValidationError):
        MatchCreate(
            tournament_id=str(TEST_TOURNAMENT_ID),
            league_id=str(TEST_LEAGUE_ID),
            team_a_id=str(TEST_TEAM_A_ID),
            team_b_id=str(TEST_TEAM_B_ID),
            team_a_name="Team A",
            team_b_name="Team B",
            game_number=0  # Invalid, must be >= 1
        )

def test_match_update():
    """Test updating a match with partial data"""
    played_at = datetime.now(timezone.utc)
    
    update_data = {
        "status": MatchStatus.COMPLETED,
        "score_a": 21,
        "score_b": 19,
        "winner_id": str(TEST_TEAM_A_ID),
        "played_at": played_at.isoformat(),
        "boxscore_url": "https://example.com/boxscore/123"
    }
    
    update = MatchUpdate(**update_data)
    
    assert update.status == MatchStatus.COMPLETED
    assert update.score_a == 21
    assert update.score_b == 19
    assert update.winner_id == TEST_TEAM_A_ID
    assert update.played_at == played_at
    assert str(update.boxscore_url) == "https://example.com/boxscore/123"

def test_match_in_db():
    """Test creating a match in the database"""
    created_at = datetime.now(timezone.utc)
    updated_at = datetime.now(timezone.utc)
    played_at = datetime.now(timezone.utc)
    
    match_data = {
        "id": TEST_MATCH_ID,
        "tournament_id": str(TEST_TOURNAMENT_ID),
        "league_id": str(TEST_LEAGUE_ID),
        "team_a_id": str(TEST_TEAM_A_ID),
        "team_b_id": str(TEST_TEAM_B_ID),
        "winner_id": str(TEST_TEAM_A_ID),
        "score_a": 21,
        "score_b": 18,
        "status": MatchStatus.COMPLETED,
        "stage": MatchStage.SEMIFINALS,
        "game_number": 1,
        "played_at": played_at.isoformat(),
        "boxscore_url": "https://example.com/boxscore/456",
        "team_a_name": "Team Alpha",
        "team_b_name": "Team Beta",
        "winner_name": "Team Alpha",
        "created_at": created_at.isoformat(),
        "updated_at": updated_at.isoformat(),
        "scheduled_at": (played_at - timedelta(hours=2)).isoformat()
    }
    
    match = MatchInDB(**match_data)
    
    # Test required fields
    assert match.id == TEST_MATCH_ID
    assert match.tournament_id == TEST_TOURNAMENT_ID
    assert match.team_a_id == TEST_TEAM_A_ID
    assert match.team_b_id == TEST_TEAM_B_ID
    assert match.winner_id == TEST_TEAM_A_ID
    
    # Test scores and status
    assert match.score_a == 21
    assert match.score_b == 18
    assert match.status == MatchStatus.COMPLETED
    
    # Test metadata
    assert match.team_a_name == "Team Alpha"
    assert match.team_b_name == "Team Beta"
    assert match.winner_name == "Team Alpha"
    assert match.created_at == created_at
    assert match.updated_at == updated_at

def test_match_with_teams():
    """Test match schema with team information"""
    match_data = {
        "id": TEST_MATCH_ID,
        "tournament_id": str(TEST_TOURNAMENT_ID),
        "league_id": str(TEST_LEAGUE_ID),
        "team_a_id": str(TEST_TEAM_A_ID),
        "team_b_id": str(TEST_TEAM_B_ID),
        "team_a_name": "Team Alpha",
        "team_b_name": "Team Beta",
        "status": MatchStatus.SCHEDULED,
        "stage": MatchStage.GROUP,
        "game_number": 1,
        "created_at": datetime.now(timezone.utc),
        "team_a": {"id": str(TEST_TEAM_A_ID), "name": "Team Alpha", "logo_url": "https://example.com/alpha.png"},
        "team_b": {"id": str(TEST_TEAM_B_ID), "name": "Team Beta", "logo_url": "https://example.com/beta.png"}
    }
    
    match = MatchWithTeams(**match_data)
    
    assert match.team_a["name"] == "Team Alpha"
    assert match.team_b["name"] == "Team Beta"
    assert match.status == MatchStatus.SCHEDULED

def test_match_with_details():
    """Test match schema with team and player details"""
    match_data = {
        "id": TEST_MATCH_ID,
        "tournament_id": str(TEST_TOURNAMENT_ID),
        "league_id": str(TEST_LEAGUE_ID),
        "team_a_id": str(TEST_TEAM_A_ID),
        "team_b_id": str(TEST_TEAM_B_ID),
        "team_a_name": "Team Alpha",
        "team_b_name": "Team Beta",
        "status": MatchStatus.SCHEDULED,
        "stage": MatchStage.FINALS,
        "game_number": 1,
        "created_at": datetime.now(timezone.utc),
        "team_a_players": [
            {"id": str(uuid4()), "gamertag": "Player1", "position": "PG"},
            {"id": str(uuid4()), "gamertag": "Player2", "position": "SG"}
        ],
        "team_b_players": [
            {"id": str(uuid4()), "gamertag": "Player3", "position": "SF"},
            {"id": str(uuid4()), "gamertag": "Player4", "position": "PF"}
        ],
        "tournament": {"id": str(TEST_TOURNAMENT_ID), "name": "Championship Finals"}
    }
    
    match = MatchWithDetails(**match_data)
    
    assert len(match.team_a_players) == 2
    assert len(match.team_b_players) == 2
    assert match.team_a_players[0]["position"] == "PG"
    assert match.tournament["name"] == "Championship Finals"
    assert match.stage == MatchStage.FINALS

def test_match_result():
    """Test match result submission"""
    result_data = {
        "score_a": 21,
        "score_b": 19,
        "winner_id": str(TEST_TEAM_A_ID),
        "boxscore_url": "https://example.com/boxscore/789"
    }
    
    result = MatchResult(**result_data)
    
    assert result.score_a == 21
    assert result.score_b == 19
    assert result.winner_id == TEST_TEAM_A_ID
    assert str(result.boxscore_url) == "https://example.com/boxscore/789"

def test_player_match_stats():
    """Test player match statistics"""
    stats_data = {
        "player_id": str(TEST_PLAYER_ID),
        "team_id": str(TEST_TEAM_A_ID),
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
        "minutes_played": 36
    }
    
    stats = PlayerMatchStats(**stats_data)
    
    assert stats.player_id == TEST_PLAYER_ID
    assert stats.team_id == TEST_TEAM_A_ID
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

def test_match_stats():
    """Test match statistics submission"""
    player1_id = uuid4()
    player2_id = uuid4()
    
    stats_data = {
        "match_id": str(TEST_MATCH_ID),
        "stats": [
            {
                "player_id": str(player1_id),
                "team_id": str(TEST_TEAM_A_ID),
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
                "minutes_played": 36
            },
            {
                "player_id": str(player2_id),
                "team_id": str(TEST_TEAM_A_ID),
                "points": 18,
                "assists": 12,
                "rebounds": 5,
                "steals": 3,
                "blocks": 0,
                "turnovers": 2,
                "fouls": 1,
                "fgm": 7,
                "fga": 14,
                "three_points_made": 4,
                "three_points_attempted": 8,
                "ftm": 0,
                "fta": 0,
                "plus_minus": 15,
                "minutes_played": 38
            }
        ]
    }
    
    match_stats = MatchStats(**stats_data)
    
    assert match_stats.match_id == TEST_MATCH_ID
    assert len(match_stats.stats) == 2
    assert match_stats.stats[0].player_id == player1_id
    assert match_stats.stats[1].player_id == player2_id
    assert match_stats.stats[0].points == 25
    assert match_stats.stats[1].assists == 12

def test_match_stage_enum():
    """Test match stage enum values"""
    assert MatchStage.GROUP == "group"
    assert MatchStage.ROUND_OF_32 == "round_of_32"
    assert MatchStage.ROUND_OF_16 == "round_of_16"
    assert MatchStage.QUARTERFINALS == "quarterfinals"
    assert MatchStage.SEMIFINALS == "semifinals"
    assert MatchStage.FINALS == "finals"
    assert MatchStage.THIRD_PLACE == "third_place"
    assert MatchStage.EXHIBITION == "exhibition"
    
    # Test enum iteration
    stages = list(MatchStage)
    assert len(stages) == 8
    assert MatchStage.GROUP in stages
    assert MatchStage.FINALS in stages
