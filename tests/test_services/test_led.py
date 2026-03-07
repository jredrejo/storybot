"""Tests for LED controller service."""

import pytest

from app.services.led_controller import (
    MockLEDService,
    RealLEDService,
    create_led_service,
)


@pytest.fixture
def mock_led_service():
    """Create a mock LED service for testing."""
    return MockLEDService()


@pytest.fixture
def real_led_service():
    """Create a real LED service for testing."""
    return RealLEDService()


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

    @pytest.mark.asyncio
    async def test_mock_led_service_clamps_color_values(self, mock_led_service):
        """Test that color values are clamped to 0-255."""
        await mock_led_service.set_color(300, -50, 128)
        color = mock_led_service.get_color()
        assert color == (255, 0, 128)


class TestRealLEDService:
    """Test real LED service functionality."""

    @pytest.mark.asyncio
    async def test_real_led_service_initializes(self, real_led_service):
        """Test that real LED service can be created."""
        assert real_led_service is not None
        assert hasattr(real_led_service, "is_mock")
        assert hasattr(real_led_service, "set_color")
        assert hasattr(real_led_service, "get_color")
        assert hasattr(real_led_service, "turn_off")

    @pytest.mark.asyncio
    async def test_real_led_service_is_not_mock(self, real_led_service):
        """Test that real LED service reports as not mock."""
        assert real_led_service.is_mock is False

    @pytest.mark.asyncio
    async def test_real_led_service_initial_color(self, real_led_service):
        """Test initial color is black (off)."""
        color = real_led_service.get_color()
        assert color == (0, 0, 0)

    @pytest.mark.asyncio
    async def test_real_led_service_set_color(self, real_led_service):
        """Test setting LED color."""
        await real_led_service.set_color(255, 128, 64)
        color = real_led_service.get_color()
        assert color == (255, 128, 64)

    @pytest.mark.asyncio
    async def test_real_led_service_clamps_color_values(self, real_led_service):
        """Test that color values are clamped to 0-255."""
        await real_led_service.set_color(500, -100, 128)
        color = real_led_service.get_color()
        assert color == (255, 0, 128)

    @pytest.mark.asyncio
    async def test_real_led_service_turn_off(self, real_led_service):
        """Test turning off LEDs."""
        await real_led_service.set_color(255, 255, 255)
        await real_led_service.turn_off()
        assert real_led_service.get_color() == (0, 0, 0)

    @pytest.mark.asyncio
    async def test_real_led_service_get_status_not_available(self, real_led_service):
        """Test get_status when hardware not available."""
        status = await real_led_service.get_status()
        assert status["name"] == "led"
        assert status["is_mock"] is False
        assert status["status"] == "not_connected"
        assert "not verified" in status["error_message"]

    @pytest.mark.asyncio
    async def test_real_led_service_get_status_available(self, real_led_service):
        """Test get_status when hardware is available."""
        real_led_service._available = True
        status = await real_led_service.get_status()
        assert status["status"] == "ok"
        assert status["error_message"] is None

    @pytest.mark.asyncio
    async def test_real_led_service_initialize(self, real_led_service):
        """Test initialize method."""
        await real_led_service.initialize()
        # Hardware detection not implemented, so _available stays False
        assert real_led_service._available is False

    @pytest.mark.asyncio
    async def test_real_led_service_shutdown(self, real_led_service):
        """Test shutdown method turns off LEDs."""
        await real_led_service.set_color(100, 100, 100)
        await real_led_service.shutdown()
        assert real_led_service.get_color() == (0, 0, 0)


class TestCreateLEDService:
    """Test LED service factory function."""

    def test_create_led_service_returns_mock(self):
        """Test that create_led_service returns MockLEDService."""
        service = create_led_service()
        # Currently always returns mock until hardware is verified
        assert isinstance(service, MockLEDService)
        assert service.is_mock is True
