"""
Narration generation schemas.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class NarrationSegment(BaseModel):
    """A single narration segment aligned to a storyboard scene."""

    scene_number: int
    scene_title: str
    text: str = Field(description="The narration text for this segment")
    start_time_seconds: float = Field(
        description="Start time in the final video"
    )
    end_time_seconds: float = Field(description="End time in the final video")
    duration_seconds: float
    audio_file_path: str = Field(
        default="",
        description="Local path to the generated audio file for this segment"
    )
    audio_url: str = Field(
        default="",
        description="Firebase Storage URL for this segment's audio"
    )
    word_count: int = Field(default=0)
    speaking_rate: float = Field(
        default=1.0,
        description="TTS speaking rate multiplier"
    )


class NarrationScript(BaseModel):
    """Complete narration output for the entire video."""

    project_id: str
    title: str
    full_text: str = Field(
        description="Complete narration text (all segments joined)"
    )
    segments: list[NarrationSegment]
    total_duration_seconds: float
    tts_engine: str = Field(description="TTS engine used: edge-tts | gtts")
    tts_voice: str = Field(description="Voice name / language code")
    combined_audio_path: str = Field(
        default="",
        description="Local path to the final merged narration audio file"
    )
    combined_audio_url: str = Field(
        default="",
        description="Firebase Storage URL for the combined audio"
    )
    transcript_path: str = Field(
        default="",
        description="Local path to the plain-text transcript file"
    )
    transcript_url: str = Field(
        default="",
        description="Firebase Storage URL for the transcript"
    )
    word_count: int = Field(default=0)


class AudioResult(BaseModel):
    """Result from the TTS service for a single text segment."""

    success: bool
    audio_file_path: str = Field(default="")
    duration_seconds: float = Field(default=0.0)
    error_message: str = Field(default="")
    tts_engine: str = Field(default="")
    voice: str = Field(default="")
