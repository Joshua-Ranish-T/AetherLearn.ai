"""
Project Repository — Local JSON implementation.
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
from app.database.models import ProjectDocument

logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_DIR = BASE_DIR / "data"
DB_PATH = DB_DIR / "projects.json"


class ProjectRepository:
    """Repository for project documents in local JSON file."""

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
            logger.warning("Error reading projects DB", error=str(exc))
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
            raise DatabaseError(f"Failed to write projects database: {exc}") from exc

    def create(self, data: dict[str, Any]) -> ProjectDocument:
        project_id = str(uuid.uuid4())
        now = datetime.now(tz=timezone.utc)

        doc: ProjectDocument = {
            "id": project_id,
            "title": data.get("title") or "Untitled Project",
            "description": data.get("description") or "",
            "input_type": data.get("input_type") or "text",
            "input_text": data.get("input_text") or "",
            "input_file_url": data.get("input_file_url") or "",
            "status": "pending",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "metadata": data.get("metadata") or {},
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
        if not project_id or project_id not in db:
            raise NotFoundError(f"Project '{project_id}' not found.", context={"project_id": project_id})
        return db[project_id]

    def list_all(self, limit: int = 50, offset: int = 0) -> list[ProjectDocument]:
        limit = max(1, limit)
        offset = max(0, offset)
        db = self._read_db()
        items = list(db.values())
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items[offset:offset + limit]

    def update(self, project_id: str, updates: dict[str, Any]) -> ProjectDocument:
        db = self._read_db()
        if not project_id or project_id not in db:
            raise NotFoundError(f"Project '{project_id}' not found.")
        
        updates["updated_at"] = datetime.now(tz=timezone.utc).isoformat()
        db[project_id].update(updates)
        self._write_db(db)
        return db[project_id]

    def update_status(self, project_id: str, status: str) -> None:
        self.update(project_id, {"status": status})

    def delete(self, project_id: str) -> None:
        db = self._read_db()
        if not project_id or project_id not in db:
            raise NotFoundError(f"Project '{project_id}' not found.")
        del db[project_id]
        self._write_db(db)
        logger.info("Project deleted", project_id=project_id)

    def get_by_status(self, status: str) -> list[ProjectDocument]:
        db = self._read_db()
        return [doc for doc in db.values() if doc.get("status") == status]

