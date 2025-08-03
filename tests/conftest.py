"""Pytest configuration and shared fixtures."""

import importlib
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from main import app
from app.core.auth import get_current_user, get_current_admin_user
supabase_module = importlib.import_module("app.core.supabase")


@pytest.fixture
def mock_supabase(monkeypatch):
    """Provide a mocked Supabase service for tests."""
    mock = MagicMock()
    monkeypatch.setattr(supabase_module, "supabase", mock)

    modules = [
        "app.routers.players",
        "app.routers.events",
        "app.routers.teams",
        "app.routers.matches",
        "app.routers.player_stats",
        "app.routers.admin",
        "app.routers.leaderboard_supabase",
        "app.routers.payments",
        "app.routers.discord",
    ]
    for path in modules:
        try:
            module = importlib.import_module(path)
            monkeypatch.setattr(module, "supabase", mock, raising=False)
        except ModuleNotFoundError:
            continue
    return mock


@pytest.fixture
def mock_current_user():
    async def _mock_current_user():
        return {"id": 1, "email": "user@example.com", "is_active": True, "is_admin": False}

    return _mock_current_user


@pytest.fixture
def mock_current_admin_user():
    async def _mock_current_admin_user():
        return {"id": 1, "email": "admin@example.com", "is_active": True, "is_admin": True}

    return _mock_current_admin_user


@pytest.fixture
def client(mock_current_user, mock_current_admin_user, mock_supabase):
    """Test client with authentication dependencies overridden."""
    app.dependency_overrides[get_current_user] = mock_current_user
    app.dependency_overrides[get_current_admin_user] = mock_current_admin_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
