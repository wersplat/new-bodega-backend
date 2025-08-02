"""
Test script for Teams API endpoints
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
TEST_TEAM = {
    "name": f"Test Team {uuid4().hex[:8]}",
    "logo_url": "https://example.com/logo.png",
    "region_id": str(uuid4()),  # This would be a valid region ID in a real test
}

# Global variable to store created team ID for subsequent tests
created_team_id = None


def test_create_team():
    """Test creating a new team"""
    global created_team_id
    
    # Create a new team
    response = client.post(
        "/api/teams/",
        json=TEST_TEAM,
        headers={"Content-Type": "application/json"}
    )
    
    # Check response
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}. Response: {response.text}"
    data = response.json()
    assert "id" in data, f"Response missing 'id' field. Response: {data}"
    
    # Save the created team ID for subsequent tests
    created_team_id = data["id"]
    
    # Verify the returned data matches what we sent
    for key, value in TEST_TEAM.items():
        assert data[key] == value, f"Mismatch in {key}. Expected {value}, got {data.get(key)}"


def test_get_team():
    """Test retrieving a team by ID"""
    if not created_team_id:
        pytest.skip("No team ID available from previous test")
    
    # Get the team we just created
    response = client.get(f"/api/teams/{created_team_id}")
    
    # Check response
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    
    # Verify the returned data matches what we sent
    for key, value in TEST_TEAM.items():
        assert data[key] == value, f"Mismatch in {key}. Expected {value}, got {data.get(key)}"
    
    # Check that players list exists (should be empty for a new team)
    assert "players" in data, "Response missing 'players' field"
    assert isinstance(data["players"], list), "Players field should be a list"


def test_update_team():
    """Test updating a team"""
    if not created_team_id:
        pytest.skip("No team ID available from previous test")
    
    # Update the team
    update_data = {
        "name": f"Updated {TEST_TEAM['name']}",
        "logo_url": "https://example.com/updated-logo.png"
    }
    
    response = client.put(
        f"/api/teams/{created_team_id}",
        json=update_data,
        headers={"Content-Type": "application/json"}
    )
    
    # Check response
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    
    # Verify the updated fields
    assert data["name"] == update_data["name"], f"Name not updated. Expected {update_data['name']}, got {data.get('name')}"
    assert data["logo_url"] == update_data["logo_url"], f"Logo URL not updated. Expected {update_data['logo_url']}, got {data.get('logo_url')}"


def test_list_teams():
    """Test listing teams with filtering"""
    # Get all teams
    response = client.get("/api/teams/")
    
    # Check response
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    
    # Should be a list
    assert isinstance(data, list), f"Expected a list of teams, got {type(data)}"
    
    # Our test team should be in the list
    team_ids = [team["id"] for team in data if "id" in team]
    if created_team_id:
        assert created_team_id in team_ids, f"Created team ID {created_team_id} not found in teams list"


def test_search_teams():
    """Test searching for teams by name"""
    if not created_team_id:
        pytest.skip("No team ID available from previous test")
    
    # Search for our test team
    search_term = TEST_TEAM["name"].split()[0]  # Just use the first word of the name
    response = client.get(f"/api/teams/search/{search_term}")
    
    # Check response
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    
    # Should be a list
    assert isinstance(data, list), f"Expected a list of teams, got {type(data)}"
    
    # Our test team should be in the results
    team_ids = [team["id"] for team in data if "id" in team]
    if created_team_id:
        assert created_team_id in team_ids, f"Created team ID {created_team_id} not found in search results"


def test_delete_team():
    """Test deleting a team"""
    global created_team_id
    
    if not created_team_id:
        pytest.skip("No team ID available from previous test")
    
    # Delete the team
    response = client.delete(f"/api/teams/{created_team_id}")
    
    # Check response
    assert response.status_code == 204, f"Expected status code 204, got {response.status_code}. Response: {response.text}"
    
    # Verify the team no longer exists
    response = client.get(f"/api/teams/{created_team_id}")
    assert response.status_code == 404, f"Expected status code 404 after deletion, got {response.status_code}"
    
    # Reset the global variable
    created_team_id = None
