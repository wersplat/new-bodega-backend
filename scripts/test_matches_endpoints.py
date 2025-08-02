"""
Test script for Matches API endpoints
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
TEST_TEAM_A = {
    "name": f"Team A {uuid4().hex[:8]}",
    "logo_url": "https://example.com/logo-a.png",
    "region_id": str(uuid4()),
}

TEST_TEAM_B = {
    "name": f"Team B {uuid4().hex[:8]}",
    "logo_url": "https://example.com/logo-b.png",
    "region_id": str(uuid4()),
}

TEST_MATCH = {
    "team_a_id": None,  # Will be set after creating test teams
    "team_b_id": None,  # Will be set after creating test teams
    "team_a_name": "",  # Will be set by the API
    "team_b_name": "",  # Will be set by the API
    "score_a": 10,
    "score_b": 8,
    "stage": "group",
    "round": 1,
    "status": "completed",
    "start_time": datetime.now(timezone.utc).isoformat(),
    "best_of": 3,
    "region_id": str(uuid4()),
    "event_id": str(uuid4()),  # Would be a valid event ID in a real test
}

# Global variables to store created IDs
created_match_id = None
created_team_a_id = None
created_team_b_id = None


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


def test_create_match():
    """Test creating a new match"""
    global created_match_id, created_team_a_id, created_team_b_id
    
    # First, create test teams
    created_team_a_id = create_test_team(TEST_TEAM_A)
    created_team_b_id = create_test_team(TEST_TEAM_B)
    
    if not created_team_a_id or not created_team_b_id:
        pytest.skip("Failed to create test teams")
    
    # Update match data with team IDs
    match_data = TEST_MATCH.copy()
    match_data["team_a_id"] = created_team_a_id
    match_data["team_b_id"] = created_team_b_id
    
    # Create a new match
    response = client.post(
        "/api/matches/",
        json=match_data,
        headers={"Content-Type": "application/json"}
    )
    
    # Check response
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}. Response: {response.text}"
    data = response.json()
    assert "id" in data, f"Response missing 'id' field. Response: {data}"
    
    # Save the created match ID for subsequent tests
    created_match_id = data["id"]
    
    # Verify the returned data matches what we sent
    for key, value in match_data.items():
        if key in ["team_a_id", "team_b_id", "score_a", "score_b"]:
            assert str(data[key]) == str(value), f"Mismatch in {key}. Expected {value}, got {data.get(key)}"
    
    # Check that winner is set correctly (team_a should win based on scores)
    assert data["winner_id"] == created_team_a_id, f"Winner not set correctly. Expected {created_team_a_id}, got {data.get('winner_id')}"


def test_get_match():
    """Test retrieving a match by ID"""
    if not created_match_id:
        pytest.skip("No match ID available from previous test")
    
    # Get the match we just created
    response = client.get(f"/api/matches/{created_match_id}")
    
    # Check response
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    
    # Verify the returned data matches what we sent
    assert data["id"] == created_match_id, f"Match ID mismatch. Expected {created_match_id}, got {data.get('id')}"
    assert data["team_a_id"] == created_team_a_id, f"Team A ID mismatch. Expected {created_team_a_id}, got {data.get('team_a_id')}"
    assert data["team_b_id"] == created_team_b_id, f"Team B ID mismatch. Expected {created_team_b_id}, got {data.get('team_b_id')}"
    
    # Check that player_stats list exists (should be empty for a new match)
    assert "player_stats" in data, "Response missing 'player_stats' field"
    assert isinstance(data["player_stats"], list), "player_stats field should be a list"


def test_update_match():
    """Test updating a match"""
    if not created_match_id:
        pytest.skip("No match ID available from previous test")
    
    # Update the match
    update_data = {
        "score_a": 12,
        "score_b": 10,
        "status": "completed",
        "notes": "Updated test match"
    }
    
    response = client.put(
        f"/api/matches/{created_match_id}",
        json=update_data,
        headers={"Content-Type": "application/json"}
    )
    
    # Check response
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    
    # Verify the updated fields
    assert data["score_a"] == update_data["score_a"], f"Score A not updated. Expected {update_data['score_a']}, got {data.get('score_a')}"
    assert data["score_b"] == update_data["score_b"], f"Score B not updated. Expected {update_data['score_b']}, got {data.get('score_b')}"
    assert data["status"] == update_data["status"], f"Status not updated. Expected {update_data['status']}, got {data.get('status')}"
    assert data.get("notes") == update_data["notes"], f"Notes not updated. Expected {update_data['notes']}, got {data.get('notes')}"


def test_list_matches():
    """Test listing matches with filtering"""
    # Get all matches
    response = client.get("/api/matches/")
    
    # Check response
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    
    # Should be a list
    assert isinstance(data, list), f"Expected a list of matches, got {type(data)}"
    
    # Our test match should be in the list
    match_ids = [match["id"] for match in data if "id" in match]
    if created_match_id:
        assert created_match_id in match_ids, f"Created match ID {created_match_id} not found in matches list"


def test_get_team_matches():
    """Test getting matches for a specific team"""
    if not created_team_a_id:
        pytest.skip("No team ID available from previous test")
    
    # Get matches for team A
    response = client.get(f"/api/matches/team/{created_team_a_id}")
    
    # Check response
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    
    # Should be a list
    assert isinstance(data, list), f"Expected a list of matches, got {type(data)}"
    
    # Our test match should be in the list
    match_ids = [match["id"] for match in data if "id" in match]
    if created_match_id:
        assert created_match_id in match_ids, f"Created match ID {created_match_id} not found in team matches"


def test_delete_match():
    """Test deleting a match"""
    global created_match_id
    
    if not created_match_id:
        pytest.skip("No match ID available from previous test")
    
    # Delete the match
    response = client.delete(f"/api/matches/{created_match_id}")
    
    # Check response
    assert response.status_code == 204, f"Expected status code 204, got {response.status_code}. Response: {response.text}"
    
    # Verify the match no longer exists
    response = client.get(f"/api/matches/{created_match_id}")
    assert response.status_code == 404, f"Expected status code 404 after deletion, got {response.status_code}"
    
    # Clean up test teams
    if created_team_a_id:
        client.delete(f"/api/teams/{created_team_a_id}")
    if created_team_b_id:
        client.delete(f"/api/teams/{created_team_b_id}")
    
    # Reset the global variable
    created_match_id = None
