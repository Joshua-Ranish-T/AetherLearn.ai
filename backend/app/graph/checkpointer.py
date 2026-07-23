"""
Firebase-backed LangGraph checkpointer.

Persists LangGraph state snapshots to Firestore so that:
- Long-running jobs survive server restarts
- State can be resumed from any checkpoint
- Full execution history is queryable
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Iterator, Sequence

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    get_checkpoint_id,
)

from app.core.firebase import get_firestore
from app.core.logging_config import get_logger

logger = get_logger(__name__)

CHECKPOINTS_COLLECTION = "checkpoints"


def _serialize(obj: Any) -> Any:
    """JSON-serialize LangGraph state (handle non-serializable types)."""
    if isinstance(obj, dict):
        return {str(k): _serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_serialize(item) for item in obj]
    if hasattr(obj, "model_dump"):
        try:
            return _serialize(obj.model_dump())
        except Exception:
            pass
    if hasattr(obj, "dict") and callable(obj.dict):
        try:
            return _serialize(obj.dict())
        except Exception:
            pass
    if hasattr(obj, "value"):
        return obj.value
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    return str(obj)


class FirebaseCheckpointer(BaseCheckpointSaver):
    """
    LangGraph checkpointer backed by Firebase Firestore.

    Each thread's checkpoints are stored under:
    /checkpoints/{thread_id}/snapshots/{checkpoint_id}
    """

    @property
    def _db(self):  # type: ignore[override]
        return get_firestore()

    def _thread_col(self, thread_id: str):
        return (
            self._db
            .collection(CHECKPOINTS_COLLECTION)
            .document(thread_id)
            .collection("snapshots")
        )

    def get_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        """Retrieve the latest (or specific) checkpoint for a thread."""
        configurable = config.get("configurable", {}) if config else {}
        thread_id: str | None = configurable.get("thread_id")
        if not thread_id:
            return None
        checkpoint_id: str | None = configurable.get("checkpoint_id")

        try:
            col = self._thread_col(thread_id)
            if checkpoint_id:
                snap = col.document(checkpoint_id).get()
                if not snap.exists:
                    return None
                doc = snap.to_dict() or {}
            else:
                # Get the most recent checkpoint
                results = list(
                    col.order_by("created_at", direction="DESCENDING").limit(1).stream()
                )
                if not results:
                    return None
                doc = results[0].to_dict() or {}

            checkpoint = doc.get("checkpoint", {})
            metadata = doc.get("metadata", {})
            parent_config: RunnableConfig | None = None
            if parent_id := doc.get("parent_checkpoint_id"):
                parent_config = {
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_id": parent_id,
                    }
                }

            return CheckpointTuple(
                config={
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_id": doc.get("checkpoint_id", checkpoint_id or ""),
                    }
                },
                checkpoint=checkpoint,
                metadata=metadata,
                parent_config=parent_config,
            )
        except Exception as exc:
            logger.warning("Failed to retrieve checkpoint", thread_id=thread_id, error=str(exc))
            return None

    def list(
        self,
        config: RunnableConfig | None,
        *,
        filter: dict[str, Any] | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> Iterator[CheckpointTuple]:
        """List checkpoints for a thread, most recent first."""
        configurable = config.get("configurable", {}) if config else {}
        thread_id: str | None = configurable.get("thread_id")
        if not thread_id:
            return
        try:
            col = self._thread_col(thread_id)
            query = col.order_by("created_at", direction="DESCENDING")
            if limit:
                query = query.limit(limit)
            for snap in query.stream():
                doc = snap.to_dict() or {}
                parent_config: RunnableConfig | None = None
                if parent_id := doc.get("parent_checkpoint_id"):
                    parent_config = {
                        "configurable": {
                            "thread_id": thread_id,
                            "checkpoint_id": parent_id,
                        }
                    }
                yield CheckpointTuple(
                    config={
                        "configurable": {
                            "thread_id": thread_id,
                            "checkpoint_id": doc.get("checkpoint_id", ""),
                        }
                    },
                    checkpoint=doc.get("checkpoint", {}),
                    metadata=doc.get("metadata", {}),
                    parent_config=parent_config,
                )
        except Exception as exc:
            logger.warning("Failed to list checkpoints", thread_id=thread_id, error=str(exc))
            return

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict[str, Any],
    ) -> RunnableConfig:
        """Persist a checkpoint to Firestore."""
        configurable = config.get("configurable", {}) if config else {}
        thread_id: str = configurable.get("thread_id", "default")
        checkpoint_id: str = checkpoint.get("id", "") if isinstance(checkpoint, dict) else str(getattr(checkpoint, "id", ""))
        parent_id: str | None = configurable.get("checkpoint_id")

        doc = {
            "thread_id": thread_id,
            "checkpoint_id": checkpoint_id,
            "parent_checkpoint_id": parent_id or "",
            "checkpoint": _serialize(checkpoint),
            "metadata": _serialize(dict(metadata) if metadata else {}),
            "created_at": datetime.now(tz=timezone.utc),
        }

        try:
            if thread_id and checkpoint_id:
                self._thread_col(thread_id).document(checkpoint_id).set(doc)
        except Exception as exc:
            logger.warning(
                "Failed to persist checkpoint",
                thread_id=thread_id,
                checkpoint_id=checkpoint_id,
                error=str(exc),
            )

        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
            }
        }

    def put_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        """Store intermediate writes (no-op: we only checkpoint full state)."""
        pass

    async def aget_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        return await asyncio.to_thread(self.get_tuple, config)

    async def alist(
        self,
        config: RunnableConfig | None,
        *,
        filter: dict[str, Any] | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[CheckpointTuple]:
        res = await asyncio.to_thread(self.list, config, filter=filter, before=before, limit=limit)
        for item in res:
            yield item

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict[str, Any],
    ) -> RunnableConfig:
        return await asyncio.to_thread(self.put, config, checkpoint, metadata, new_versions)

    async def aput_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        return await asyncio.to_thread(self.put_writes, config, writes, task_id, task_path)

