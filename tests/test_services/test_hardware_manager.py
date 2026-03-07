"""Tests for hardware manager."""
import pytest
from app.services.hardware_manager import HardwareManager
from app.services.base import HardwareService


class MockService(HardwareService):
    """Mock hardware service for testing."""

    def __init__(self, name: str, is_mock: bool = True):
        self._name = name
        self._is_mock = is_mock
        self._initialized = False
        self._error = None

    @property
    def is_mock(self) -> bool:
        return self._is_mock

    @property
    def name(self) -> str:
        return self._name

    async def get_status(self) -> dict:
        if self._error:
            return {
                "name": self._name,
                "is_mock": self._is_mock,
                "status": "error",
                "error_message": self._error
            }
        return {
            "name": self._name,
            "is_mock": self._is_mock,
            "status": "ok" if self._initialized else "not_connected"
        }

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False


@pytest.fixture
async def hardware_manager():
    """Create a HardwareManager instance."""
    manager = HardwareManager()
    yield manager
    # Cleanup
    await manager.shutdown()


class TestHardwareManager:
    """Test HardwareManager functionality."""

    @pytest.mark.asyncio
    async def test_get_status_returns_dict_with_service_states(self, hardware_manager):
        """HardwareManager.get_status() returns dict with service states."""
        status = await hardware_manager.get_status()
        assert isinstance(status, dict)
        assert "hardware" in status
        assert "uptime_seconds" in status
        assert "version" in status

    @pytest.mark.asyncio
    async def test_rescan_triggers_detection_of_all_services(self, hardware_manager):
        """HardwareManager.rescan() triggers detection of all services."""
        # Register a mock service
        mock_service = MockService("test_service")
        hardware_manager.register_service("test_service", mock_service)

        # Rescan should trigger detection
        await hardware_manager.rescan()

        # Verify service was detected
        status = await hardware_manager.get_status()
        assert "test_service" in status["hardware"]

    @pytest.mark.asyncio
    async def test_register_service_adds_to_registry(self, hardware_manager):
        """Registering a service adds it to the registry."""
        mock_service = MockService("nfc")
        hardware_manager.register_service("nfc", mock_service)

        status = await hardware_manager.get_status()
        assert "nfc" in status["hardware"]

    @pytest.mark.asyncio
    async def test_shutdown_cleans_up_all_services(self, hardware_manager):
        """HardwareManager.shutdown() cleans up all services."""
        mock_service = MockService("audio")
        await mock_service.initialize()
        hardware_manager.register_service("audio", mock_service)

        # Verify service is initialized
        status_before = await mock_service.get_status()
        assert status_before["status"] == "ok"

        # Shutdown manager
        await hardware_manager.shutdown()

        # Verify service was cleaned up
        status_after = await mock_service.get_status()
        assert status_after["status"] == "not_connected"
