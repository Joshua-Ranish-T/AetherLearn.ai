"""
Video API Router — v1
Endpoints:
  GET /video/{id}  — Get video metadata and download URL
  GET /videos      — List all videos
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse

from app.core.exceptions import NotFoundError, DatabaseError
from app.core.logging_config import get_logger
from app.database.repositories.video_repository import VideoRepository
from app.schemas.project import VideoResponse

logger = get_logger(__name__)
router = APIRouter(tags=["Videos"])


@router.get("/videos", response_model=list[VideoResponse])
async def list_videos(limit: int = 20) -> list[VideoResponse]:
    """List all generated videos, most recent first."""
    try:
        repo = VideoRepository()
        items = repo.list_all(limit=limit)
        return [VideoResponse(**item) for item in items]
    except DatabaseError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.to_dict(),
        )


@router.get("/video/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str) -> VideoResponse:
    """Get video metadata and download URLs."""
    try:
        repo = VideoRepository()
        doc = repo.get_by_id(video_id)
        return VideoResponse(**doc)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.to_dict())
    except DatabaseError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.to_dict(),
        )


@router.get("/project/{project_id}/videos", response_model=list[VideoResponse])
async def get_project_videos(project_id: str) -> list[VideoResponse]:
    """Get all videos generated for a project."""
    try:
        repo = VideoRepository()
        items = repo.get_by_project(project_id)
        return [VideoResponse(**item) for item in items]
    except DatabaseError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.to_dict(),
        )


@router.get("/video/{video_id}/download")
async def download_video(video_id: str) -> RedirectResponse:
    """Redirect to the signed Firebase Storage download URL."""
    try:
        repo = VideoRepository()
        doc = repo.get_by_id(video_id)
        file_url = doc.get("file_url", "")
        if not file_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video file URL not available.",
            )
        return RedirectResponse(url=file_url)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.to_dict())
