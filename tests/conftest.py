"""Pytest configuration and shared fixtures."""

import importlib
from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.auth import get_current_user, get_current_admin_user

supabase_module = importlib.import_module("app.core.supabase")


@pytest.fixture
def mock_supabase(mock_rate_limiter, monkeypatch):
    """Provide a mocked Supabase service for tests."""
    mock = MagicMock()
    mock.get_client.return_value = MagicMock()
    mock.fetch_by_id = MagicMock()
    mock.get_by_id = MagicMock()
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


@pytest.fixture(autouse=True, scope="session")
def mock_rate_limiter():
    """Disable rate limiting during tests."""
    rate_limiter_module = importlib.import_module("app.core.rate_limiter")

    class DummyLimiter:
        def limit(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

        def exempt(self, func):
            return func

    rate_limiter_module.limiter = DummyLimiter()

    import slowapi.middleware

    class DummyMiddleware:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            await self.app(scope, receive, send)

    slowapi.middleware.SlowAPIMiddleware = DummyMiddleware
    return rate_limiter_module.limiter


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
    from main import app

    app.dependency_overrides[get_current_user] = mock_current_user
    app.dependency_overrides[get_current_admin_user] = mock_current_admin_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def player_data():
    """Sample player data used in endpoint tests."""
    return {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "gamertag": "TestPlayer",
        "region": "NA",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
    }


@pytest.fixture
def event_data():
    """Sample event data used in endpoint tests."""
    now = datetime.now(timezone.utc)
    return {
        "id": str(uuid4()),
        "name": "Test Event",
        "event_type": "League",
        "tier": "T1",
        "start_date": now.isoformat(),
        "end_date": (now).isoformat(),
        "season_number": 1,
        "status": "upcoming",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }


@pytest.fixture
def team_data():
    """Sample team data used in endpoint tests."""
    now = datetime.now(timezone.utc)
    return {
        "id": str(uuid4()),
        "name": "Test Team",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }
