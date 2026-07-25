"""
Projects API Router — v1
Endpoints:
  POST   /projects          — Create new project
  GET    /projects          — List all projects
  GET    /project/{id}      — Get project by ID
  DELETE /project/{id}      — Delete project
"""

from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.exceptions import NotFoundError, DatabaseError, InputError
from app.core.logging_config import get_logger
from app.database.repositories.project_repository import ProjectRepository
from app.database.repositories.job_repository import JobRepository
from app.database.repositories.video_repository import VideoRepository
from app.schemas.project import ProjectCreate, ProjectListResponse, ProjectResponse
from app.services.storage_service import StorageService
from app.utils.file_utils import ensure_dir
from pathlib import Path
import tempfile
import os

logger = get_logger(__name__)
router = APIRouter(prefix="/projects", tags=["Projects"])

settings = get_settings()


class ExplainRequest(BaseModel):
    topic: str


@router.post("/explain", status_code=status.HTTP_200_OK)
async def explain_topic(payload: ExplainRequest) -> dict:
    """Generate an interactive tutor explanation of a topic using Gemini."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_fast_model or settings.gemini_model)
        prompt = (
            f"You are EduVideo AI, an expert, encouraging, and highly intelligent math and science AI tutor. "
            f"The user wants to learn about:\n\n'{payload.topic}'\n\n"
            f"Provide a clear, engaging, structured explanation (around 150-200 words) using clean markdown formatting (bolding key concepts, using bullet points). "
            f"Explain the intuitive visual idea behind this concept. "
            f"End your response by stating that you are constructing a custom 3D animated video lesson to demonstrate this step-by-step right now!"
        )
        res = model.generate_content(prompt)
        return {"explanation": res.text}
    except Exception as exc:
        logger.warning("Gemini explain failed, using fallback explanation", error=str(exc))
        return {
            "explanation": (
                f"### Understanding **{payload.topic}**\n\n"
                f"This is a fundamental concept in mathematics and science that helps us model and visualize dynamic relationships. "
                f"By examining the underlying geometry and rate of change, complex ideas become intuitive and easy to grasp.\n\n"
                f"**Key Intuition:**\n"
                f"- **Visual Representation:** Translating abstract symbols into geometric transformations.\n"
                f"- **Step-by-Step Evolution:** Observing how components interact dynamically over time.\n\n"
                f"*I am constructing a rich 3D animated video lesson to demonstrate this step-by-step right now! Watch the terminal logs below as the scenes are rendered.*"
            )
        }


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate) -> ProjectResponse:
    """Create a new educational video project."""
    try:
        repo = ProjectRepository()
        doc = repo.create(
            {
                "title": payload.title,
                "description": payload.description,
                "input_type": payload.input_type.value,
                "input_text": payload.input_text,
                "metadata": payload.metadata,
            }
        )
        return ProjectResponse(**doc)
    except DatabaseError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.to_dict(),
        )


@router.post("/upload", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project_with_file(
    title: str = Form(...),
    description: str = Form(default=""),
    input_type: str = Form(...),
    file: UploadFile = File(...),
) -> ProjectResponse:
    """Create a project by uploading a PDF or image file."""
    # Validate file type
    allowed_types = {
        "application/pdf": "pdf",
        "image/jpeg": "image",
        "image/png": "image",
        "image/webp": "image",
        "image/gif": "image",
    }
    content_type = file.content_type or ""
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {content_type}. Allowed: PDF, JPEG, PNG, WebP, GIF",
        )

    # Save file locally first
    suffix = Path(file.filename or "upload").suffix or ".bin"
    tmp_dir = ensure_dir(str(settings.render_output_path / "uploads"))
    tmp_path = str(tmp_dir / f"upload_{os.getpid()}{suffix}")

    try:
        content = await file.read()
        with open(tmp_path, "wb") as f:
            f.write(content)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {exc}",
        )

    # Upload to Firebase Storage
    file_url = ""
    try:
        storage = StorageService()
        import uuid
        storage_path = f"uploads/{uuid.uuid4()}{suffix}"
        file_url = storage.upload_file(tmp_path, storage_path, content_type=content_type)
    except Exception as exc:
        logger.warning("Firebase upload failed, using local path", error=str(exc))
        file_url = tmp_path  # Fall back to local path

    # Create project
    try:
        repo = ProjectRepository()
        doc = repo.create(
            {
                "title": title,
                "description": description,
                "input_type": input_type,
                "input_file_url": file_url,
                "metadata": {
                    "original_filename": file.filename,
                    "file_size_bytes": len(content),
                    "content_type": content_type,
                    "local_path": tmp_path,
                },
            }
        )
        return ProjectResponse(**doc)
    except DatabaseError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.to_dict(),
        )


@router.get("", response_model=ProjectListResponse)
async def list_projects(limit: int = 20, offset: int = 0) -> ProjectListResponse:
    """List all projects, most recent first."""
    try:
        repo = ProjectRepository()
        items = repo.list_all(limit=limit, offset=offset)
        return ProjectListResponse(
            items=[ProjectResponse(**item) for item in items],
            total=len(items),
            limit=limit,
            offset=offset,
        )
    except DatabaseError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.to_dict(),
        )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str) -> ProjectResponse:
    """Get a project by ID."""
    try:
        repo = ProjectRepository()
        doc = repo.get_by_id(project_id)
        return ProjectResponse(**doc)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.to_dict())
    except DatabaseError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.to_dict(),
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response, response_model=None)
async def delete_project(project_id: str) -> None:
    """Delete a project and its associated jobs."""
    try:
        repo = ProjectRepository()
        repo.delete(project_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.to_dict())
    except DatabaseError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.to_dict(),
        )
