"""
Project Repository — Local JSON implementation.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from app.core.exceptions import NotFoundError, DatabaseError
from app.core.logging_config import get_logger
from app.database.models import ProjectDocument

logger = get_logger(__name__)

DB_PATH = os.path.join(os.getcwd(), "data", "projects.json")

class ProjectRepository:
    """Repository for project documents in local JSON file."""

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

    def create(self, data: dict[str, Any]) -> ProjectDocument:
        project_id = str(uuid.uuid4())
        now = datetime.now(tz=timezone.utc)

        doc: ProjectDocument = {
            "id": project_id,
            "title": data.get("title", "Untitled Project"),
            "description": data.get("description", ""),
            "input_type": data.get("input_type", "text"),
            "input_text": data.get("input_text", ""),
            "input_file_url": data.get("input_file_url", ""),
            "status": "pending",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "metadata": data.get("metadata", {}),
        }

        try:
            db = self._read_db()
            db[project_id] = doc
            self._write_db(db)
            logger.info("Project created locally", project_id=project_id)
            return doc
        except Exception as exc:
            raise DatabaseError(f"Failed to create project: {exc}", context={"project_id": project_id}) from exc

    def get_by_id(self, project_id: str) -> ProjectDocument:
        db = self._read_db()
        if project_id not in db:
            raise NotFoundError(f"Project '{project_id}' not found.", context={"project_id": project_id})
        return db[project_id]

    def list_all(self, limit: int = 50, offset: int = 0) -> list[ProjectDocument]:
        db = self._read_db()
        items = list(db.values())
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items[offset:offset+limit]

    def update(self, project_id: str, updates: dict[str, Any]) -> ProjectDocument:
        db = self._read_db()
        if project_id not in db:
            raise NotFoundError(f"Project '{project_id}' not found.")
        
        updates["updated_at"] = datetime.now(tz=timezone.utc).isoformat()
        db[project_id].update(updates)
        self._write_db(db)
        return db[project_id]

    def update_status(self, project_id: str, status: str) -> None:
        self.update(project_id, {"status": status})

    def delete(self, project_id: str) -> None:
        db = self._read_db()
        if project_id not in db:
            raise NotFoundError(f"Project '{project_id}' not found.")
        del db[project_id]
        self._write_db(db)
        logger.info("Project deleted", project_id=project_id)

    def get_by_status(self, status: str) -> list[ProjectDocument]:
        db = self._read_db()
        return [doc for doc in db.values() if doc.get("status") == status]
