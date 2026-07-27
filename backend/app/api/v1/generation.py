"""
Generation API Router — v1
Endpoints:
  POST  /generate              — Start the video generation pipeline
  GET   /jobs/{job_id}         — Get job status
  GET   /jobs/{job_id}/stream  — SSE stream of live job progress
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import AsyncIterator

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.core.config import get_settings
from app.core.exceptions import NotFoundError, DatabaseError
from app.core.logging_config import get_logger
from app.core.auth import get_current_user
from app.database.repositories.job_repository import JobRepository
from app.database.repositories.project_repository import ProjectRepository
from app.database.repositories.video_repository import VideoRepository
from app.schemas.project import GenerationRequest, JobResponse, ProgressEvent
from app.graph.state import VideoGenerationState, create_initial_state

logger = get_logger(__name__)
router = APIRouter(tags=["Generation"])

settings = get_settings()


@router.post("/generate", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_generation(
    payload: GenerationRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
) -> JobResponse:
    """
    Start the video generation pipeline for a project.

    Returns the job ID immediately; use /jobs/{id} to poll status
    or /jobs/{id}/stream for live SSE updates.
    """
    user_id = user.get("uid", "local_dev_user") or "local_dev_user"
    project_repo = ProjectRepository()
    job_repo = JobRepository()

    # Verify project exists
    try:
        project = project_repo.get_by_id(payload.project_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.to_dict())
    except DatabaseError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=exc.to_dict())

    # Check if already running (unless force_regenerate)
    if not payload.force_regenerate and project.get("status") == "running":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A generation job is already running for this project. "
                   "Use force_regenerate=true to restart.",
        )

    # Create job document
    job_status = "queued" if settings.use_background_worker else "pending"
    job = job_repo.create(payload.project_id, user_id=user_id, status=job_status)
    job_id = job["id"]

    # Build initial graph state
    initial_state = create_initial_state(
        project_id=payload.project_id,
        job_id=job_id,
        input_type=project.get("input_type", "text"),
        input_text=project.get("input_text", ""),
        input_file_path=project.get("metadata", {}).get("local_path", ""),
        input_file_url=project.get("input_file_url", ""),
        render_quality=payload.quality,
        tts_engine=payload.tts_engine,
        tts_voice=payload.tts_voice,
        render_output_dir=str(settings.render_output_path),
        max_repair_retries=settings.max_repair_retries,
    )
    job_repo.update(job_id, {"initial_state": dict(initial_state)})

    # Launch graph in background task or leave queued for background worker
    if settings.use_background_worker:
        logger.info("Job queued for background worker", job_id=job_id, project_id=payload.project_id)
    else:
        logger.info("Running job in local background task", job_id=job_id, project_id=payload.project_id)
        job_repo.update(job_id, {"status": "running"})
        background_tasks.add_task(
            _run_generation_pipeline, job_id, payload.project_id, initial_state
        )

    return JobResponse(**job_repo.get_by_id(job_id))


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    user: dict = Depends(get_current_user),
) -> JobResponse:
    """Get the current status of a generation job."""
    try:
        job_repo = JobRepository()
        job = job_repo.get_by_id(job_id)
        return JobResponse(**job)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.to_dict())
    except DatabaseError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=exc.to_dict())


@router.get("/jobs/{job_id}/stream")
async def stream_job_progress(
    job_id: str,
    user: dict = Depends(get_current_user),
) -> StreamingResponse:
    """
    SSE stream of live job progress updates.
    Client should use EventSource API.
    """
    return StreamingResponse(
        _sse_generator(job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# Background task
# ─────────────────────────────────────────────────────────────────────────────

async def _run_generation_pipeline(
    job_id: str,
    project_id: str,
    initial_state: VideoGenerationState,
) -> None:
    """Background task: execute the LangGraph video generation pipeline."""
    from app.graph.builder import get_graph

    try:
        graph = get_graph()
        config = {
            "configurable": {
                "thread_id": initial_state.get("thread_id", job_id),
            }
        }

        # Stream graph execution
        from app.database.repositories.job_repository import JobRepository
        job_repo = JobRepository()
        async for event in graph.astream(initial_state, config=config):
            logger.debug("Graph event", event_keys=list(event.keys()))
            for node_name, node_output in event.items():
                if isinstance(node_output, dict):
                    stage = node_output.get("current_stage")
                    if stage:
                        try:
                            job_repo.update_stage(job_id, stage)
                        except Exception as exc:
                            logger.warning("Failed to update stage in background task", error=str(exc))
                    stage_logs = node_output.get("stage_logs")
                    if stage_logs and isinstance(stage_logs, list):
                        for log_entry in stage_logs:
                            try:
                                job_repo.append_log(job_id, log_entry)
                            except Exception as exc:
                                logger.warning("Failed to append log in background task", error=str(exc))

        logger.info("Pipeline completed", job_id=job_id)
    except Exception as exc:
        logger.exception("Pipeline background task failed", job_id=job_id, error=str(exc))
        # Mark job as failed in Firestore
        try:
            from app.database.repositories.job_repository import JobRepository
            job_repo = JobRepository()
            job_repo.mark_failed(job_id, str(exc), "background_task")
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# SSE generator
# ─────────────────────────────────────────────────────────────────────────────

async def _sse_generator(job_id: str) -> AsyncIterator[str]:
    """Yield SSE events by polling Firestore job status."""
    job_repo = JobRepository()
    last_stage = ""
    last_log_count = 0

    STAGE_PROGRESS = {
        "supervisor": 5,
        "ocr_agent": 15,
        "content_generation_agent": 30,
        "manim_script_agent": 50,
        "manim_execution_service": 70,
        "repair_agent": 75,
        "narration_agent": 85,
        "synchronization_service": 95,
        "finalize": 100,
        "done": 100,
        "error_handler": 100,
    }

    max_polls = 600  # Poll for up to 10 minutes (at 1s intervals)
    poll_count = 0

    while poll_count < max_polls:
        try:
            job = job_repo.get_by_id(job_id)
        except Exception:
            await asyncio.sleep(2)
            poll_count += 1
            continue

        job_status = job.get("status", "pending")
        current_stage = job.get("current_stage", "")
        logs = job.get("logs", [])

        progress = STAGE_PROGRESS.get(current_stage, 0)

        # Emit stage change event
        if current_stage != last_stage:
            event = ProgressEvent(
                event_type="stage_start",
                job_id=job_id,
                stage=current_stage,
                message=f"Started: {current_stage.replace('_', ' ').title()}",
                progress_percent=progress,
                timestamp=datetime.now(tz=timezone.utc).isoformat(),
            )
            yield event.to_sse()
            last_stage = current_stage

        # Emit new log entries
        if len(logs) > last_log_count:
            new_logs = logs[last_log_count:]
            for log_entry in new_logs:
                if isinstance(log_entry, dict):
                    event = ProgressEvent(
                        event_type="log",
                        job_id=job_id,
                        stage=log_entry.get("stage", current_stage),
                        message=log_entry.get("message", ""),
                        progress_percent=progress,
                        metadata=log_entry,
                        timestamp=datetime.now(tz=timezone.utc).isoformat(),
                    )
                    yield event.to_sse()
            last_log_count = len(logs)

        # Check terminal states
        if job_status in ("completed", "failed"):
            final_event = ProgressEvent(
                event_type="done" if job_status == "completed" else "error",
                job_id=job_id,
                stage=current_stage,
                message=f"Job {job_status}",
                progress_percent=100 if job_status == "completed" else progress,
                metadata={
                    "status": job_status,
                    "error": job.get("error_message", ""),
                },
                timestamp=datetime.now(tz=timezone.utc).isoformat(),
            )
            yield final_event.to_sse()
            break

        await asyncio.sleep(1)
        poll_count += 1

    # Final heartbeat to close connection
    yield "data: {\"event_type\": \"close\"}\n\n"
