"""
Render API Router — v1
Endpoints:
  POST /render  — Manually trigger a re-render for a project
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.exceptions import NotFoundError, DatabaseError
from app.core.logging_config import get_logger
from app.core.auth import get_current_user
from app.database.repositories.job_repository import JobRepository
from app.database.repositories.project_repository import ProjectRepository
from app.schemas.project import GenerationRequest, JobResponse
from app.schemas.state import create_initial_state

logger = get_logger(__name__)
router = APIRouter(tags=["Render"])
settings = get_settings()


class RenderRequest(BaseModel):
    """Request body for POST /render."""
    project_id: str
    quality: str = "low_quality"
    tts_engine: str = "edge-tts"
    tts_voice: str = "en-US-AriaNeural"
    start_from_stage: str = "manim_script_agent"


@router.post("/render", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_render(
    payload: RenderRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
) -> JobResponse:
    """
    Manually trigger a re-render starting from a specific pipeline stage.
    Useful for re-rendering after manual script edits.
    """
    user_id = user.get("uid", "local_dev_user") or "local_dev_user"
    project_repo = ProjectRepository()
    job_repo = JobRepository()

    # Verify project
    try:
        project = project_repo.get_by_id(payload.project_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.to_dict())
    except DatabaseError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.to_dict(),
        )

    # Create new job
    job = job_repo.create(payload.project_id, user_id=user_id)
    job_id = job["id"]

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

    from app.api.v1.generation import _run_generation_pipeline
    background_tasks.add_task(
        _run_generation_pipeline, job_id, payload.project_id, initial_state
    )

    logger.info(
        "Manual render triggered",
        job_id=job_id,
        project_id=payload.project_id,
        start_stage=payload.start_from_stage,
    )

    return JobResponse(**job)
