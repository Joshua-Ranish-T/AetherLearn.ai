"""
Video Repository — Local JSON implementation.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from app.core.exceptions import NotFoundError, DatabaseError
from app.core.logging_config import get_logger
from app.database.models import VideoDocument

logger = get_logger(__name__)

DB_PATH = os.path.join(os.getcwd(), "data", "videos.json")

class VideoRepository:
    """Repository for video documents in local JSON file."""

    def __init__(self) -> None:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        if not os.path.exists(DB_PATH):
            with open(DB_PATH, "w") as f:
                json.dump({}, f)

    def _read_db(self) -> dict[str, Any]:
        try:
            with open(DB_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def _write_db(self, data: dict[str, Any]) -> None:
        with open(DB_PATH, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def create(self, data: dict[str, Any]) -> VideoDocument:
        video_id = str(uuid.uuid4())
        now = datetime.now(tz=timezone.utc)

        doc: VideoDocument = {
            "id": video_id,
            "project_id": data["project_id"],
            "job_id": data["job_id"],
            "title": data.get("title", "Generated Video"),
            "video_url": data["video_url"],
            "thumbnail_url": data.get("thumbnail_url", ""),
            "duration_seconds": data.get("duration_seconds", 0.0),
            "created_at": now.isoformat(),
            "metadata": data.get("metadata", {}),
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
        if video_id not in db:
            raise NotFoundError(f"Video '{video_id}' not found.")
        return db[video_id]

    def list_all(self, limit: int = 50, offset: int = 0) -> list[VideoDocument]:
        db = self._read_db()
        items = list(db.values())
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items[offset:offset+limit]

    def get_by_project_id(self, project_id: str, limit: int = 10) -> list[VideoDocument]:
        db = self._read_db()
        items = [doc for doc in db.values() if doc.get("project_id") == project_id]
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items[:limit]

    def delete(self, video_id: str) -> None:
        db = self._read_db()
        if video_id not in db:
            raise NotFoundError(f"Video '{video_id}' not found.")
        del db[video_id]
        self._write_db(db)
        logger.info("Video deleted", video_id=video_id)
