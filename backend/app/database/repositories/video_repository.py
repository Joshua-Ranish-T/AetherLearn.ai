"""
Video Repository — Local JSON implementation.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.exceptions import NotFoundError, DatabaseError
from app.core.logging_config import get_logger
from app.database.models import VideoDocument

logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_DIR = BASE_DIR / "data"
DB_PATH = DB_DIR / "videos.json"


class VideoRepository:
    """Repository for video documents in local JSON file."""

    def __init__(self) -> None:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        if not DB_PATH.exists():
            self._write_db({})

    def _read_db(self) -> dict[str, Any]:
        if not DB_PATH.exists():
            return {}
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except Exception as exc:
            logger.warning("Error reading videos DB", error=str(exc))
            return {}

    def _write_db(self, data: dict[str, Any]) -> None:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        tmp_path = DB_PATH.with_suffix(".json.tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            os.replace(tmp_path, DB_PATH)
        except Exception as exc:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    pass
            raise DatabaseError(f"Failed to write videos database: {exc}") from exc

    def create(self, data: dict[str, Any]) -> VideoDocument:
        video_id = str(uuid.uuid4())
        now = datetime.now(tz=timezone.utc)

        doc: VideoDocument = {
            "id": video_id,
            "project_id": data.get("project_id") or "",
            "job_id": data.get("job_id") or "",
            "title": data.get("title") or "Generated Video",
            "duration_seconds": float(data.get("duration_seconds") or 0.0),
            "resolution": data.get("resolution") or "1080p",
            "file_url": data.get("file_url") or data.get("video_url") or "",
            "audio_url": data.get("audio_url") or "",
            "transcript_url": data.get("transcript_url") or "",
            "manim_script_url": data.get("manim_script_url") or "",
            "storyboard_url": data.get("storyboard_url") or "",
            "thumbnail_url": data.get("thumbnail_url") or "",
            "file_size_bytes": int(data.get("file_size_bytes") or 0),
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "metadata": data.get("metadata") or {},
        }

        try:
            db = self._read_db()
            db[video_id] = doc
            self._write_db(db)
            logger.info("Video created locally", video_id=video_id)
            return doc
        except Exception as exc:
            raise DatabaseError(f"Failed to create video: {exc}") from exc

    def get_by_id(self, video_id: str) -> VideoDocument:
        db = self._read_db()
        if not video_id or video_id not in db:
            raise NotFoundError(f"Video '{video_id}' not found.")
        return db[video_id]

    def list_all(self, limit: int = 50, offset: int = 0) -> list[VideoDocument]:
        limit = max(1, limit)
        offset = max(0, offset)
        db = self._read_db()
        items = list(db.values())
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items[offset:offset + limit]

    def get_by_project_id(self, project_id: str, limit: int = 10) -> list[VideoDocument]:
        limit = max(1, limit)
        db = self._read_db()
        items = [doc for doc in db.values() if doc.get("project_id") == project_id]
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items[:limit]

    # Alias used by API routes
    get_by_project = get_by_project_id

    def delete(self, video_id: str) -> None:
        db = self._read_db()
        if not video_id or video_id not in db:
            raise NotFoundError(f"Video '{video_id}' not found.")
        del db[video_id]
        self._write_db(db)
        logger.info("Video deleted", video_id=video_id)

