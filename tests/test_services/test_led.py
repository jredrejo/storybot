"""Tests for LED controller service."""

import pytest

from app.services.led_controller import MockLEDService


@pytest.fixture
def mock_led_service():
    """Create a mock LED service for testing."""
    return MockLEDService()


class TestMockLEDService:
    """Test mock LED service functionality."""

    @pytest.mark.asyncio
    async def test_mock_led_service_initializes(self, mock_led_service):
        """Test that mock LED service can be created."""
        assert mock_led_service is not None
        assert hasattr(mock_led_service, "is_mock")
        assert hasattr(mock_led_service, "set_color")
        assert hasattr(mock_led_service, "get_color")
        assert hasattr(mock_led_service, "turn_off")

    @pytest.mark.asyncio
    async def test_mock_led_service_is_mock(self, mock_led_service):
        """Test that mock LED service reports as mock."""
        assert mock_led_service.is_mock is True

    @pytest.mark.asyncio
    async def test_mock_led_service_initial_color(self, mock_led_service):
        """Test initial color is black (off)."""
        color = mock_led_service.get_color()
        assert color == (0, 0, 0)

    @pytest.mark.asyncio
    async def test_mock_led_service_set_color(self, mock_led_service):
        """Test setting LED color."""
        await mock_led_service.set_color(255, 0, 0)  # Red
        color = mock_led_service.get_color()
        assert color == (255, 0, 0)

        await mock_led_service.set_color(0, 255, 0)  # Green
        color = mock_led_service.get_color()
        assert color == (0, 255, 0)

        await mock_led_service.set_color(0, 0, 255)  # Blue
        color = mock_led_service.get_color()
        assert color == (0, 0, 255)

    @pytest.mark.asyncio
    async def test_mock_led_service_turn_off(self, mock_led_service):
        """Test turning off LEDs."""
        await mock_led_service.set_color(255, 255, 255)
        assert mock_led_service.get_color() == (255, 255, 255)

        await mock_led_service.turn_off()
        assert mock_led_service.get_color() == (0, 0, 0)

    @pytest.mark.asyncio
    async def test_mock_led_service_get_status(self, mock_led_service):
        """Test getting mock LED service status."""
        status = await mock_led_service.get_status()
        assert "name" in status
        assert "is_mock" in status
        assert "status" in status
        assert status["name"] == "led"
        assert status["is_mock"] is True

    @pytest.mark.asyncio
    async def test_mock_led_service_initialize_and_shutdown(self, mock_led_service):
        """Test initialize and shutdown methods."""
        await mock_led_service.initialize()
        await mock_led_service.shutdown()
        assert mock_led_service.get_color() == (0, 0, 0)
