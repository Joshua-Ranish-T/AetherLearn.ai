"""
LangGraph node wrappers.

Each function is a thin adapter that:
1. Calls the corresponding agent/service
2. Returns a state update dict
3. Handles errors by setting state error flags (never raising)

Nodes are imported by graph/builder.py which adds them to the StateGraph.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from app.core.logging_config import get_logger
from app.schemas.state import VideoGenerationState

logger = get_logger(__name__)


def _log_entry(stage: str, status: str, message: str, **metadata: Any) -> dict[str, Any]:
    return {
        "type": "log",
        "stage": stage,
        "status": status,
        "message": message,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        **metadata,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Supervisor Node
# ─────────────────────────────────────────────────────────────────────────────

def supervisor_node(state: VideoGenerationState) -> dict[str, Any]:
    """
    Entry point. Validates input and sets routing flags.
    Imported lazily to avoid circular imports.
    """
    from app.agents.supervisor_agent import SupervisorAgent

    logger.info("Supervisor node executing", project_id=state.get("project_id"))
    agent = SupervisorAgent()
    try:
        updates = agent.run(state)
        updates["stage_logs"] = [
            _log_entry("supervisor", "completed", "Supervisor: routing determined")
        ]
        return updates
    except Exception as exc:
        logger.exception("Supervisor node failed", error=str(exc))
        return {
            "has_error": True,
            "error_message": str(exc),
            "error_stage": "supervisor",
            "stage_logs": [_log_entry("supervisor", "error", str(exc))],
        }


# ─────────────────────────────────────────────────────────────────────────────
# OCR Agent Node
# ─────────────────────────────────────────────────────────────────────────────

def ocr_agent_node(state: VideoGenerationState) -> dict[str, Any]:
    """Runs OCR extraction on PDF/image inputs."""
    from app.agents.ocr_agent import OCRAgent

    logger.info("OCR agent node executing", project_id=state.get("project_id"))
    agent = OCRAgent()
    try:
        updates = agent.run(state)
        updates["ocr_completed"] = True
        updates["current_stage"] = "ocr_agent"
        updates["stage_logs"] = [
            _log_entry("ocr_agent", "completed", "Content extracted via OCR")
        ]
        return updates
    except Exception as exc:
        logger.exception("OCR agent node failed", error=str(exc))
        return {
            "has_error": True,
            "error_message": str(exc),
            "error_stage": "ocr_agent",
            "stage_logs": [_log_entry("ocr_agent", "error", str(exc))],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Content Generation Node
# ─────────────────────────────────────────────────────────────────────────────

def content_generation_node(state: VideoGenerationState) -> dict[str, Any]:
    """Generates lesson plan and storyboard using Gemini."""
    from app.agents.content_generation_agent import ContentGenerationAgent

    logger.info("Content generation node executing", project_id=state.get("project_id"))
    agent = ContentGenerationAgent()
    try:
        updates = agent.run(state)
        updates["content_generated"] = True
        updates["current_stage"] = "content_generation_agent"
        updates["stage_logs"] = [
            _log_entry(
                "content_generation_agent",
                "completed",
                f"Lesson plan created with {len(updates.get('lesson_plan', {}).storyboard if updates.get('lesson_plan') else [])} scenes",
            )
        ]
        return updates
    except Exception as exc:
        logger.exception("Content generation node failed", error=str(exc))
        return {
            "has_error": True,
            "error_message": str(exc),
            "error_stage": "content_generation_agent",
            "stage_logs": [_log_entry("content_generation_agent", "error", str(exc))],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Manim Script Generation Node
# ─────────────────────────────────────────────────────────────────────────────

def manim_script_node(state: VideoGenerationState) -> dict[str, Any]:
    """Generates executable Manim CE Python code from the storyboard."""
    from app.agents.manim_script_agent import ManimScriptAgent

    logger.info("Manim script generation node executing", project_id=state.get("project_id"))
    agent = ManimScriptAgent()
    try:
        updates = agent.run(state)
        updates["manim_script_generated"] = True
        updates["current_stage"] = "manim_script_agent"
        updates["stage_logs"] = [
            _log_entry("manim_script_agent", "completed", "Manim script generated")
        ]
        return updates
    except Exception as exc:
        logger.exception("Manim script node failed", error=str(exc))
        return {
            "has_error": True,
            "error_message": str(exc),
            "error_stage": "manim_script_agent",
            "stage_logs": [_log_entry("manim_script_agent", "error", str(exc))],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Manim Execution Service Node
# ─────────────────────────────────────────────────────────────────────────────

def manim_execution_node(state: VideoGenerationState) -> dict[str, Any]:
    """Executes Manim script as a subprocess."""
    from app.services.manim_execution_service import ManimExecutionService
    from app.schemas.manim import ExecutionStatus

    logger.info("Manim execution node executing", project_id=state.get("project_id"))
    service = ManimExecutionService()
    try:
        result = service.execute(state)
        success = result.status == ExecutionStatus.SUCCESS
        log_status = "completed" if success else "warning"
        log_msg = "Manim render succeeded" if success else f"Manim render failed: {result.error_message}"

        return {
            "execution_result": result,
            "execution_successful": success,
            "current_stage": "manim_execution_service",
            "stage_logs": [_log_entry("manim_execution_service", log_status, log_msg)],
        }
    except Exception as exc:
        logger.exception("Manim execution node failed", error=str(exc))
        return {
            "has_error": True,
            "error_message": str(exc),
            "error_stage": "manim_execution_service",
            "stage_logs": [_log_entry("manim_execution_service", "error", str(exc))],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Repair Agent Node
# ─────────────────────────────────────────────────────────────────────────────

def repair_agent_node(state: VideoGenerationState) -> dict[str, Any]:
    """Analyzes execution errors and patches Manim code."""
    from app.agents.repair_agent import RepairAgent

    logger.info(
        "Repair agent node executing",
        retry=state.get("repair_retry_count", 0),
        project_id=state.get("project_id"),
    )
    agent = RepairAgent()
    try:
        updates = agent.run(state)
        new_count = state.get("repair_retry_count", 0) + 1
        updates["repair_retry_count"] = new_count
        updates["current_stage"] = "repair_agent"
        updates["stage_logs"] = [
            _log_entry("repair_agent", "completed", f"Repair attempt #{new_count} applied")
        ]
        return updates
    except Exception as exc:
        logger.exception("Repair agent node failed", error=str(exc))
        return {
            "has_error": True,
            "error_message": str(exc),
            "error_stage": "repair_agent",
            "stage_logs": [_log_entry("repair_agent", "error", str(exc))],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Narration Agent Node
# ─────────────────────────────────────────────────────────────────────────────

def narration_agent_node(state: VideoGenerationState) -> dict[str, Any]:
    """Generates narration script and TTS audio files."""
    from app.agents.narration_agent import NarrationAgent

    logger.info("Narration agent node executing", project_id=state.get("project_id"))
    agent = NarrationAgent()
    try:
        updates = agent.run(state)
        updates["narration_completed"] = True
        updates["current_stage"] = "narration_agent"
        updates["stage_logs"] = [
            _log_entry("narration_agent", "completed", "Narration audio generated")
        ]
        return updates
    except Exception as exc:
        logger.exception("Narration agent node failed", error=str(exc))
        return {
            "has_error": True,
            "error_message": str(exc),
            "error_stage": "narration_agent",
            "stage_logs": [_log_entry("narration_agent", "error", str(exc))],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Synchronization Service Node
# ─────────────────────────────────────────────────────────────────────────────

def synchronization_node(state: VideoGenerationState) -> dict[str, Any]:
    """Merges rendered animation + narration → final MP4."""
    from app.services.synchronization_service import SynchronizationService

    logger.info("Synchronization node executing", project_id=state.get("project_id"))
    service = SynchronizationService()
    try:
        updates = service.synchronize(state)
        updates["synchronization_completed"] = True
        updates["current_stage"] = "synchronization_service"
        updates["stage_logs"] = [
            _log_entry(
                "synchronization_service",
                "completed",
                f"Final MP4 created: {updates.get('video_file_path', '')}",
            )
        ]
        return updates
    except Exception as exc:
        logger.exception("Synchronization node failed", error=str(exc))
        return {
            "has_error": True,
            "error_message": str(exc),
            "error_stage": "synchronization_service",
            "stage_logs": [_log_entry("synchronization_service", "error", str(exc))],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Finalization Node
# ─────────────────────────────────────────────────────────────────────────────

def finalize_node(state: VideoGenerationState) -> dict[str, Any]:
    """
    Uploads final assets to Firebase Storage, creates video document in Firestore,
    and updates project/job status.
    """
    from app.services.storage_service import StorageService
    from app.database.repositories.video_repository import VideoRepository
    from app.database.repositories.project_repository import ProjectRepository
    from app.database.repositories.job_repository import JobRepository
    import os, time

    logger.info("Finalize node executing", project_id=state.get("project_id"))

    try:
        storage_service = StorageService()
        video_repo = VideoRepository()
        project_repo = ProjectRepository()
        job_repo = JobRepository()

        project_id = state.get("project_id", "")
        job_id = state.get("job_id", "")
        lesson_plan = state.get("lesson_plan")

        uploaded_urls: dict[str, str] = {}

        # Upload video
        if state.get("video_file_path") and os.path.exists(state.get("video_file_path", "")):
            uploaded_urls["video_url"] = storage_service.upload_file(
                state["video_file_path"],
                f"projects/{project_id}/video.mp4",
                content_type="video/mp4",
            )

        # Upload audio
        if state.get("audio_file_path") and os.path.exists(state.get("audio_file_path", "")):
            uploaded_urls["audio_url"] = storage_service.upload_file(
                state["audio_file_path"],
                f"projects/{project_id}/narration.mp3",
                content_type="audio/mpeg",
            )

        # Upload transcript
        if state.get("transcript_file_path") and os.path.exists(state.get("transcript_file_path", "")):
            uploaded_urls["transcript_url"] = storage_service.upload_file(
                state["transcript_file_path"],
                f"projects/{project_id}/transcript.txt",
                content_type="text/plain",
            )

        # Upload Manim script
        if state.get("manim_script_file_path") and os.path.exists(state.get("manim_script_file_path", "")):
            uploaded_urls["manim_script_url"] = storage_service.upload_file(
                state["manim_script_file_path"],
                f"projects/{project_id}/manim_script.py",
                content_type="text/x-python",
            )

        # Create video document in Firestore
        video_doc = video_repo.create(
            {
                "project_id": project_id,
                "job_id": job_id,
                "title": lesson_plan.title if lesson_plan else "Generated Video",
                "duration_seconds": state.get("video_duration_seconds", 0.0),
                "file_url": uploaded_urls.get("video_url", ""),
                "audio_url": uploaded_urls.get("audio_url", ""),
                "transcript_url": uploaded_urls.get("transcript_url", ""),
                "manim_script_url": uploaded_urls.get("manim_script_url", ""),
                "storyboard_url": uploaded_urls.get("storyboard_url", ""),
                "metadata": {
                    "subject": lesson_plan.subject if lesson_plan else "",
                    "difficulty": lesson_plan.difficulty_level if lesson_plan else "",
                    "scene_count": len(lesson_plan.storyboard) if lesson_plan else 0,
                },
            }
        )

        # Update project status
        project_repo.update_status(project_id, "completed")

        # Update job
        import time as time_module
        # duration computed from state start
        job_repo.mark_completed(job_id, duration_seconds=0.0)

        return {
            "video_id": video_doc["id"],
            "video_url": uploaded_urls.get("video_url", ""),
            "audio_url": uploaded_urls.get("audio_url", ""),
            "transcript_url": uploaded_urls.get("transcript_url", ""),
            "manim_script_url": uploaded_urls.get("manim_script_url", ""),
            "current_stage": "finalize",
            "stage_logs": [
                _log_entry("finalize", "completed", f"Video {video_doc['id']} created and uploaded")
            ],
        }
    except Exception as exc:
        logger.exception("Finalize node failed", error=str(exc))
        return {
            "has_error": True,
            "error_message": str(exc),
            "error_stage": "finalize",
            "stage_logs": [_log_entry("finalize", "error", str(exc))],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Error Handler Node
# ─────────────────────────────────────────────────────────────────────────────

def error_handler_node(state: VideoGenerationState) -> dict[str, Any]:
    """Records the error in Firestore and terminates the graph gracefully."""
    from app.database.repositories.project_repository import ProjectRepository
    from app.database.repositories.job_repository import JobRepository

    error_stage = state.get("error_stage", "unknown")
    error_message = state.get("error_message", "Unknown error")

    logger.error(
        "Pipeline error handler invoked",
        stage=error_stage,
        error=error_message,
        project_id=state.get("project_id"),
    )

    try:
        job_repo = JobRepository()
        project_repo = ProjectRepository()
        job_id = state.get("job_id", "")
        project_id = state.get("project_id", "")

        if job_id:
            job_repo.mark_failed(job_id, error_message, error_stage)
        if project_id:
            project_repo.update_status(project_id, "failed")
    except Exception as db_exc:
        logger.warning("Failed to persist error state", error=str(db_exc))

    return {
        "current_stage": "error_handler",
        "stage_logs": [
            _log_entry("error_handler", "error", f"Pipeline failed at {error_stage}: {error_message}")
        ],
    }
