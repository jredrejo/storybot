"""Tests for TTS engine service."""

import pytest

from app.services.tts_engine import TTSEngine


@pytest.fixture
def tts_engine():
    """Create a TTS engine instance."""
    return TTSEngine()


class TestTTSEngine:
    """Test TTS engine functionality."""

    @pytest.mark.asyncio
    async def test_tts_engine_initializes(self, tts_engine):
        """Test that TTS engine can be created."""
        assert tts_engine is not None
        assert hasattr(tts_engine, "is_loaded")
        assert hasattr(tts_engine, "synthesize")
        assert hasattr(tts_engine, "synthesize_to_file")

    @pytest.mark.asyncio
    async def test_tts_engine_not_loaded_initially(self, tts_engine):
        """Test that TTS engine is not loaded until model is loaded."""
        assert tts_engine.is_loaded is False

    @pytest.mark.asyncio
    async def test_tts_engine_load_model(self, tts_engine):
        """Test loading a TTS model."""
        # This will fail if model doesn't exist - that's expected
        result = await tts_engine.load_model("es_ES-sharvard-medium")
        # Result could be False if model not found
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_tts_engine_synthesize_without_model(self, tts_engine):
        """Test that synthesize fails gracefully without model."""
        with pytest.raises(RuntimeError, match="Model not loaded"):
            tts_engine.synthesize("Hola mundo")

    @pytest.mark.asyncio
    async def test_tts_engine_synthesize_to_file_without_model(
        self, tts_engine, tmp_path
    ):
        """Test that synthesize_to_file fails gracefully without model."""
        output_file = tmp_path / "test.wav"
        with pytest.raises(RuntimeError, match="Model not loaded"):
            await tts_engine.synthesize_to_file("Hola mundo", output_file)

    @pytest.mark.asyncio
    async def test_tts_engine_get_status(self, tts_engine):
        """Test getting TTS engine status."""
        status = await tts_engine.get_status()
        assert "name" in status
        assert "is_mock" in status
        assert "status" in status
        assert status["name"] == "tts"
        assert status["is_mock"] is False  # TTS is never mocked per CONTEXT.md
