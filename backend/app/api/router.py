"""
API Router — mounts all v1 sub-routers under /api/v1
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.generation import router as generation_router
from app.api.v1.projects import router as projects_router
from app.api.v1.render import router as render_router
from app.api.v1.video import router as video_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(projects_router)
api_router.include_router(generation_router)
api_router.include_router(video_router)
api_router.include_router(render_router)
