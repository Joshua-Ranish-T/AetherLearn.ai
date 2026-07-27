"""
Application configuration management using Pydantic BaseSettings.
All settings are loaded from environment variables / .env file.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────────────────
    app_name: str = Field(default="AetherLearn.ai Platform")
    app_version: str = Field(default="1.0.0")
    app_env: Literal["development", "staging", "production"] = Field(default="production")
    debug: bool = Field(default=False)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")

    # ── API ───────────────────────────────────────────────────────────────
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_prefix: str = Field(default="/api/v1")
    cors_origins: list[str] = Field(
        default=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
            "https://aetherlearn-ai.vercel.app",
            "https://aetherlearn-ai.onrender.com",
        ]
    )

    # ── Google AI ─────────────────────────────────────────────────────────
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-2.5-flash")
    gemini_fast_model: str = Field(default="gemini-2.0-flash")

    # ── Firebase & Auth ───────────────────────────────────────────────────
    use_firebase: bool = Field(default=True)
    require_auth: bool = Field(default=True)
    firebase_credentials_path: str = Field(default="./firebase-credentials.json")
    firebase_credentials_json: str = Field(default="")
    firebase_project_id: str = Field(default="")
    firebase_storage_bucket: str = Field(default="")

    # ── Rendering & Workers ─────────────────────────────────────────────────
    use_background_worker: bool = Field(default=False)
    e2b_api_key: str = Field(default="")
    render_output_dir: str = Field(default="./renders")
    manim_quality: Literal["low_quality", "medium_quality", "high_quality"] = Field(
        default="low_quality"
    )
    manim_format: str = Field(default="mp4")

    # ── Repair Agent ──────────────────────────────────────────────────────
    max_repair_retries: int = Field(default=3, ge=1, le=10)

    # ── TTS ───────────────────────────────────────────────────────────────
    tts_engine: Literal["edge-tts", "gtts"] = Field(default="edge-tts")
    tts_voice: str = Field(default="en-US-AriaNeural")
    tts_language: str = Field(default="en")

    # ── FFmpeg ────────────────────────────────────────────────────────────
    ffmpeg_binary: str = Field(default="ffmpeg")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            v_str = v.strip()
            if not v_str:
                return []
            try:
                parsed = json.loads(v_str)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except (json.JSONDecodeError, TypeError):
                pass
            return [origin.strip() for origin in v_str.split(",") if origin.strip()]
        if isinstance(v, list):
            return [str(item).strip() for item in v if str(item).strip()]
        return v

    @property
    def render_output_path(self) -> Path:
        path = Path(self.render_output_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def firebase_credentials_file(self) -> Path:
        return Path(self.firebase_credentials_path)

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
