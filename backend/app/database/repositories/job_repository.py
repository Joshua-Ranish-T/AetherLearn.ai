"""Job Repository — Local JSON and Firestore implementation."""

from __future__ import annotations

import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from google.cloud.firestore import ArrayUnion
from google.cloud.firestore_v1.base_query import FieldFilter

from app.core.config import get_settings
from app.core.exceptions import DatabaseError, NotFoundError
from app.core.firebase import get_firestore, is_firebase_initialized
from app.core.logging_config import get_logger
from app.database.models import JobDocument
from app.database.repositories.file_lock import acquire_lock

logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_DIR = BASE_DIR / "data"
DB_PATH = DB_DIR / "jobs.json"
COLLECTION_NAME = "jobs"


class JobRepository:
    """Repository for job documents supporting Firebase Firestore with local JSON fallback."""

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
                logger.warning("Error reading jobs DB", error=str(exc))
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
                raise DatabaseError(f"Failed to write jobs database: {exc}") from exc

    def create(self, project_id: str, user_id: str = "local_dev_user") -> JobDocument:
        job_id = str(uuid.uuid4())
        now = datetime.now(tz=UTC)

        doc: JobDocument = {
            "id": job_id,
            "project_id": project_id,
            "user_id": user_id,
            "status": "pending",
            "current_stage": "initialized",
            "stages_completed": [],
            "progress_percent": 0.0,
            "error_message": "",
            "error_stage": "",
            "retry_count": 0,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "started_at": now.isoformat(),
            "completed_at": None,
            "duration_seconds": 0.0,
            "logs": [],
            "result_data": {},
            "graph_state_ref": "",
        }

        if self._use_firestore:
            try:
                doc_ref = get_firestore().collection(COLLECTION_NAME).document(job_id)
                doc_ref.set(dict(doc))
                logger.info(
                    "Job created in Firestore",
                    job_id=job_id,
                    project_id=project_id,
                )
                return doc
            except Exception as exc:
                raise DatabaseError(
                    f"Firestore job create failed in cloud mode: {exc}",
                    context={"job_id": job_id, "project_id": project_id},
                ) from exc

        try:
            with acquire_lock(DB_PATH):
                db = self._read_db()
                db[job_id] = doc
                self._write_db(db)
            logger.info(
                "Job created locally",
                job_id=job_id,
                project_id=doc["project_id"],
            )
            return doc
        except Exception as exc:
            raise DatabaseError(f"Failed to create job: {exc}") from exc

    def get_by_id(self, job_id: str) -> JobDocument:
        if not job_id:
            raise NotFoundError("Job ID cannot be empty.")

        if self._use_firestore:
            try:
                doc_ref = get_firestore().collection(COLLECTION_NAME).document(job_id)
                snap = cast(Any, doc_ref.get())
                if snap.exists:
                    return cast(JobDocument, snap.to_dict() or {})
                raise NotFoundError(
                    f"Job '{job_id}' not found in Firestore.",
                    context={"job_id": job_id},
                )
            except NotFoundError:
                raise
            except Exception as exc:
                raise DatabaseError(
                    f"Firestore get_by_id failed in cloud mode: {exc}",
                    context={"job_id": job_id},
                ) from exc

        db = self._read_db()
        if not job_id or job_id not in db:
            raise NotFoundError(f"Job '{job_id}' not found.")
        return cast(JobDocument, db[job_id])

    def update(self, job_id: str, updates: dict[str, Any]) -> JobDocument:
        updates["updated_at"] = datetime.now(tz=UTC).isoformat()

        if self._use_firestore:
            try:
                doc_ref = get_firestore().collection(COLLECTION_NAME).document(job_id)
                snap = cast(Any, doc_ref.get())
                if snap.exists:
                    doc_ref.update(updates)
                    updated_snap = cast(Any, doc_ref.get())
                    return cast(JobDocument, updated_snap.to_dict() or {})
                raise NotFoundError(f"Job '{job_id}' not found in Firestore.")
            except NotFoundError:
                raise
            except Exception as exc:
                raise DatabaseError(f"Firestore job update failed in cloud mode: {exc}") from exc

        with acquire_lock(DB_PATH):
            db = self._read_db()
            if not job_id or job_id not in db:
                raise NotFoundError(f"Job '{job_id}' not found.")
            db[job_id].update(updates)
            self._write_db(db)
            return cast(JobDocument, db[job_id])

    def mark_failed(self, job_id: str, error_message: str, current_stage: str) -> None:
        self.update(
            job_id,
            {
                "status": "failed",
                "error_message": error_message,
                "error_stage": current_stage,
                "current_stage": current_stage,
                "completed_at": datetime.now(tz=UTC).isoformat(),
            },
        )

    def mark_completed(self, job_id: str, duration_seconds: float = 0.0) -> None:
        self.update(
            job_id,
            {
                "status": "completed",
                "current_stage": "finalize",
                "duration_seconds": duration_seconds,
                "completed_at": datetime.now(tz=UTC).isoformat(),
            },
        )

    def update_stage(self, job_id: str, stage: str) -> None:
        self.update(job_id, {"current_stage": stage})

    def append_log(self, job_id: str, log: dict[str, Any]) -> None:
        if self._use_firestore:
            try:
                doc_ref = get_firestore().collection(COLLECTION_NAME).document(job_id)
                snap = cast(Any, doc_ref.get())
                if snap.exists:
                    doc_ref.update(
                        {
                            "logs": ArrayUnion([log]),
                            "updated_at": datetime.now(tz=UTC).isoformat(),
                        }
                    )
                    return
                raise NotFoundError(f"Job '{job_id}' not found in Firestore.")
            except NotFoundError:
                raise
            except Exception as exc:
                raise DatabaseError(f"Firestore append_log failed in cloud mode: {exc}") from exc

        with acquire_lock(DB_PATH):
            db = self._read_db()
            if not job_id or job_id not in db:
                raise NotFoundError(f"Job '{job_id}' not found.")
            if "logs" not in db[job_id] or not isinstance(db[job_id]["logs"], list):
                db[job_id]["logs"] = []
            db[job_id]["logs"].append(log)
            db[job_id]["updated_at"] = datetime.now(tz=UTC).isoformat()
            self._write_db(db)

    def get_by_project_id(self, project_id: str, limit: int = 10) -> list[JobDocument]:
        if self._use_firestore:
            try:
                query: Any = get_firestore().collection(COLLECTION_NAME)
                query = query.where(filter=FieldFilter("project_id", "==", project_id))
                raw_docs = [cast(Any, doc).to_dict() for doc in query.stream()]
                items = [cast(JobDocument, x) for x in raw_docs if x is not None]
                items.sort(key=lambda x: str(x.get("created_at", "")), reverse=True)
                return items[:limit]
            except Exception as exc:
                raise DatabaseError(f"Firestore get_by_project_id failed in cloud mode: {exc}") from exc

        db = self._read_db()
        all_items = [
            cast(JobDocument, doc)
            for doc in db.values()
            if doc.get("project_id") == project_id
        ]
        all_items.sort(key=lambda x: str(x.get("created_at", "")), reverse=True)
        return all_items[:limit]

    def get_by_project(self, project_id: str, limit: int = 10) -> list[JobDocument]:
        """Alias used by API routes."""
        return self.get_by_project_id(project_id, limit)

    def get(self, job_id: str) -> JobDocument:
        """Alias for get_by_id."""
        return self.get_by_id(job_id)


def emit_live_log(job_id: str, stage: str, status: str, message: str, **metadata: Any) -> None:
    """Helper to emit live log entries during long-running tasks like Manim execution or OCR."""
    if not job_id:
        return
    try:
        repo = JobRepository()
        log_entry = {
            "type": "log",
            "stage": stage,
            "status": status,
            "message": message,
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "metadata": metadata,
            **metadata,
        }
        repo.append_log(job_id, log_entry)
    except Exception as exc:
        logger.debug("Failed to emit live log", error=str(exc), job_id=job_id)

