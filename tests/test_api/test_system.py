"""Tests for system API endpoints."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestSystemEndpoints:
    """Test system endpoint functionality."""

    def test_root_returns_ok(self, client):
        """GET / returns status ok."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "storybot"

    def test_system_status_returns_hardware_state(self, client):
        """GET /api/system/status returns SystemStatus."""
        response = client.get("/api/system/status")
        assert response.status_code == 200
        data = response.json()
        assert "hardware" in data
        assert "uptime_seconds" in data
        assert "version" in data
        assert data["version"] == "0.1.0"

    def test_system_rescan_triggers_detection(self, client):
        """POST /api/system/rescan returns updated status."""
        response = client.post("/api/system/rescan")
        assert response.status_code == 200
        data = response.json()
        assert "hardware" in data
        assert "uptime_seconds" in data
        assert "version" in data
