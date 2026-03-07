"""Tests for audio player service."""

import pytest

from app.services.audio_player import MockAudioPlayer


@pytest.fixture
def mock_audio_player():
    """Create a mock audio player for testing."""
    return MockAudioPlayer()


class TestMockAudioPlayer:
    """Test mock audio player functionality."""

    @pytest.mark.asyncio
    async def test_mock_audio_player_initializes(self, mock_audio_player):
        """Test that mock audio player can be created."""
        assert mock_audio_player is not None
        assert hasattr(mock_audio_player, "is_mock")
        assert hasattr(mock_audio_player, "play")
        assert hasattr(mock_audio_player, "stop")
        assert hasattr(mock_audio_player, "is_playing")

    @pytest.mark.asyncio
    async def test_mock_audio_player_is_mock(self, mock_audio_player):
        """Test that mock audio player reports as mock."""
        assert mock_audio_player.is_mock is True

    @pytest.mark.asyncio
    async def test_mock_audio_player_not_playing_initially(self, mock_audio_player):
        """Test that mock audio player is not playing initially."""
        assert mock_audio_player.is_playing is False

    @pytest.mark.asyncio
    async def test_mock_audio_player_play_wav(self, mock_audio_player, tmp_path):
        """Test playing a WAV file with mock player."""
        # Create a dummy WAV file (minimal valid WAV header)
        wav_file = tmp_path / "test.wav"
        wav_file.write_bytes(
            b"RIFF\x24\x00\x00\x00WAVEfmt "
            b"\x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00"
            b"\x02\x00\x10\x00data\x00\x00\x00\x00"
        )

        await mock_audio_player.play(wav_file)
        assert mock_audio_player.is_playing is True

    @pytest.mark.asyncio
    async def test_mock_audio_player_play_mp3(self, mock_audio_player, tmp_path):
        """Test playing an MP3 file with mock player (converts to WAV)."""
        # Create a dummy MP3 file (minimal valid MP3 header)
        mp3_file = tmp_path / "test.mp3"
        mp3_file.write_bytes(b"\xff\xfb\x90\x00" + b"\x00" * 100)

        await mock_audio_player.play(mp3_file)
        # Mock player should track this even without real audio
        assert mock_audio_player.is_playing is True

    @pytest.mark.asyncio
    async def test_mock_audio_player_stop(self, mock_audio_player, tmp_path):
        """Test stopping playback."""
        wav_file = tmp_path / "test.wav"
        wav_file.write_bytes(
            b"RIFF\x24\x00\x00\x00WAVEfmt "
            b"\x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00"
            b"\x02\x00\x10\x00data\x00\x00\x00\x00"
        )

        await mock_audio_player.play(wav_file)
        assert mock_audio_player.is_playing is True

        await mock_audio_player.stop()
        assert mock_audio_player.is_playing is False

    @pytest.mark.asyncio
    async def test_mock_audio_player_get_status(self, mock_audio_player):
        """Test getting mock audio player status."""
        status = await mock_audio_player.get_status()
        assert "name" in status
        assert "is_mock" in status
        assert "status" in status
        assert status["name"] == "audio"
        assert status["is_mock"] is True

    @pytest.mark.asyncio
    async def test_mock_audio_player_initialize_and_shutdown(self, mock_audio_player):
        """Test initialize and shutdown methods."""
        await mock_audio_player.initialize()
        await mock_audio_player.shutdown()
        assert mock_audio_player.is_playing is False
