"""Story models for API requests and responses."""

from typing import Optional
from pydantic import BaseModel, Field


class StoryCreate(BaseModel):
    """Story creation request."""

    title: str = Field(..., description="Story title")
    emoji: str = Field(..., description="Story emoji icon")
    led_color: str = Field(..., description="LED color in hex format (e.g., #FF5733)")


class Story(BaseModel):
    """Story model with all fields."""

    id: str = Field(..., description="Unique story identifier (UUID)")
    title: str = Field(..., description="Story title")
    emoji: str = Field(..., description="Story emoji icon")
    led_color: str = Field(..., description="LED color in hex format")
    audio_file: str = Field(..., description="Audio file name (e.g., audio.mp3)")
    cover_image: Optional[str] = Field(
        None, description="Cover image file name (e.g., cover.jpg)"
    )
    nfc_uid: Optional[str] = Field(None, description="NFC card UID assigned to story")
    created_at: str = Field(..., description="ISO timestamp of creation")


class StoryList(BaseModel):
    """List of stories with total count."""

    stories: list[Story] = Field(..., description="List of stories")
    total: int = Field(..., description="Total number of stories")
