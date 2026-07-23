"""
Job Repository — Local JSON implementation.
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
from app.database.models import JobDocument

logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_DIR = BASE_DIR / "data"
DB_PATH = DB_DIR / "jobs.json"


class JobRepository:
    """Repository for job documents in local JSON file."""

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
            logger.warning("Error reading jobs DB", error=str(exc))
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
            raise DatabaseError(f"Failed to write jobs database: {exc}") from exc

    def create(self, project_id: str) -> JobDocument:
        job_id = str(uuid.uuid4())
        now = datetime.now(tz=timezone.utc)

        doc: JobDocument = {
            "id": job_id,
            "project_id": project_id,
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
        if not job_id or job_id not in db:
            raise NotFoundError(f"Job '{job_id}' not found.")
        return db[job_id]

    def update(self, job_id: str, updates: dict[str, Any]) -> JobDocument:
        db = self._read_db()
        if not job_id or job_id not in db:
            raise NotFoundError(f"Job '{job_id}' not found.")
        
        updates["updated_at"] = datetime.now(tz=timezone.utc).isoformat()
        db[job_id].update(updates)
        self._write_db(db)
        return db[job_id]

    def mark_failed(self, job_id: str, error_message: str, current_stage: str) -> None:
        self.update(job_id, {
            "status": "failed",
            "error_message": error_message,
            "error_stage": current_stage,
            "current_stage": current_stage,
            "completed_at": datetime.now(tz=timezone.utc).isoformat()
        })

    def mark_completed(self, job_id: str, duration_seconds: float = 0.0) -> None:
        self.update(job_id, {
            "status": "completed",
            "current_stage": "finalize",
            "duration_seconds": duration_seconds,
            "completed_at": datetime.now(tz=timezone.utc).isoformat()
        })

    def update_stage(self, job_id: str, stage: str) -> None:
        self.update(job_id, {
            "current_stage": stage
        })

    def append_log(self, job_id: str, log: dict[str, Any]) -> None:
        db = self._read_db()
        if not job_id or job_id not in db:
            raise NotFoundError(f"Job '{job_id}' not found.")
        if "logs" not in db[job_id] or not isinstance(db[job_id]["logs"], list):
            db[job_id]["logs"] = []
        db[job_id]["logs"].append(log)
        db[job_id]["updated_at"] = datetime.now(tz=timezone.utc).isoformat()
        self._write_db(db)

    def get_by_project_id(self, project_id: str, limit: int = 10) -> list[JobDocument]:
        db = self._read_db()
        items = [doc for doc in db.values() if doc.get("project_id") == project_id]
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items[:limit]

    # Alias used by API routes
    get_by_project = get_by_project_id

