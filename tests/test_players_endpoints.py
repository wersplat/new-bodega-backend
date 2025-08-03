import pytest


def test_get_player(client, mock_supabase, player_data):
    """Ensure player profile can be retrieved."""
    mock_supabase.fetch_by_id.return_value = player_data

    response = client.get(f"/v1/players/{player_data['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == player_data["id"]
