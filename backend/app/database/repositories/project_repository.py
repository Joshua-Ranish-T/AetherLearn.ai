"""Project Repository — Local JSON and Firestore implementation."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from app.core.config import get_settings
from app.core.exceptions import DatabaseError, NotFoundError
from app.core.firebase import get_firestore, is_firebase_initialized
from app.core.logging_config import get_logger
from app.database.models import ProjectDocument
from app.database.repositories.file_lock import acquire_lock
from google.cloud.firestore_v1.base_query import FieldFilter

logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_DIR = BASE_DIR / "data"
DB_PATH = DB_DIR / "projects.json"
COLLECTION_NAME = "projects"


class ProjectRepository:
    """Repository for project documents supporting Firebase Firestore with local JSON fallback."""

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
        if not DB_PATH.exists():
            return {}
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                return cast(dict[str, Any], json.load(f))
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Failed to read local DB, initializing empty", error=str(exc))
            return {}

    def _write_db(self, data: dict[str, Any]) -> None:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        tmp_path = DB_PATH.with_suffix(".tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            tmp_path.replace(DB_PATH)
        except OSError as exc:
            logger.error("Failed to write local DB", error=str(exc))
            raise DatabaseError(f"Failed to write DB: {exc}") from exc

    def create(self, data: dict[str, Any]) -> ProjectDocument:
        project_id = str(data.get("id") or uuid.uuid4())
        now = datetime.now(tz=UTC)

        doc: ProjectDocument = {
            "id": project_id,
            "user_id": str(data.get("user_id") or "local_dev_user"),
            "title": str(data.get("title", "")),
            "description": str(data.get("description", "")),
            "input_type": str(data.get("input_type", "text")),
            "input_text": str(data.get("input_text", "")),
            "input_file_url": str(data.get("input_file_url", "")),
            "status": "pending",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "metadata": data.get("metadata") or {},
        }

        if self._use_firestore:
            try:
                doc_ref = get_firestore().collection(COLLECTION_NAME).document(project_id)
                doc_ref.set(dict(doc))
                logger.info("Project created in Firestore", project_id=project_id)
                return doc
            except Exception as exc:
                raise DatabaseError(
                    f"Firestore create failed in cloud mode: {exc}",
                    context={"project_id": project_id},
                ) from exc

        try:
            with acquire_lock(DB_PATH):
                db = self._read_db()
                db[project_id] = doc
                self._write_db(db)
            logger.info("Project created locally", project_id=project_id)
            return doc
        except Exception as exc:
            raise DatabaseError(
                f"Failed to create project: {exc}",
                context={"project_id": project_id},
            ) from exc

    def get_by_id(self, project_id: str) -> ProjectDocument:
        if not project_id:
            raise NotFoundError("Project ID cannot be empty.")

        if self._use_firestore:
            try:
                doc_ref = get_firestore().collection(COLLECTION_NAME).document(project_id)
                snap = cast(Any, doc_ref.get())
                if snap.exists:
                    return cast(ProjectDocument, snap.to_dict() or {})
                raise NotFoundError(
                    f"Project '{project_id}' not found in Firestore.",
                    context={"project_id": project_id},
                )
            except NotFoundError:
                raise
            except Exception as exc:
                raise DatabaseError(
                    f"Firestore get_by_id failed in cloud mode: {exc}",
                    context={"project_id": project_id},
                ) from exc

        db = self._read_db()
        if project_id not in db:
            raise NotFoundError(
                f"Project '{project_id}' not found.",
                context={"project_id": project_id},
            )
        return cast(ProjectDocument, db[project_id])

    def list_all(
        self, limit: int = 50, offset: int = 0, user_id: str | None = None
    ) -> list[ProjectDocument]:
        limit = max(1, limit)
        offset = max(0, offset)

        if self._use_firestore:
            try:
                query: Any = get_firestore().collection(COLLECTION_NAME)
                if user_id and user_id != "local_dev_user":
                    query = query.where(filter=FieldFilter("user_id", "==", user_id))
                raw_docs = [cast(Any, doc).to_dict() for doc in query.stream()]
                items = [cast(ProjectDocument, x) for x in raw_docs if x is not None]
                items.sort(key=lambda x: str(x.get("created_at", "")), reverse=True)
                return items[offset : offset + limit]
            except Exception as exc:
                raise DatabaseError(f"Firestore list_all failed in cloud mode: {exc}") from exc

        db = self._read_db()
        all_items = [cast(ProjectDocument, v) for v in db.values()]
        if user_id and user_id != "local_dev_user":
            all_items = [
                x for x in all_items if x.get("user_id") == user_id or not x.get("user_id")
            ]
        all_items.sort(key=lambda x: str(x.get("created_at", "")), reverse=True)
        return all_items[offset : offset + limit]

    def update(self, project_id: str, updates: dict[str, Any]) -> ProjectDocument:
        updates["updated_at"] = datetime.now(tz=UTC).isoformat()

        if self._use_firestore:
            try:
                doc_ref = get_firestore().collection(COLLECTION_NAME).document(project_id)
                snap = cast(Any, doc_ref.get())
                if snap.exists:
                    doc_ref.update(updates)
                    updated_snap = cast(Any, doc_ref.get())
                    return cast(ProjectDocument, updated_snap.to_dict() or {})
                raise NotFoundError(f"Project '{project_id}' not found in Firestore.")
            except NotFoundError:
                raise
            except Exception as exc:
                raise DatabaseError(f"Firestore update failed in cloud mode: {exc}") from exc

        with acquire_lock(DB_PATH):
            db = self._read_db()
            if not project_id or project_id not in db:
                raise NotFoundError(f"Project '{project_id}' not found.")
            db[project_id].update(updates)
            self._write_db(db)
            return cast(ProjectDocument, db[project_id])

    def update_status(self, project_id: str, status: str) -> None:
        self.update(project_id, {"status": status})

    def delete(self, project_id: str) -> None:
        if self._use_firestore:
            try:
                doc_ref = get_firestore().collection(COLLECTION_NAME).document(project_id)
                snap = cast(Any, doc_ref.get())
                if snap.exists:
                    doc_ref.delete()
                    logger.info("Project deleted from Firestore", project_id=project_id)
                    return
                raise NotFoundError(f"Project '{project_id}' not found in Firestore.")
            except NotFoundError:
                raise
            except Exception as exc:
                raise DatabaseError(f"Firestore delete failed in cloud mode: {exc}") from exc

        with acquire_lock(DB_PATH):
            db = self._read_db()
            if not project_id or project_id not in db:
                raise NotFoundError(f"Project '{project_id}' not found.")
            del db[project_id]
            self._write_db(db)
            logger.info("Project deleted", project_id=project_id)

    def get_by_status(self, status: str) -> list[ProjectDocument]:
        if self._use_firestore:
            try:
                query: Any = get_firestore().collection(COLLECTION_NAME)
                query = query.where(filter=FieldFilter("status", "==", status))
                raw_docs = [cast(Any, doc).to_dict() for doc in query.stream()]
                return [cast(ProjectDocument, x) for x in raw_docs if x is not None]
            except Exception as exc:
                raise DatabaseError(f"Firestore get_by_status failed in cloud mode: {exc}") from exc

        db = self._read_db()
        return [
            cast(ProjectDocument, doc)
            for doc in db.values()
            if doc.get("status") == status
        ]

    def get(self, project_id: str) -> ProjectDocument:
        """Alias for get_by_id."""
        return self.get_by_id(project_id)
