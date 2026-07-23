"""
Job Repository — Local JSON implementation.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from app.core.exceptions import NotFoundError, DatabaseError
from app.core.logging_config import get_logger
from app.database.models import JobDocument

logger = get_logger(__name__)

DB_PATH = os.path.join(os.getcwd(), "data", "jobs.json")

class JobRepository:
    """Repository for job documents in local JSON file."""

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

    def create(self, project_id: str) -> JobDocument:
        job_id = str(uuid.uuid4())
        now = datetime.now(tz=timezone.utc)

        doc: JobDocument = {
            "id": job_id,
            "project_id": project_id,
            "status": "queued",
            "current_stage": "initialized",
            "progress_percent": 0.0,
            "error_message": "",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "started_at": None,
            "completed_at": None,
            "result_data": {},
        }

        try:
            db = self._read_db()
            db[job_id] = doc
            self._write_db(db)
            logger.info("Job created locally", job_id=job_id, project_id=doc["project_id"])
            return doc
        except Exception as exc:
            raise DatabaseError(f"Failed to create job: {exc}") from exc

    def get_by_id(self, job_id: str) -> JobDocument:
        db = self._read_db()
        if job_id not in db:
            raise NotFoundError(f"Job '{job_id}' not found.")
        return db[job_id]

    def update(self, job_id: str, updates: dict[str, Any]) -> JobDocument:
        db = self._read_db()
        if job_id not in db:
            raise NotFoundError(f"Job '{job_id}' not found.")
        
        updates["updated_at"] = datetime.now(tz=timezone.utc).isoformat()
        db[job_id].update(updates)
        self._write_db(db)
        return db[job_id]

    def get_by_project_id(self, project_id: str, limit: int = 10) -> list[JobDocument]:
        db = self._read_db()
        items = [doc for doc in db.values() if doc.get("project_id") == project_id]
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items[:limit]
