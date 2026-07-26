"""Video Repository — Local JSON and Firestore implementation."""

from __future__ import annotations

import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from app.core.config import get_settings
from app.core.exceptions import DatabaseError, NotFoundError
from app.core.firebase import get_firestore, is_firebase_initialized
from app.core.logging_config import get_logger
from app.database.models import VideoDocument
from app.database.repositories.file_lock import acquire_lock
from google.cloud.firestore_v1.base_query import FieldFilter

logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_DIR = BASE_DIR / "data"
DB_PATH = DB_DIR / "videos.json"
COLLECTION_NAME = "videos"


class VideoRepository:
    """Repository for video documents supporting Firebase Firestore with local JSON fallback."""

    def __init__(self) -> None:
        if not self._use_firestore:
            DB_DIR.mkdir(parents=True, exist_ok=True)
            if not DB_PATH.exists():
                self._write_db({})

    @property
    def _use_firestore(self) -> bool:
        settings = get_settings()
        if not is_firebase_initialized():
            if settings.use_firebase or settings.is_production:
                from app.core.firebase import initialize_firebase
                try:
                    initialize_firebase()
                except Exception as exc:
                    if settings.is_production:
                        raise DatabaseError(
                            f"Firebase initialization required in cloud/production mode failed: {exc}"
                        ) from exc
                    logger.warning("Firebase init failed, falling back to local JSON db", error=str(exc))
        return is_firebase_initialized()

    def _read_db(self) -> dict[str, Any]:
        with acquire_lock(DB_PATH):
            if not DB_PATH.exists():
                return {}
            try:
                with open(DB_PATH, encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        return {}
                    return json.loads(content)
            except Exception as exc:
                logger.warning("Error reading videos DB", error=str(exc))
                return {}

    def _write_db(self, data: dict[str, Any]) -> None:
        with acquire_lock(DB_PATH):
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
        now = datetime.now(tz=UTC)

        doc: VideoDocument = {
            "id": video_id,
            "project_id": str(data.get("project_id") or ""),
            "job_id": str(data.get("job_id") or ""),
            "user_id": str(data.get("user_id") or "local_dev_user"),
            "title": str(data.get("title") or "Generated Video"),
            "duration_seconds": float(data.get("duration_seconds") or 0.0),
            "resolution": str(data.get("resolution") or "1080p"),
            "file_url": str(data.get("file_url") or data.get("video_url") or ""),
            "audio_url": str(data.get("audio_url") or ""),
            "transcript_url": str(data.get("transcript_url") or ""),
            "manim_script_url": str(data.get("manim_script_url") or ""),
            "storyboard_url": str(data.get("storyboard_url") or ""),
            "thumbnail_url": str(data.get("thumbnail_url") or ""),
            "file_size_bytes": int(data.get("file_size_bytes") or 0),
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "metadata": data.get("metadata") or {},
        }

        if self._use_firestore:
            try:
                doc_ref = get_firestore().collection(COLLECTION_NAME).document(video_id)
                doc_ref.set(dict(doc))
                logger.info("Video created in Firestore", video_id=video_id)
                return doc
            except Exception as exc:
                raise DatabaseError(
                    f"Firestore video create failed in cloud mode: {exc}",
                    context={"video_id": video_id},
                ) from exc

        try:
            with acquire_lock(DB_PATH):
                db = self._read_db()
                db[video_id] = doc
                self._write_db(db)
            logger.info("Video created locally", video_id=video_id)
            return doc
        except Exception as exc:
            raise DatabaseError(f"Failed to create video: {exc}") from exc

    def get_by_id(self, video_id: str) -> VideoDocument:
        if not video_id:
            raise NotFoundError("Video ID cannot be empty.")

        if self._use_firestore:
            try:
                doc_ref = get_firestore().collection(COLLECTION_NAME).document(video_id)
                snap = cast(Any, doc_ref.get())
                if snap.exists:
                    return cast(VideoDocument, snap.to_dict() or {})
                raise NotFoundError(
                    f"Video '{video_id}' not found in Firestore.",
                    context={"video_id": video_id},
                )
            except NotFoundError:
                raise
            except Exception as exc:
                raise DatabaseError(
                    f"Firestore get_by_id failed in cloud mode: {exc}",
                    context={"video_id": video_id},
                ) from exc

        db = self._read_db()
        if not video_id or video_id not in db:
            raise NotFoundError(f"Video '{video_id}' not found.")
        return cast(VideoDocument, db[video_id])

    def list_all(
        self, limit: int = 50, offset: int = 0, user_id: str | None = None
    ) -> list[VideoDocument]:
        limit = max(1, limit)
        offset = max(0, offset)

        if self._use_firestore:
            try:
                query: Any = get_firestore().collection(COLLECTION_NAME)
                if user_id and user_id != "local_dev_user":
                    query = query.where(filter=FieldFilter("user_id", "==", user_id))
                raw_docs = [cast(Any, doc).to_dict() for doc in query.stream()]
                items = [cast(VideoDocument, x) for x in raw_docs if x is not None]
                items.sort(key=lambda x: str(x.get("created_at", "")), reverse=True)
                return items[offset : offset + limit]
            except Exception as exc:
                raise DatabaseError(f"Firestore video list_all failed in cloud mode: {exc}") from exc

        db = self._read_db()
        all_items = [cast(VideoDocument, v) for v in db.values()]
        if user_id and user_id != "local_dev_user":
            all_items = [
                x for x in all_items if x.get("user_id") == user_id or not x.get("user_id")
            ]
        all_items.sort(key=lambda x: str(x.get("created_at", "")), reverse=True)
        return all_items[offset : offset + limit]

    def get_by_project_id(self, project_id: str, limit: int = 10) -> list[VideoDocument]:
        limit = max(1, limit)
        if self._use_firestore:
            try:
                query: Any = get_firestore().collection(COLLECTION_NAME)
                query = query.where(filter=FieldFilter("project_id", "==", project_id))
                raw_docs = [cast(Any, doc).to_dict() for doc in query.stream()]
                items = [cast(VideoDocument, x) for x in raw_docs if x is not None]
                items.sort(key=lambda x: str(x.get("created_at", "")), reverse=True)
                return items[:limit]
            except Exception as exc:
                raise DatabaseError(f"Firestore get_by_project_id failed in cloud mode: {exc}") from exc

        db = self._read_db()
        all_items = [
            cast(VideoDocument, doc)
            for doc in db.values()
            if doc.get("project_id") == project_id
        ]
        all_items.sort(key=lambda x: str(x.get("created_at", "")), reverse=True)
        return all_items[:limit]

    def get_by_project(self, project_id: str, limit: int = 10) -> list[VideoDocument]:
        """Alias used by API routes."""
        return self.get_by_project_id(project_id, limit)

    def get(self, video_id: str) -> VideoDocument:
        """Alias for get_by_id."""
        return self.get_by_id(video_id)

    def delete(self, video_id: str) -> None:
        if self._use_firestore:
            try:
                doc_ref = get_firestore().collection(COLLECTION_NAME).document(video_id)
                snap = cast(Any, doc_ref.get())
                if snap.exists:
                    doc_ref.delete()
                    logger.info("Video deleted from Firestore", video_id=video_id)
                    return
                raise NotFoundError(f"Video '{video_id}' not found in Firestore.")
            except NotFoundError:
                raise
            except Exception as exc:
                raise DatabaseError(f"Firestore delete failed in cloud mode: {exc}") from exc

        with acquire_lock(DB_PATH):
            db = self._read_db()
            if not video_id or video_id not in db:
                raise NotFoundError(f"Video '{video_id}' not found.")
            del db[video_id]
            self._write_db(db)
            logger.info("Video deleted", video_id=video_id)
