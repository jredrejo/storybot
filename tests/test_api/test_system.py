"""Tests for system API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client with lifespan context."""
    with TestClient(app) as c:
        yield c


class TestSystemEndpoints:
    """Test system endpoint functionality."""

    def test_root_returns_ok(self, client):
        """GET / redirects to children's kiosk interface."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/children/"

    def test_system_status_returns_hardware_state(self, client):
        """GET /api/system/status returns SystemStatus."""
        response = client.get("/api/system/status")
        assert response.status_code == 200
        data = response.json()
        assert "hardware" in data
        assert "uptime_seconds" in data
        assert "version" in data
        assert data["version"] == "0.1.0"

        # Verify all 4 services are present
        hardware = data["hardware"]
        assert "tts" in hardware
        assert "nfc" in hardware
        assert "led" in hardware
        assert "audio" in hardware

        # Verify each service has is_mock flag
        for service_name, service_state in hardware.items():
            assert "is_mock" in service_state
            assert "status" in service_state
            assert service_state["name"] == service_name

    def test_system_rescan_triggers_detection(self, client):
        """POST /api/system/rescan returns updated status."""
        response = client.post("/api/system/rescan")
        assert response.status_code == 200
        data = response.json()
        assert "hardware" in data
        assert "uptime_seconds" in data
        assert "version" in data

        # Verify all 4 services after rescan
        hardware = data["hardware"]
        assert "tts" in hardware
        assert "nfc" in hardware
        assert "led" in hardware
        assert "audio" in hardware
