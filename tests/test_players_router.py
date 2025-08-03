"""Players router integration tests.

These tests rely on external services (Redis, Supabase) and are skipped by default.
"""
import pytest

pytest.skip("Players router integration tests require external services", allow_module_level=True)
