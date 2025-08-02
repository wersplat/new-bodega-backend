"""
Test script for Player Stats API endpoints
"""

import os
import sys
import pytest
from datetime import datetime, timezone
from uuid import uuid4
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

# Import FastAPI test client
from fastapi.testclient import TestClient
from main import app

# Create test client
client = TestClient(app)

# Test data
TEST_PLAYER = {
    "gamertag": f"testplayer_{uuid4().hex[:8]}",
    "region_id": str(uuid4()),
    "player_rp": 1000.0,
}

TEST_TEAM = {
    "name": f"Test Team {uuid4().hex[:8]}",
    "logo_url": "https://example.com/logo.png",
    "region_id": str(uuid4()),
}

TEST_MATCH = {
    "team_a_id": None,  # Will be set after creating test team
    "team_b_id": None,  # Will be set after creating test team
    "team_a_name": "Team A",
    "team_b_name": "Team B",
    "score_a": 10,
    "score_b": 8,
    "stage": "group",
    "round": 1,
    "status": "completed",
    "start_time": datetime.now(timezone.utc).isoformat(),
    "best_of": 3,
    "region_id": str(uuid4()),
    "event_id": str(uuid4()),
}

TEST_PLAYER_STATS = {
    "player_id": None,  # Will be set after creating test player
    "match_id": None,   # Will be set after creating test match
    "team_id": None,    # Will be set after creating test team
    "points": 25,
    "assists": 5,
    "rebounds": 10,
    "steals": 2,
    "blocks": 1,
    "turnovers": 3,
    "field_goals_made": 10,
    "field_goals_attempted": 15,
    "three_points_made": 3,
    "three_points_attempted": 6,
    "free_throws_made": 2,
    "free_throws_attempted": 3,
    "minutes_played": 25.5,
    "plus_minus": 12,
    "fouls": 2,
    "offensive_rebounds": 3,
    "defensive_rebounds": 7,
    "efficiency": 30.5,
}

# Global variables to store created IDs
created_player_id = None
created_team_id = None
created_match_id = None
created_stats_id = None


def create_test_player(player_data: Dict[str, Any]) -> Optional[str]:
    """Helper function to create a test player"""
    response = client.post(
        "/api/players/",
        json=player_data,
        headers={"Content-Type": "application/json"}
    )
    if response.status_code == 201:
        return response.json()["id"]
    return None


def create_test_team(team_data: Dict[str, Any]) -> Optional[str]:
    """Helper function to create a test team"""
    response = client.post(
        "/api/teams/",
        json=team_data,
        headers={"Content-Type": "application/json"}
    )
    if response.status_code == 201:
        return response.json()["id"]
    return None


def create_test_match(match_data: Dict[str, Any]) -> Optional[str]:
    """Helper function to create a test match"""
    # First create teams if they don't exist
    if not match_data.get("team_a_id"):
        team_a_data = {
            "name": match_data.get("team_a_name", "Team A"),
            "region_id": str(uuid4()),
        }
        match_data["team_a_id"] = create_test_team(team_a_data)
    
    if not match_data.get("team_b_id"):
        team_b_data = {
            "name": match_data.get("team_b_name", "Team B"),
            "region_id": str(uuid4()),
        }
        match_data["team_b_id"] = create_test_team(team_b_data)
    
    # Create the match
    response = client.post(
        "/api/matches/",
        json=match_data,
        headers={"Content-Type": "application/json"}
    )
    if response.status_code == 201:
        return response.json()["id"]
    return None


def test_create_player_stats():
    """Test creating new player statistics"""
    global created_player_id, created_team_id, created_match_id, created_stats_id
    
    # First, create test player, team, and match
    created_player_id = create_test_player(TEST_PLAYER)
    created_team_id = create_test_team(TEST_TEAM)
    
    # Update match data with team ID
    match_data = TEST_MATCH.copy()
    match_data["team_a_id"] = created_team_id
    match_data["team_b_id"] = str(uuid4())  # Create a different team for team B
    
    created_match_id = create_test_match(match_data)
    
    if not all([created_player_id, created_team_id, created_match_id]):
        pytest.skip("Failed to create test data (player, team, or match)")
    
    # Update stats data with IDs
    stats_data = TEST_PLAYER_STATS.copy()
    stats_data["player_id"] = created_player_id
    stats_data["match_id"] = created_match_id
    stats_data["team_id"] = created_team_id
    
    # Create player stats
    response = client.post(
        "/api/player-stats/",
        json=stats_data,
        headers={"Content-Type": "application/json"}
    )
    
    # Check response
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}. Response: {response.text}"
    data = response.json()
    assert "id" in data, f"Response missing 'id' field. Response: {data}"
    
    # Save the created stats ID for subsequent tests
    created_stats_id = data["id"]
    
    # Verify the returned data matches what we sent
    for key, value in stats_data.items():
        if key in ["points", "assists", "rebounds", "steals", "blocks", "turnovers"]:
            assert data[key] == value, f"Mismatch in {key}. Expected {value}, got {data.get(key)}"
    
    # Check that performance score (ps) was calculated
    assert "ps" in data, "Response missing 'ps' (performance score) field"
    assert isinstance(data["ps"], (int, float)), "Performance score should be a number"
    assert data["ps"] >= 0, "Performance score should not be negative"


def test_get_player_stats():
    """Test retrieving player statistics by ID"""
    if not created_stats_id:
        pytest.skip("No stats ID available from previous test")
    
    # Get the stats we just created
    response = client.get(f"/api/player-stats/{created_stats_id}")
    
    # Check response
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    
    # Verify the returned data matches what we sent
    assert data["id"] == created_stats_id, f"Stats ID mismatch. Expected {created_stats_id}, got {data.get('id')}"
    assert data["player_id"] == created_player_id, f"Player ID mismatch. Expected {created_player_id}, got {data.get('player_id')}"
    assert data["match_id"] == created_match_id, f"Match ID mismatch. Expected {created_match_id}, got {data.get('match_id')}"
    assert data["team_id"] == created_team_id, f"Team ID mismatch. Expected {created_team_id}, got {data.get('team_id')}"
    
    # Check that related data is included
    assert "player" in data, "Response missing 'player' field"
    assert "match" in data, "Response missing 'match' field"
    assert "team" in data, "Response missing 'team' field"


def test_update_player_stats():
    """Test updating player statistics"""
    if not created_stats_id:
        pytest.skip("No stats ID available from previous test")
    
    # Update the stats
    update_data = {
        "points": 30,
        "assists": 8,
        "rebounds": 12,
        "minutes_played": 28.5,
        "notes": "Updated test stats"
    }
    
    response = client.put(
        f"/api/player-stats/{created_stats_id}",
        json=update_data,
        headers={"Content-Type": "application/json"}
    )
    
    # Check response
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    
    # Verify the updated fields
    assert data["points"] == update_data["points"], f"Points not updated. Expected {update_data['points']}, got {data.get('points')}"
    assert data["assists"] == update_data["assists"], f"Assists not updated. Expected {update_data['assists']}, got {data.get('assists')}"
    assert data["rebounds"] == update_data["rebounds"], f"Rebounds not updated. Expected {update_data['rebounds']}, got {data.get('rebounds')}"
    assert data["minutes_played"] == update_data["minutes_played"], f"Minutes played not updated. Expected {update_data['minutes_played']}, got {data.get('minutes_played')}"
    assert data.get("notes") == update_data["notes"], f"Notes not updated. Expected {update_data['notes']}, got {data.get('notes')}"
    
    # Check that performance score was recalculated
    assert "ps" in data, "Response missing 'ps' (performance score) field after update"


def test_list_player_stats():
    """Test listing player statistics with filtering"""
    # Get all player stats
    response = client.get("/api/player-stats/")
    
    # Check response
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    
    # Should be a list
    assert isinstance(data, list), f"Expected a list of player stats, got {type(data)}"
    
    # Our test stats should be in the list
    stats_ids = [stats["id"] for stats in data if "id" in stats]
    if created_stats_id:
        assert created_stats_id in stats_ids, f"Created stats ID {created_stats_id} not found in stats list"


def test_get_player_stats_history():
    """Test getting player statistics history for a specific player"""
    if not created_player_id:
        pytest.skip("No player ID available from previous test")
    
    # Get player stats history
    response = client.get(f"/api/player-stats/player/{created_player_id}/history")
    
    # Check response
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    
    # Should be a list
    assert isinstance(data, list), f"Expected a list of player stats, got {type(data)}"
    
    # Our test stats should be in the history
    stats_ids = [stats["id"] for stats in data if "id" in stats]
    if created_stats_id:
        assert created_stats_id in stats_ids, f"Created stats ID {created_stats_id} not found in player history"


def test_get_team_stats_for_match():
    """Test getting player statistics for a specific team in a match"""
    if not created_match_id or not created_team_id:
        pytest.skip("Match ID or Team ID not available from previous test")
    
    # Get team stats for the match
    response = client.get(f"/api/player-stats/match/{created_match_id}/team/{created_team_id}")
    
    # Check response
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    
    # Should be a list
    assert isinstance(data, list), f"Expected a list of player stats, got {type(data)}"
    
    # Our test stats should be in the list
    stats_ids = [stats["id"] for stats in data if "id" in stats]
    if created_stats_id:
        assert created_stats_id in stats_ids, f"Created stats ID {created_stats_id} not found in team match stats"


def test_delete_player_stats():
    """Test deleting player statistics"""
    global created_stats_id, created_player_id, created_team_id, created_match_id
    
    if not created_stats_id:
        pytest.skip("No stats ID available from previous test")
    
    # Delete the stats
    response = client.delete(f"/api/player-stats/{created_stats_id}")
    
    # Check response
    assert response.status_code == 204, f"Expected status code 204, got {response.status_code}. Response: {response.text}"
    
    # Verify the stats no longer exist
    response = client.get(f"/api/player-stats/{created_stats_id}")
    assert response.status_code == 404, f"Expected status code 404 after deletion, got {response.status_code}"
    
    # Clean up test data
    if created_match_id:
        client.delete(f"/api/matches/{created_match_id}")
    if created_team_id:
        client.delete(f"/api/teams/{created_team_id}")
    if created_player_id:
        client.delete(f"/api/players/{created_player_id}")
    
    # Reset global variables
    created_stats_id = None
    created_player_id = None
    created_team_id = None
    created_match_id = None
