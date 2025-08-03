import pytest


def test_get_team(client, mock_supabase, team_data):
    """Ensure team details can be retrieved."""
    mock_supabase.get_by_id.return_value = team_data

    response = client.get(f"/v1/teams/{team_data['id']}?include_players=false")
    assert response.status_code == 200
    assert response.json()["id"] == team_data["id"]
