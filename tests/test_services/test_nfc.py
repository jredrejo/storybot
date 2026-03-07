"""Tests for NFC handler service."""

import asyncio

import pytest

from app.services.nfc_handler import MockNFCService


@pytest.fixture
def mock_nfc_service():
    """Create a mock NFC service for testing."""
    return MockNFCService()


class TestMockNFCService:
    """Test mock NFC service functionality."""

    @pytest.mark.asyncio
    async def test_mock_nfc_service_initializes(self, mock_nfc_service):
        """Test that mock NFC service can be created."""
        assert mock_nfc_service is not None
        assert hasattr(mock_nfc_service, "is_mock")
        assert hasattr(mock_nfc_service, "start_polling")
        assert hasattr(mock_nfc_service, "stop_polling")
        assert hasattr(mock_nfc_service, "simulate_tap")

    @pytest.mark.asyncio
    async def test_mock_nfc_service_is_mock(self, mock_nfc_service):
        """Test that mock NFC service reports as mock."""
        assert mock_nfc_service.is_mock is True

    @pytest.mark.asyncio
    async def test_mock_nfc_service_polling(self, mock_nfc_service):
        """Test polling lifecycle."""
        uid_received = []

        def callback(uid: str):
            uid_received.append(uid)

        await mock_nfc_service.start_polling(callback)
        # Mock doesn't actually poll, just sets up callback
        await mock_nfc_service.stop_polling()

    @pytest.mark.asyncio
    async def test_mock_nfc_service_simulate_tap(self, mock_nfc_service):
        """Test simulating a card tap."""
        uid_received = []

        def callback(uid: str):
            uid_received.append(uid)

        test_uid = "04:A3:5B:C2:D4:30"
        await mock_nfc_service.start_polling(callback)
        mock_nfc_service.simulate_tap(test_uid)

        # Give callback time to execute
        await asyncio.sleep(0.1)

        assert test_uid in uid_received
        await mock_nfc_service.stop_polling()

    @pytest.mark.asyncio
    async def test_mock_nfc_service_get_status(self, mock_nfc_service):
        """Test getting mock NFC service status."""
        status = await mock_nfc_service.get_status()
        assert "name" in status
        assert "is_mock" in status
        assert "status" in status
        assert status["name"] == "nfc"
        assert status["is_mock"] is True

    @pytest.mark.asyncio
    async def test_mock_nfc_service_initialize_and_shutdown(self, mock_nfc_service):
        """Test initialize and shutdown methods."""
        await mock_nfc_service.initialize()
        await mock_nfc_service.shutdown()
        assert not mock_nfc_service.is_polling
