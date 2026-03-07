"""Tests for Story API endpoints."""

import json
import shutil
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client with lifespan context."""
    # Clean up any existing stories before tests
    stories_dir = Path("content/stories")
    if stories_dir.exists():
        # Remove all story directories
        for item in stories_dir.iterdir():
            if item.is_dir() and item.name.startswith(("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")):
                shutil.rmtree(item)
        # Reset index
        index_file = stories_dir / "stories.json"
        if index_file.exists():
            index_file.write_text(json.dumps({"version": 1, "stories": {}, "nfc_to_story": {}}))

    with TestClient(app) as c:
        yield c

    # Clean up after tests
    if stories_dir.exists():
        for item in stories_dir.iterdir():
            if item.is_dir() and item.name.startswith(("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")):
                shutil.rmtree(item)
        index_file = stories_dir / "stories.json"
        if index_file.exists():
            index_file.write_text(json.dumps({"version": 1, "stories": {}, "nfc_to_story": {}}))


class TestPostStories:
    """Test POST /api/stories endpoint."""

    def test_post_stories_with_multipart_returns_201(self, client: TestClient, tmp_path):
        """Test POST /api/stories with multipart form returns 201 with Story."""
        # Create multipart form data
        audio_content = b"fake audio data"
        files = {
            "audio": ("audio.mp3", BytesIO(audio_content), "audio/mpeg")
        }
        data = {
            "title": "Test Story",
            "emoji": "📚",
            "led_color": "#FF5733",
        }

        response = client.post("/api/stories", files=files, data=data)

        assert response.status_code == 201
        story = response.json()
        assert "id" in story
        assert story["title"] == "Test Story"
        assert story["emoji"] == "📚"
        assert story["led_color"] == "#FF5733"
        assert "audio_file" in story
        assert story["audio_file"] == "audio.mp3"
        assert story["nfc_uid"] is None
        assert story["cover_image"] is None
        assert "created_at" in story

    def test_post_stories_without_audio_returns_422(self, client: TestClient):
        """Test POST /api/stories without audio returns 422 (FastAPI validation)."""
        data = {
            "title": "Test Story",
            "emoji": "📚",
            "led_color": "#FF5733",
        }

        response = client.post("/api/stories", data=data)

        # FastAPI returns 422 for missing required form fields
        assert response.status_code == 422

    def test_post_stories_with_invalid_audio_type_returns_400(self, client: TestClient):
        """Test POST /api/stories with invalid audio type returns 400."""
        files = {
            "audio": ("document.pdf", BytesIO(b"fake pdf"), "application/pdf")
        }
        data = {
            "title": "Test Story",
            "emoji": "📚",
            "led_color": "#FF5733",
        }

        response = client.post("/api/stories", files=files, data=data)

        assert response.status_code == 400
        assert "audio" in response.json()["detail"].lower()

    def test_post_stories_with_cover_image_saves_cover(self, client: TestClient):
        """Test POST /api/stories with cover image saves cover file."""
        files = {
            "audio": ("audio.mp3", BytesIO(b"fake audio"), "audio/mpeg"),
            "cover": ("cover.jpg", BytesIO(b"fake image"), "image/jpeg"),
        }
        data = {
            "title": "Test Story",
            "emoji": "📚",
            "led_color": "#FF5733",
        }

        response = client.post("/api/stories", files=files, data=data)

        assert response.status_code == 201
        story = response.json()
        assert story["cover_image"] == "cover.jpg"


class TestGetStories:
    """Test GET /api/stories endpoint."""

    def test_get_stories_returns_story_list(self, client: TestClient):
        """Test GET /api/stories returns StoryList."""
        # First create a story
        files = {
            "audio": ("audio.mp3", BytesIO(b"fake audio"), "audio/mpeg")
        }
        data = {
            "title": "Test Story",
            "emoji": "📚",
            "led_color": "#FF5733",
        }
        client.post("/api/stories", files=files, data=data)

        # Now list stories
        response = client.get("/api/stories")

        assert response.status_code == 200
        stories = response.json()
        assert "stories" in stories
        assert "total" in stories
        assert stories["total"] == 1
        assert len(stories["stories"]) == 1
        assert stories["stories"][0]["title"] == "Test Story"

    def test_get_stories_empty_returns_empty_list(self, client: TestClient):
        """Test GET /api/stories returns empty list when no stories."""
        response = client.get("/api/stories")

        assert response.status_code == 200
        stories = response.json()
        assert stories["stories"] == []
        assert stories["total"] == 0


class TestGetStoryById:
    """Test GET /api/stories/{id} endpoint."""

    def test_get_story_by_id_returns_story(self, client: TestClient):
        """Test GET /api/stories/{id} returns Story."""
        # First create a story
        files = {
            "audio": ("audio.mp3", BytesIO(b"fake audio"), "audio/mpeg")
        }
        data = {
            "title": "Test Story",
            "emoji": "📚",
            "led_color": "#FF5733",
        }
        create_response = client.post("/api/stories", files=files, data=data)
        story_id = create_response.json()["id"]

        # Get story by ID
        response = client.get(f"/api/stories/{story_id}")

        assert response.status_code == 200
        story = response.json()
        assert story["id"] == story_id
        assert story["title"] == "Test Story"

    def test_get_story_by_invalid_id_returns_404(self, client: TestClient):
        """Test GET /api/stories/{id} with invalid ID returns 404."""
        response = client.get("/api/stories/non-existent-id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestDeleteStory:
    """Test DELETE /api/stories/{id} endpoint."""

    def test_delete_story_returns_204(self, client: TestClient):
        """Test DELETE /api/stories/{id} returns 204."""
        # First create a story
        files = {
            "audio": ("audio.mp3", BytesIO(b"fake audio"), "audio/mpeg")
        }
        data = {
            "title": "Test Story",
            "emoji": "📚",
            "led_color": "#FF5733",
        }
        create_response = client.post("/api/stories", files=files, data=data)
        story_id = create_response.json()["id"]

        # Delete story
        response = client.delete(f"/api/stories/{story_id}")

        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/api/stories/{story_id}")
        assert get_response.status_code == 404

    def test_delete_story_with_invalid_id_returns_404(self, client: TestClient):
        """Test DELETE /api/stories/{id} with invalid ID returns 404."""
        response = client.delete("/api/stories/non-existent-id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
