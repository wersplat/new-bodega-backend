import pytest


def test_get_event(client, mock_supabase, event_data):
    """Ensure event details can be retrieved."""
    mock_supabase.get_by_id.return_value = event_data

    response = client.get(f"/v1/events/{event_data['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == event_data["id"]
